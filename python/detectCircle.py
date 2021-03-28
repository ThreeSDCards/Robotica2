import cv2
import numpy as np
import matplotlib.pyplot as plt

image = np.uint8( cv2.imread("media/drawn_circle.png"))
img = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

plt.imshow(img, cmap = 'gray', interpolation = 'bicubic')
plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
plt.show()
circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, 1.3, 100)
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    print(circles)
    for (x, y, r) in circles:
        cv2.circle(image, (x,y), r, (0, 255, 0), 2)

cv2.waitKey()