import serial
from time import sleep

from serial.serialutil import SerialException

BAUD_RATE = 115200

ORANGE = '\033[38;5;208m'
RESET = '\033[0m'

# Sample G-code for drawing a smile (pen down when Z=0, pen up when Z>0)
SMILE_GCODE = """G0 Z1
G0 X30 Y50
G0 Z0
G1 X35 Y45
G1 X40 Y42
G1 X45 Y40
G1 X50 Y40
G1 X55 Y40
G1 X60 Y42
G1 X65 Y45
G1 X70 Y50
G0 Z1
G0 X45 Y60
G0 Z0
G1 X45 Y65
G0 Z1
G0 X55 Y60
G0 Z0
G1 X55 Y65
G0 Z1
"""

def checksum(string: str | bytes):
    csum = 0
    for c in string:
        csum ^= c
    return csum

class ArduinoInterface:
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyACM0', BAUD_RATE, dsrdtr=False, rtscts=False, timeout=2)

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

#con = ArduinoInterface()

#con.send_gcode(SMILE_GCODE)