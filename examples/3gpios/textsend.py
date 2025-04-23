# text_send_example.py

from gpio_sender_receiver import GpioSender  # Import der bereits definierten Klasse

# Beispiel: Text senden
pins = [17, 18, 27]
sender = GpioSender(pins)

sender.send_text("Hallo, Welt!")  # Text senden

sender.close()
