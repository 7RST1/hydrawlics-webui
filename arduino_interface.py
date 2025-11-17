import serial
from time import sleep
import glob
import argparse
import time

from serial.serialutil import SerialException
from serial.tools import list_ports as serial_list_ports

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

def detect_serial_port():
    """Return first detected serial port (Windows COMx or Unix tty), or None."""
    ports = [p.device for p in serial_list_ports.comports()]
    return ports[0] if ports else None

class ArduinoInterface:
    def __init__(self, port: str = '/dev/ttyACM0', baudrate: int = BAUD_RATE, timeout: float = 2):
        self.timeout = timeout
        self.ser = serial.Serial(port, baudrate, dsrdtr=False, rtscts=False, timeout=timeout)

        sleep(2)

        # Read until we get any non-empty response or timeout
        deadline = time.time() + timeout
        received = None
        while time.time() < deadline:
            line = self.ser.readline()
            if not line:
                continue
            try:
                received = line.decode('utf-8', errors='ignore').strip()
            except Exception:
                received = str(line).strip()
            break

        if received:
            print(f"Initial device response: {received}")
            is_connected = True  # accept any non-empty initial response
        else:
            print("No initial response from device within timeout.")
            is_connected = False

        print("Arduino connected" if is_connected else "Arduino was not connected")
        if not is_connected:
            raise SerialException("Arduino not connected")

    def wait_for_ready(self, timeout: float = 1) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.ser.readline()
            if not line:
                continue
            try:
                s = line.decode('utf-8', errors='ignore').strip()
            except Exception:
                s = str(line).strip()
            print(f"Received: {s}")
            # accepts 'ready' or 'ok' (case-insensitive)
            lowered = s.lower()
            if 'ready' in lowered or lowered == 'ok' in lowered:
                return True
        return False

    def send_gcode(self, gcode: str) -> bool:
        # Ensure device signals ready/ok before sending each line
        if not self.wait_for_ready(timeout=120):
            print("Arduino not ready to receive G-code.")
            return False

        gcode_trimmed = gcode.strip()
        # compute checksum on the line itself (no trailing newline),
        # then send the line with a newline appended
        gcode_trimmed_bytes = gcode_trimmed.encode('utf-8')
        gcode_bytes = gcode_trimmed_bytes + b'\n'

        if len(gcode_bytes) > 4000:
            print(ORANGE + "Warning: " + RESET + "G-code is approaching arduino memory limit!", str(len(gcode_bytes)) + "/8192 (but realistically lower than that)")
            print("\tReduce length if you encounter checksum mismatch")

        local_checksum = checksum(gcode_trimmed_bytes)
        print(f"Sending {len(gcode_bytes)} bytes, checksum {local_checksum}:")
        self.ser.write(gcode_bytes)
        self.ser.flush()

        # Wait for responses until we get an OK with checksum OR timeout.
        rec_checksum = -1
        deadline = time.time() + 10  # adjust timeout as needed
        while time.time() < deadline:
            line = self.ser.readline()
            if not line:
                # no data yet, keep waiting until deadline
                continue
            decoded = line.decode('utf-8', errors='ignore').strip()
            print(f"Received: {decoded}")

            lowered = decoded.lower()
            # If device signals general readiness, keep waiting for the OK line
            if 'ready' in lowered or lowered == 'ok' or 'start' in lowered:
                parts = decoded.split()
                if parts[0].upper().startswith("OK") and len(parts) > 1:
                    try:
                        rec_checksum = int(parts[-1])
                    except ValueError:
                        rec_checksum = -1
                    break
                # otherwise, it's a readiness ping; continue reading until explicit OK with checksum
                continue

            if decoded.upper().startswith("OK"):
                parts = decoded.split()
                try:
                    rec_checksum = int(parts[-1])
                except ValueError:
                    rec_checksum = -1
                break

        if rec_checksum == -1:
            print("No OK+checksum received from Arduino before timeout.")
        print(str(local_checksum) + " == " + str(rec_checksum), end=": ")
        if rec_checksum != local_checksum:
            print("Checksum mismatch!")
        else:
            print("Checksum OK")
        return rec_checksum == local_checksum
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send G-code files to Arduino over serial")
    parser.add_argument("--port", type=str, default=None,
                        help="Serial port to connect to (e.g., /dev/ttyACM0 or COM3)")
    parser.add_argument("--gcode_file", type=str, default=find_gcode_file()[0],
                        help="Path to the G-code file to send")
    args = parser.parse_args()

    # Auto-detect port if not provided
    port_to_use = args.port or detect_serial_port()
    if port_to_use is None:
        print("No serial ports found. Specify --port COMx or connect device and try again.")
        exit(1)
    print(f"Using serial port: {port_to_use}")

    try:
        arduino = ArduinoInterface(port=port_to_use)

        with open(args.gcode_file, 'r') as f:
            lines = []
            for raw in f:
                s = raw.strip()
                if not s:
                    continue
                if s.startswith(';'):
                    continue
                lines.append(s)

        all_ok = True
        for line in lines:
            ok = arduino.send_gcode(line)
            if not ok:
                print("Failed to send G-code line:", line)
                all_ok = False
                break
            sleep(0.1)  # Small delay between commands to avoid overwhelming the Arduino

        if all_ok:
            print("G-code file sent successfully.")
        else:
            print("G-code file transfer aborted.")
    
    except SerialException as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print(f"G-code file '{args.gcode_file}' not found.")
