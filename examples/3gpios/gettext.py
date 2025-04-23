# text_receive_example.py

from gpio_comm.gpio_comm import GpioReceiver  # Import der bereits definierten Klasse

# Beispiel: Text empfangen
pins = [17, 18, 27]
clock = 18      
receiver = GpioReceiver(pins, clock)

received_text = receiver.receive_text()  # Länge des Textes in Zeichen
print(f"Empfangener Text: {received_text}")

receiver.close()
