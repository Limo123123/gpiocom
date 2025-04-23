# text_receive_example.py

from gpio_comm.gpio_comm import GpioReceiver  # Import der bereits definierten Klasse

# Beispiel: Text empfangen
pins = [17, 18, 27]
receiver = GpioReceiver(pins)

received_text = receiver.receive_text(12)  # Länge des Textes in Zeichen
print(f"Empfangener Text: {received_text}")

receiver.close()
