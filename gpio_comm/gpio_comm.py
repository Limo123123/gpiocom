import time
import os
import lgpio

class GpioSender:
    def __init__(self, pins, gpio_chip=0):
        self.gpio_chip = gpio_chip  # GPIO-Chip-Nummer
        self.pins = pins
        self.validate_pins()
        self.handle = lgpio.gpiochip_open(self.gpio_chip)  # Öffne GPIO-Handle für Chip

    def validate_pins(self):
        """Stellt sicher, dass genügend Pins für die Kommunikation vorhanden sind."""
        if len(self.pins) < 3:  # Minimalanzahl von Pins für einfache Kommunikation
            raise ValueError("Mindestens 3 GPIO-Pins müssen angegeben werden.")
    
    def write_pin(self, pin, value):
        """Setzt den Wert eines bestimmten Pins (1 oder 0)."""
        lgpio.gpio_write(self.handle, pin, value)
    
    def send_text(self, text):
        """Sendet Textdaten als Binärdaten über GPIO."""
        binary_data = ''.join(format(ord(c), '08b') for c in text)  # Text zu Binär umwandeln
        self.send_binary(binary_data)
        
    def send_number(self, number):
        """Sendet eine Zahl als Binärdaten."""
        binary_data = format(number, '08b')  # Zahl zu Binär umwandeln
        self.send_binary(binary_data)
        
    def send_binary(self, binary_data):
        """Sendet Binärdaten über die GPIO-Pins."""
        for i, bit in enumerate(binary_data):
            self.write_pin(self.pins[i % len(self.pins)], 1 if bit == '1' else 0)
            time.sleep(0.1)  # Pause für Stabilität

    def send_file(self, file_path):
        """Sendet eine Datei in Paketen über die GPIO-Pins."""
        if not os.path.isfile(file_path):
            raise ValueError(f"Die Datei {file_path} existiert nicht.")
        
        total_size = os.path.getsize(file_path)
        with open(file_path, 'rb') as f:
            data = f.read()

        total_sent = 0
        for i in range(0, len(data), 64):  # Paketgröße 64 Bytes
            packet = data[i:i + 64]
            self.send_packet(packet)
            total_sent += len(packet)
            progress = (total_sent / total_size) * 100
            print(f"Fortschritt: {progress:.2f}%")
            time.sleep(0.1)
    
    def send_packet(self, packet):
        """Sendet ein Paket über GPIO-Pins."""
        for byte in packet:
            for bit in format(byte, '08b'):
                self.write_pin(self.pins[0], 1 if bit == '1' else 0)  # Nur ein Pin, zur Vereinfachung
            time.sleep(0.1)  # Pause für Stabilität

    def send_folder(self, folder_path):
        """Sendet alle Dateien in einem Ordner als Pakete über GPIO."""
        if not os.path.isdir(folder_path):
            raise ValueError(f"Der Ordner {folder_path} existiert nicht.")
        
        files = os.listdir(folder_path)
        for file_name in files:
            file_path = os.path.join(folder_path, file_name)
            self.send_file(file_path)
    
    def close(self):
        """Schließt den GPIO-Handle nach der Nutzung."""
        lgpio.gpiochip_close(self.handle)
        
class GpioReceiver:
    def __init__(self, pins, gpio_chip=0):
        self.gpio_chip = gpio_chip  # GPIO-Chip-Nummer
        self.pins = pins
        self.validate_pins()
        self.handle = lgpio.gpiochip_open(self.gpio_chip)  # Öffne GPIO-Handle für Chip

    def validate_pins(self):
        """Stellt sicher, dass genügend Pins für die Kommunikation vorhanden sind."""
        if len(self.pins) < 3:
            raise ValueError("Mindestens 3 GPIO-Pins müssen angegeben werden.")
    
    def read_pin(self, pin):
        """Liest den Wert eines bestimmten GPIO-Pins."""
        return lgpio.gpio_read(self.handle, pin)

    def receive_binary(self, length):
        """Empfängt Binärdaten über die GPIO-Pins."""
        binary_data = ''
        for _ in range(length):
            bit = self.read_pin(self.pins[0])  # Ein Pin wird hier zum Ablesen verwendet
            binary_data += str(bit)
            time.sleep(0.1)  # Warten, um das Signal korrekt zu empfangen
        return binary_data
    
    def receive_text(self, length):
        """Empfängt Textdaten über die GPIOs."""
        binary_data = self.receive_binary(length * 8)  # Text ist eine Folge von 8-Bit-Zeichen
        text = ''.join(chr(int(binary_data[i:i+8], 2)) for i in range(0, len(binary_data), 8))
        return text
    
    def receive_number(self):
        """Empfängt eine Zahl über die GPIOs."""
        binary_data = self.receive_binary(8)  # Eine Zahl ist 8 Bit
        return int(binary_data, 2)
    
    def receive_file(self, folder_path, file_name):
        """Empfängt eine Datei und speichert sie auf dem lokalen Dateisystem."""
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'wb') as f:
            while True:
                packet = self.receive_binary(64)  # Paketgröße von 64 Bytes
                if not packet:
                    break
                f.write(bytearray(int(packet[i:i+8], 2) for i in range(0, len(packet), 8)))
        print(f"Datei empfangen: {file_path}")
    
    def receive_folder(self, folder_path):
        """Empfängt alle Dateien eines Ordners."""
        while True:
            # Hier könnte eine Möglichkeit eingebaut werden, um die Ordnerstruktur zu empfangen
            pass
    
    def close(self):
        """Schließt den GPIO-Handle nach der Nutzung."""
        lgpio.gpiochip_close(self.handle)