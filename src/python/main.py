import cv2
import numpy as np
import imutils
import time
import DBManager
import serial
from manager import Manager
from Camera import Camera

USE_GUI = False

mark = Manager()
DBmark = DBManager.DBManager()



def main():
    cam = Camera()
    for frame in cam:
        ball = frame.getCircle()
        if ball is None:
            continue

        x_norm = ball.x / frame.shape[1]
        y_norm = ball.y / frame.shape[0]
            
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
