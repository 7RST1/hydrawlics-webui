import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv('polygon_coordinates.csv')

# Create a figure
plt.figure(figsize=(8, 6))

# Group by ID and plot each polygon without markers
for polygon_id, group in df.groupby('ID'):
    plt.plot(group['X'], group['Y'], linestyle='-', label=f'Polygon {polygon_id}', marker='')

# Add labels and legend
plt.title('Visualization of Polygon Coordinates')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.legend()
plt.grid(True)
plt.axis('equal')

# Show the plot
plt.show()

import matplotlib.pyplot as plt

x, y = [], []
cx, cy = 0.0, 0.0
cz = 1e6
z_cut = 0.0  # default; may be overwritten by generator comment

paths = []
current_path = []
cx = cy = 0.0
cz = 1e6
z_cut = 0.0

with open("output.gcode") as f:
    for raw in f:
        line = raw.strip()
        if not line:
            continue
        # detect generator comment with z_cut if available: "(z_safe=..., z_cut=...)"
        if line.startswith("(") and "z_cut=" in line:
            try:
                part = [p for p in line.strip("()").split(",") if "z_cut=" in p][0]
                z_cut = float(part.split("=")[1])
            except Exception:
                pass
            continue

        if not line.startswith(("G0", "G1")):
            continue

        parts = line.split()
        dx = dy = dz = None
        for part in parts:
            if part.startswith("X"):
                dx = float(part[1:])
            elif part.startswith("Y"):
                dy = float(part[1:])
            elif part.startswith("Z"):
                dz = float(part[1:])

        # update coordinates/Z state
        if dx is not None:
            cx = dx
        if dy is not None:
            cy = dy
        prev_cz = cz
        if dz is not None:
            cz = dz

        pen_down = (cz <= z_cut + 1e-6)

        # If we just plunged (went from pen-up to pen-down) ensure start vertex is recorded
        if (not (prev_cz <= z_cut + 1e-6)) and pen_down:
            # start a new path with current XY
            if current_path:
                paths.append(current_path)
            current_path = [(cx, cy)]

        # record XY movement while pen is down
        if dx is not None or dy is not None:
            if pen_down:
                current_path.append((cx, cy))
            else:
                # travel move while pen up -> close current drawing path if any
                if current_path:
                    paths.append(current_path)
                    current_path = []

# close last path if needed
if current_path:
    paths.append(current_path)

# plot each drawn path separately (so travels aren't connected)
plt.figure(figsize=(8, 6))
for p in paths:
    xs = [pt[0] for pt in p]
    ys = [pt[1] for pt in p]
    if xs and ys:
        plt.plot(xs, ys, linewidth=0.5)

plt.axis("equal")
# If your CSV coordinates are image pixels (Y downwards), uncomment:
plt.title("G-code visualization (only drawing moves shown)")
plt.show()
