import serial
import time

try:
    arduino_uno = serial.Serial('COM4', 9600, timeout=2)
    time.sleep(2)

    print("Connected to Arduino on COM4")

    while True:
        found_x = arduino_uno.readline().decode('utf-8').strip()

        if found_x == "x":
            print("hi")
            break

except serial.SerialException as e:
    print(f"Serial connection error: {e}")

except KeyboardInterrupt:
    print("Program stopped.")

finally:
    if 'arduino_uno' in locals() and arduino_uno.is_open:
        arduino_uno.close()