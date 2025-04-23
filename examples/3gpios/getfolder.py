# folder_receive_example.py

from gpio_comm.gpio_comm import GpioReceiver  # Import der bereits definierten Klasse

# Beispiel: Ordner empfangen
pins = [17, 18, 27]
receiver = GpioReceiver(pins)

receiver.receive_folder("/path/to/receive/folder")  # Ordner empfangen

receiver.close()
