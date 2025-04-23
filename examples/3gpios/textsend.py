# text_send_example.py

from gpio_comm.gpio_comm import GpioSender  # Import der bereits definierten Klasse

# Beispiel: Text senden
pins = [17, 18, 27]
clock = 18  
sender = GpioSender(pins, clock)

sender.send_text("Hallo, Welt!")  # Text senden

sender.close()
