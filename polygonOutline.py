import numpy as np
import cv2

def draw_polygon_outlines(img, contours):

    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    img_copy = img.copy()

    for cnt in contours:
        approx = cv2.approxPolyDP(cnt, 0.0005 * cv2.arcLength(cnt, True), True)
        cv2.drawContours(img_copy, [approx], 0, (255, 0, 255), 2)

    return img_copy

# result = draw_polygon_outlines(img, contours)
# cv2.imshow('Polygon Outlines', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

