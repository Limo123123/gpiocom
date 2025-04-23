# number_receive_example.py

from gpio_sender_receiver import GpioReceiver  # Import der bereits definierten Klasse

# Beispiel: Zahl empfangen
pins = [17, 18, 27]
receiver = GpioReceiver(pins)

received_number = receiver.receive_number()
print(f"Empfangene Zahl: {received_number}")

receiver.close()
