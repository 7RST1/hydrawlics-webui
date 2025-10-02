import numpy as np
import cv2
import pandas as pd
from polygonOutline import contours

font = cv2.FONT_HERSHEY_SIMPLEX

all_coords = []
polygon_id = 0

print("Number of contours:", len(contours))

for c in (contours): 
    print("Contour area:", cv2.contourArea(c))
      
    approx = cv2.approxPolyDP(c, 0.0005 * cv2.arcLength(c, True), True)

    coords = []

    for point in approx:
        y, x = point[0]
        coords.append((int(x), int(y)))

    print(f"Polygon {polygon_id} id: {coords}")

    for(x, y) in coords:
        all_coords.append((polygon_id, x, y))
    
    polygon_id += 1
    
coordinat_df = pd.DataFrame(all_coords, columns=['ID', 'X', 'Y'])
coordinat_df.to_csv('polygon_coordinates.csv', index=False)
print("Coordinates saved to polygon_coordinates.csv")

