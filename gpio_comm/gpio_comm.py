# gpio_comm.py

import time
import os
import struct
import lgpio

START_MARKER = 0x02
STOP_MARKER  = 0x03
CHUNK_SIZE   = 64  # Bytes pro Paket

class GpioSender:
    def __init__(self, data_pins, clock_pin, gpio_chip=0, delay=0.001):
        """
        data_pins: Liste von GPIO-Nummern (BCM), in paralleler Busbreite.
        clock_pin: GPIO-Nummer für Clock/Handshake.
        gpio_chip: Nummer des gpiochip (meist 0).
        delay:   Pause zwischen Clock-Flanken in Sekunden.
        """
        self.pins     = data_pins
        self.clk      = clock_pin
        self.bus_w    = len(self.pins)
        self.delay    = delay
        self.h        = lgpio.gpiochip_open(gpio_chip)
        # Pins claimen
        for p in self.pins:
            lgpio.gpio_claim_output(self.h, p)
        lgpio.gpio_claim_output(self.h, self.clk)

    def _write_group(self, bits):
        # bits: Liste von 0/1 der Länge bus_w
        for pin, bit in zip(self.pins, bits):
            lgpio.gpio_write(self.h, pin, bit)
        # Clock-Flanke
        lgpio.gpio_write(self.h, self.clk, 1)
        time.sleep(self.delay)
        lgpio.gpio_write(self.h, self.clk, 0)
        time.sleep(self.delay)

    def _send_frame(self, payload_bytes):
        # 1) START
        self._send_raw_byte(START_MARKER)
        # 2) Payload
        for b in payload_bytes:
            self._send_raw_byte(b)
        # 3) Checksumme
        checksum = sum(payload_bytes) & 0xFF
        self._send_raw_byte(checksum)
        # 4) STOP
        self._send_raw_byte(STOP_MARKER)

    def _send_raw_byte(self, byte):
        # Byte in Gruppen zu bus_w Bits aufteilen
        bits = [(byte >> i) & 1 for i in range(8)]
        # Senden in Gruppen
        for i in range(0, 8, self.bus_w):
            grp = bits[i:i+self.bus_w]
            # Padd mit 0, falls grp < bus_w
            grp += [0] * (self.bus_w - len(grp))
            self._write_group(grp)

    def send_text(self, text):
        self._send_frame(text.encode('utf-8'))

    def send_number(self, number):
        # 4-Byte Big-Endian
        num_bytes = number.to_bytes(4, 'big', signed=False)
        self._send_frame(num_bytes)

    def send_file(self, file_path):
        name = os.path.basename(file_path).encode('utf-8')
        size = os.path.getsize(file_path)
        # Header: Dateiname und Dateigröße
        header = struct.pack('>H', len(name)) + name + struct.pack('>I', size)
        self._send_frame(header)
        # Daten in CHUNK_SIZE-Paketen
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                self._send_frame(chunk)

    def send_folder(self, folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path,f))]
        # Erst Header mit Anzahl Dateien
        header = struct.pack('>H', len(files))
        self._send_frame(header)
        # Dann jede Datei
        for fn in files:
            self.send_file(os.path.join(folder_path, fn))

    def close(self):
        lgpio.gpiochip_close(self.h)


class GpioReceiver:
    def __init__(self, data_pins, clock_pin, gpio_chip=0, delay=0.001):
        self.pins  = data_pins
        self.clk   = clock_pin
        self.bus_w = len(self.pins)
        self.delay = delay
        self.h     = lgpio.gpiochip_open(gpio_chip)
        # Pins claimen
        for p in self.pins:
            lgpio.gpio_claim_input(self.h, p)
        lgpio.gpio_claim_input(self.h, self.clk)

    def _read_group(self):
        # Warten auf Clock-Flanke 0→1
        while lgpio.gpio_read(self.h, self.clk) == 0: pass
        # Daten lesen
        bits = [lgpio.gpio_read(self.h, p) for p in self.pins]
        # Warten auf Flanke 1→0
        while lgpio.gpio_read(self.h, self.clk) == 1: pass
        time.sleep(self.delay)
        return bits

    def _receive_frame(self):
        # Byte-Stream rekonstruieren
        buf_bits = []
        payload = []
        # 1) START abwarten
        while True:
            bits = self._read_group()
            buf_bits += bits
            if len(buf_bits) >= 8:
                byte = 0
                for i in range(8):
                    byte |= (buf_bits[i] << i)
                buf_bits = buf_bits[8:]
                if byte == START_MARKER:
                    break
        # 2) Payload bis STOP
        while True:
            # Nächstes Byte
            while len(buf_bits) < 8:
                buf_bits += self._read_group()
            byte = 0
            for i in range(8):
                byte |= (buf_bits[i] << i)
            buf_bits = buf_bits[8:]
            if byte == STOP_MARKER:
                break
            payload.append(byte)
        # 3) Trenne Checksumme
        if len(payload) < 1:
            raise RuntimeError("Frame ohne Payload")
        recv_checksum = payload[-1]
        data = payload[:-1]
        calc_checksum = sum(data) & 0xFF
        if recv_checksum != calc_checksum:
            raise RuntimeError(f"Checksum error: got {recv_checksum}, calc {calc_checksum}")
        return bytes(data)

    def receive_text(self) -> str:
        data = self._receive_frame()
        return data.decode('utf-8', errors='replace')

    def receive_number(self) -> int:
        data = self._receive_frame()
        if len(data) != 4:
            raise RuntimeError(f"Invalid number length: {len(data)}")
        return int.from_bytes(data, 'big', signed=False)

    def receive_file(self, out_folder):
        # Header empfangen
        hdr = self._receive_frame()
        # Header: 2-Byte Name-Länge, Name, 4-Byte Size
        name_len = struct.unpack('>H', hdr[:2])[0]
        name     = hdr[2:2+name_len].decode('utf-8')
        size     = struct.unpack('>I', hdr[2+name_len:6+name_len])[0]
        # Datei anlegen
        path = os.path.join(out_folder, name)
        with open(path, 'wb') as f:
            received = 0
            while received < size:
                chunk = self._receive_frame()
                f.write(chunk)
                received += len(chunk)
        return path

    def receive_folder(self, out_folder):
        # Header: Anzahl Dateien (2-Byte)
        hdr = self._receive_frame()
        count = struct.unpack('>H', hdr)[0]
        paths = []
        for _ in range(count):
            p = self.receive_file(out_folder)
            paths.append(p)
        return paths

    def close(self):
        lgpio.gpiochip_close(self.h)
