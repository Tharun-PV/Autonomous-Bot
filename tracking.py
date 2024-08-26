import requests
import serial
import time
import RPi.GPIO as GPIO
import pyttsx3
# Initialize pyttsx3 TTS engine
engine = pyttsx3.init()
# Define the GPIO pins for IR sensors
left_ir_sensor_pin = 24
right_ir_sensor_pin = 23
# Setup GPIO mode and pins
GPIO.setmode(GPIO.BCM)
GPIO.setup(left_ir_sensor_pin, GPIO.IN)
GPIO.setup(right_ir_sensor_pin, GPIO.IN)
def send_command_to_serial(command):
    try:
        ser = serial.Serial('/dev/ttyACM0', 9600)
        time.sleep(2)
        ser.write(command.encode())
        ser.close()
        print(f"Sent command to serial: {command}")
    except serial.SerialException as e:
        print(f"Error opening or writing to serial port: {e}")
        # Speak "Motor Issue" using pyttsx3
        engine.say("Motor Issue")
        engine.runAndWait()
    except Exception as e:
        print(f"Error: {e}")
def ir_sensor_status():
    # Read the status of IR sensors
    left_ir_status = GPIO.input(left_ir_sensor_pin)
    right_ir_status = GPIO.input(right_ir_sensor_pin)
    # If either sensor is detected, return True; otherwise, return False
    if left_ir_status == GPIO.LOW or right_ir_status == GPIO.LOW:
        return True
    else:
        return False
def get_distance():
    try:
        response = requests.get('http://192.168.232.3:5000/distance')
        data = response.json()
        distance = data.get('distance', 'null')
        return distance
    except requests.RequestException as e:
        print(f"Error making GET request: {e}")
        # Speak "Camera or Server Issue" using pyttsx3
        engine.say("Camera or Server Issue")
        engine.runAndWait()
        return 'null'
def main():
    while True:
        # Check IR sensor status
        ir_detected = ir_sensor_status()
        if ir_detected:
            # If IR sensor is detected, send command 'S'
            send_command_to_serial('S')
            # Speak "Please Move aside" using pyttsx3
            engine.say("Please Move aside")
            engine.runAndWait()
        else:
            # If IR sensor is not detected, get distance from server
            distance = get_distance()
            if distance is not None:
                if distance == 'null':
                    command = 'S'
                elif distance > 50:
                    command = 'B'
                elif distance < 30:
                    command = 'F'
                else:
                    command = 'S'
                send_command_to_serial(command)
        time.sleep(0.5)
if __name__ == "__main__":
    main()
