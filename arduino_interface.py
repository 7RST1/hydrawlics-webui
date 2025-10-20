import serial
from time import sleep
import glob
import argparse

from serial.serialutil import SerialException

BAUD_RATE = 115200

ORANGE = '\033[38;5;208m'
RESET = '\033[0m'

def checksum(string: str | bytes):
    csum = 0
    for c in string:
        csum ^= c
    return csum

def find_gcode_file():
    gcode_files = glob.glob("*.gcode")

    if not gcode_files:
        print("No G-code files found in current directory.")
        exit()

    return gcode_files

class ArduinoInterface:
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = BAUD_RATE, timeout: float = 2):
        self.ser = serial.Serial(port, baudrate, dsrdtr=False, rtscts=False, timeout=timeout)

        sleep(2)

        line = self.ser.readline()
        linestr = line.decode('utf-8')
        is_connected = linestr.strip() == "Connected"

        print("Arduino connected" if is_connected else "Arduino was not connected")
        if not is_connected:
            raise SerialException("Arduino not connected")

    def send_gcode(self, gcode: str):
        # we should opt for minimal transfer to the arduino. max gcode command lines is about 300,
        # so we should consider a buffer of 128 or something like that. If the arduino sends ACK when
        # some lines have been processed, we can send 64 new ones or something.
        gcode_trimmed = gcode.strip()
        gcode_bytes = gcode_trimmed.encode('utf-8')

        if len(gcode_bytes) > 4000:
            print(ORANGE + "Warning: " + RESET + "G-code is approaching arduino memory limit!", str(len(gcode_bytes)) + "/8192 (but realistically lower than that)")
            print("\tReduce length if you encounter checksum mismatch")
        local_checksum = checksum(gcode_bytes)
        print(f"Sending {len(gcode_bytes)} bytes")
        print(f"First 50 bytes: {gcode_bytes[:50]}")
        print(f"Local checksum: {local_checksum}")

        self.ser.write(gcode_bytes + b'\0')  # Add null terminator for readStringUntil('\0')
        self.ser.flush()

        sleep(0.5)

        # Read until we get the OK response
        rec_checksum = -1
        while True:
            line = self.ser.readline()
            if not line:
                break
            print(f"Received: {line}")
            if line.decode('utf-8').strip().startswith("OK"):
                break
        linestr = line.decode('utf-8').strip()
        parts = linestr.split(" ")
        if len(parts) > 1:
            try:
                rec_checksum = int(parts[-1])
            except ValueError:
                rec_checksum = -1
        else:
            rec_checksum = -1
        print(str(local_checksum) + " == " + str(rec_checksum), end=": ")
        if rec_checksum != local_checksum:
            print("Checksum mismatch!")
        else:
            print("Checksum OK")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send G-code files to Arduino over serial")
    parser.add_argument("--port", type=str, default="/dev/ttyACM0",
                        help="Serial port to connect to (e.g., /dev/ttyACM0 or COM3)")
    parser.add_argument("--gcode_file", type=str, default=find_gcode_file()[0],
                        help="Path to the G-code file to send")
    args = parser.parse_args()

    try:
        arduino = ArduinoInterface(port=args.port)

        with open(args.gcode_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith(';')]

        for line in lines:
            arduino.send_gcode(line)
            sleep(0.1)  # Small delay between commands to avoid overwhelming the Arduino

        print("G-code file sent successfully.")
    
    except SerialException as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"G-code file '{args.gcode_file}' not found.")

#con = ArduinoInterface()

#con.send_gcode(SMILE_GCODE)