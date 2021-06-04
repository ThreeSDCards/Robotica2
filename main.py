import cv2
import numpy as np
import picamera
from picamera.array import PiRGBArray
import imutils
import time
import DBManager
import serial
from manager import Manager

USE_GUI = False

class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y

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

blue_min = (0, 62, 219)
blue_max = (65, 255, 255)


cam = picamera.PiCamera(0)
cam.resolution = (416, 416)
#cam.framerate = 40
cam.awb_mode = 'fluorescent'
rawCapture = PiRGBArray(cam, size=(416, 416))

mark = Manager()
DBmark = DBManager.DBManager()

def main():
    for frame in cam.capture_continuous(rawCapture, format='bgr', use_video_port=True):
        start_time = time.time()
        image = frame.array
        orig = image.copy()
        rawCapture.truncate(0)
        
        hsv = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, blue_min, blue_max)

        # Found it lmao
        res = find_ball(image, mask)
        if res is None:
            continue
        else:
            (x,y), radius = res

        # Normalize that shit
        x_norm = x / image.shape[1]
        y_norm = y / image.shape[0]

        
        # Keep track of FPS
        newtime = time.time()
        delta_time = newtime - start_time
        start_time = newtime

        if USE_GUI:
        # Point to it
            cv2.putText(image, str(round(x_norm, 3))+","+str(round(y_norm, 3)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)

            cv2.imshow("Input feed", orig)
            cv2.imshow("Mask", mask)
            cv2.imshow("Result", image)
            
        ball = Ball((x_norm * -2) + 1, (y_norm * -2) + 1)
        DBmark.set_ball_pos(ball.x, ball.y)
        DBmark.getNextStep()
        target = DBmark.array_data.target_coords
        mark.send(ball, target, delta_time)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

  
    cv2.destroyAllWindows()
    cam.close()

main()
