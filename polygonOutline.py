import numpy as np
import cv2
from ContourDetection import contours
from CannyEdge import img

if len(img.shape) == 2:
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

img_copy = img.copy()

for cnt in contours:
    area = cv2.contourArea(cnt)
    approx = cv2.approxPolyDP(cnt, 0.0005 * cv2.arcLength(cnt, True), True)
    cv2.drawContours(img_copy, [approx], 0, (0, 0, 255), 2)

cv2.imshow('Polygon Outlines', img_copy)
cv2.waitKey(0)
cv2.destroyAllWindows()

