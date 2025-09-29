import cv2
import numpy as np
from CannyEdge import Canny_detector, img


edges = Canny_detector(img)
cv2.waitKey(0)
edges = edges.astype(np.uint8)

contours, hierarchy = cv2.findContours(edges,
                      cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

cv2.waitKey(0)
cv2.destroyAllWindows()

#print("Number of Contours Found = " + str(len(contours)))

img_with_contours = img.copy()

cv2.drawContours(img_with_contours, contours, -1, (0, 255, 0), 2)
cv2.imshow('Contours', img_with_contours)
cv2.waitKey(0)
cv2.destroyAllWindows()

