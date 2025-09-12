import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

image_path = 'C:\\Users\\emory\\Pictures\\Smarte systemer\\cat.jpg'

img = cv2.imread(image_path)

img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def Canny_detector(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gx = cv2.Sobel(np.float32(img), cv2.CV_64F, 1, 0, 3)
    gy = cv2.Sobel(np.float32(img), cv2.CV_64F, 0, 1, 3)
    mag, ang = cv2.cartToPolar(gx, gy, angleInDegrees=True)

    weak_th = None
    strong_th = None    
    height, width = img.shape

    mag_max = np.max(mag)
    if weak_th is None:
        weak_th = mag_max * 0.1
    if strong_th is None: strong_th = mag_max * 0.5

    for i_x in range(width):
        for i_y in range(height):
            grad_ang = ang[i_y, i_x]
            grad_ang = abs(
                grad_ang - 180) if abs(grad_ang) > 180 else abs(grad_ang)

            if grad_ang <= 22.5:
                neighb_1_x, neighb_1_y = i_x - 1, i_y
                neighb_2_x, neighb_2_y = i_x + 1, i_y
            elif grad_ang > 22.5 and grad_ang <= 67.5:
                neighb_1_x, neighb_1_y = i_x - 1, i_y - 1
                neighb_2_x, neighb_2_y = i_x + 1, i_y + 1
            elif grad_ang > 67.5 and grad_ang <= 112.5:
                neighb_1_x, neighb_1_y = i_x, i_y - 1
                neighb_2_x, neighb_2_y = i_x, i_y + 1
            elif grad_ang > 112.5 and grad_ang <= 157.5:
                neighb_1_x, neighb_1_y = i_x - 1, i_y + 1
                neighb_2_x, neighb_2_y = i_x + 1, i_y - 1
            else:
                neighb_1_x, neighb_1_y = i_x - 1, i_y
                neighb_2_x, neighb_2_y = i_x + 1, i_y

            if 0 <= neighb_1_x < width and 0 <= neighb_1_y < height:
                if mag[i_y, i_x] < mag[neighb_1_y, neighb_1_x]:
                    mag[i_y, i_x] = 0
                    continue

            if 0 <= neighb_2_x < width and 0 <= neighb_2_y < height:
                if mag[i_y, i_x] < mag[neighb_2_y, neighb_2_x]:
                    mag[i_y, i_x] = 0

    ids = np.zeros_like(img)
    for i_x in range(width):
        for i_y in range(height):
            grad_mag = mag[i_y, i_x]
            if grad_mag < weak_th:
                mag[i_y, i_x] = 0
            elif strong_th > grad_mag >= weak_th:
                ids[i_y, i_x] = 1
            else:
                ids[i_y, i_x] = 2
    return mag
"""
frame = cv2.imread('C:\\Users\\emory\\Pictures\\Smarte systemer\\cat.jpg')
if frame is None:
    print("Could not read the image.")

canny_img = Canny_detector(frame)

plt.subplot(1, 2, 1)
plt.title('Original Image')
plt.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
plt.axis('off')
plt.subplot(1, 2, 2)
plt.title('Canny Edges')
plt.imshow(canny_img, cmap='gray')
plt.axis('off')
plt.tight_layout()
plt.show(block=True)
plt.show()
"""