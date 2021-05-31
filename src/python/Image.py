import cv2
import imutils
import Circle

blue_min = (90, 155, 60)
blue_max = (160, 255, 255)

class Image:

    def __init__(self, data):
        self.data = data

    def getCircle(self):
        hsv = cv2.cvtColor(self.data.copy(), cv2.COLOR_BGR2HSV)
        mask_ball = cv2.inRange(hsv, blue_min, blue_max)
        
        # Find contours and point
        cnts = cv2.findContours(mask_ball.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        center = None

        # Only proceed if anything was found
        if len(cnts) > 0:
            #Find largest contour in the mask, then use it to find circle
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 10:
                #Draw circle and centre on frame, then update tracked points
                cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)

        return Circle.Circle((int(x),int(y)), radius)
