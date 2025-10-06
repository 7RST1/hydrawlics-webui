import sys
import math
from pathlib import Path

# Add parent directory to path to import arduino-interface module
sys.path.insert(0, str(Path(__file__).parent.parent))

from arduino_interface import ArduinoInterface


def generate_large_gcode(num_commands=1000):
    """Generate a large G-code by drawing a spiral pattern"""
    gcode_lines = ["G0 Z1"]  # Pen up

    for i in range(num_commands):
        angle = i * 0.1
        radius = i * 0.05
        x = 50 + radius * math.cos(angle)
        y = 50 + radius * math.sin(angle)

        if i == 0:
            gcode_lines.append(f"G0 X{x:.2f} Y{y:.2f}")
            gcode_lines.append("G0 Z0")  # Pen down
        else:
            gcode_lines.append(f"G1 X{x:.2f} Y{y:.2f}")

    gcode_lines.append("G0 Z1")  # Pen up
    return "\n".join(gcode_lines)


def test_large_gcode():
    """Test how Arduino handles very large G-code strings"""
    large_gcode = generate_large_gcode(300)  # Start smaller to fit in buffer
    print(f"Generated G-code with {len(large_gcode)} bytes, {len(large_gcode.splitlines())} lines")

    con = ArduinoInterface()
    con.send_gcode(large_gcode)
    print("Large G-code sent successfully!")


if __name__ == "__main__":
    test_large_gcode()
    # test_large_gcode_chunked()
