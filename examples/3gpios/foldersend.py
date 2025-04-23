# folder_send_example.py

from gpio_comm.gpio_comm import GpioSender  # Import der bereits definierten Klasse

# Beispiel: Ordner senden
pins = [17, 18, 27]
sender = GpioSender(pins)

sender.send_folder("/path/to/your/folder")  # Ordner senden

sender.close()
