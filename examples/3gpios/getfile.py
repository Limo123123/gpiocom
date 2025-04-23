# file_receive_example.py

from gpio_comm.gpio_comm import GpioReceiver  # Import der bereits definierten Klasse

# Beispiel: Datei empfangen
pins = [17, 18, 27]
receiver = GpioReceiver(pins)

receiver.receive_file("./", "received_file.txt")  # Datei empfangen

receiver.close()
