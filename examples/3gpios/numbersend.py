# number_send_example.py

from gpio_comm.gpio_comm import GpioSender  # Import der bereits definierten Klasse

# Beispiel: Zahl senden
pins = [17, 18, 27]
sender = GpioSender(pins)

sender.send_number(42)  # Zahl senden

sender.close()
