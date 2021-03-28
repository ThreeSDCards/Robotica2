import cv2
import numpy as np
from imutils.video import VideoStream

#Start webcam
vs = VideoStream(src=0).start()

while True:
    frame = vs.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, 1, 1, 11, 2)

    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_area = 0
    c = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 1000:
            if area > max_area:
                max_area = area
                best_cnt = i
                image = cv2.drawContours(frame, contours, c, (0, 255, 0))
                c+=1
    
    approx = cv2.approxPolyDP(best_cnt, 0.009 * cv2.arcLength(best_cnt, True), True)
    cv2.drawContours(image, [approx], 0, (0, 255, 0), 5) 

    n = approx.ravel()
    i = 0
    for j in n:
        if i % 2 == 0:
            x = n[i]
            y = n[i+1]

            string = str(x) + " " + str(y)
            cv2.putText(image, string, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0))
        i+=1

    cv2.imshow("Input feed", frame)
    cv2.imshow("Image?", image) 
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break

vs.stop()

cv2.destroyAllWindows()
