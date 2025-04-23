# file_send_example.py

from gpio_comm.gpio_comm import GpioSender  # Import der bereits definierten Klasse

# Beispiel: Datei senden
pins = [17, 18, 27]
sender = GpioSender(pins)

sender.send_file("./file.txt")  # Datei senden

sender.close()
