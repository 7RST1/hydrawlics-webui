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

