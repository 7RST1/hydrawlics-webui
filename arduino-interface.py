import serial
from time import sleep

BAUD_RATE = 115200

# Sample G-code for drawing a smile (pen down when Z=0, pen up when Z>0)
SMILE_GCODE = """
G0 Z1
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

ser = serial.Serial('/dev/ttyACM0', BAUD_RATE, dsrdtr=False, rtscts=False)

ser.write(b'Yoooooooo')

ser.flush()

line = ser.readline()

linestr = line.decode('utf-8')
is_connected = linestr.strip() == "Connected"

print(linestr, is_connected)

if is_connected:
    #send gcode
    sleep(1)
    print("Sending G-code...")
    ser.write(SMILE_GCODE.encode('utf-8'))
    ser.flush()
    print("Done!")
    sleep(1)
    line = ser.readline()
    linestr = line.decode('utf-8')
    print("checksum: ", linestr)
    print("local checksum: ", checksum(SMILE_GCODE.encode('utf-8')))
