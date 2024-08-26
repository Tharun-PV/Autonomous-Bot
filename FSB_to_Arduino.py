import serial
import time

# Define the serial port and baud rate
ser = serial.Serial('/dev/ttyACM0', 9600)  # Change '/dev/ttyACM0' to match the port where your Arduino is connected

# Wait for the serial connection to be established
time.sleep(2)

while True:
    # Read input from terminal
    user_input = input("Enter command (F/B/S): ")

    # Send input to Arduino
    ser.write(user_input.encode())

    # Wait for a short time to ensure Arduino receives the data
    time.sleep(0.1)

