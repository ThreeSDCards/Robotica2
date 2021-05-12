import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
import time

IS_PI = False
USE_GUI = False

#Start webcam
if IS_PI:
    vs = VideoStream(src=0, usePiCamera=True,
        resolution=(640,480), framerate=60).start()
else:
    vs = VideoStream(src=0).start()

def find_ball(frame, mask):
    # Find contours and point
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None

    # Only proceed if anything was found
    if len(cnts) > 0:
        try:
            #Find largest contour in the mask, then use it to find circle
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            return ((int(x),int(y)), radius)
        except Exception:
            return None
    else:
       return None

def nothing(x):
    pass

blue_min = (90, 155, 60)
blue_max = (160, 255, 255)

def main():
    while True:
        start_time = time.time()
        #640, 480
        image = vs.read()
        if image is None:
            continue
        orig = image.copy()
        
        #400, 400
        image = imutils.resize(image, height = 400, width = 400)
        
        hsv = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, blue_min, blue_max)
        # Found it lmao
        res = find_ball(image, mask)
        if res is None:
            cv2.imshow("Input feed", orig)
            continue
        else:
            (x,y), radius = res

        # Normalize that shit
        x_norm = x / image.shape[1]
        y_norm = y / image.shape[0]

        
        if USE_GUI:
        # Point to it
            cv2.putText(image, str(round(x_norm, 3))+","+str(round(y_norm, 3)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)

            cv2.imshow("Input feed", orig)
            cv2.imshow("Mask", mask)
            cv2.imshow("Result", image)

        # Keep track of FPS
        newtime = time.time()
        print("Delta: {}".format(  str(1/( newtime - start_time))))
        start_time = newtime

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    vs.stop()

    cv2.destroyAllWindows()

main()
