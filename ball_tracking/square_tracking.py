import cv2
import numpy as np
from imutils.video import VideoStream
import imutils
import time

#Start webcam
vs = VideoStream(src=0, usePiCamera=True,
        resolution=(640,480), framerate=60).start()

def toPointList(ndArr):
    return [tuple(i[0]) for i in ndArr]

def cut_square(img, contour, ratio):
    pts = contour.reshape(4, 2)
    rect = np.zeros((4, 2), dtype = "float32")

    #Find top left and bottom right
    s = pts.sum(axis = 1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    #Calculating deltas
    diff = np.diff(pts, axis = 1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # multiply the rectangle by the original ratio
    rect *= ratio

    # now that we have our rectangle of points, let's compute
    # the width of our new image
    (tl, tr, br, bl) = rect
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    # ...and now for the height of our new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    # take the maximum of the width and height values to reach
    # our final dimensions
    maxWidth = max(int(widthA), int(widthB))
    maxHeight = max(int(heightA), int(heightB))
    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array([
	    [0, 0],
	    [maxWidth - 1, 0],
	    [maxWidth - 1, maxHeight - 1],
	    [0, maxHeight - 1]], dtype = "float32")
    # calculate the perspective transform matrix and warp
    # the perspective to grab the screen
    M = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(img, M, (maxWidth, maxHeight))

def find_best_contour(cnts):
    screenCnt = None
    for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.015 * peri, True)
            if len(approx) == 4:
                screenCnt = approx
                break
    return screenCnt

def find_ball(frame, mask):
    # Find contours and point
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
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

    return ((int(x),int(y)), radius)

def nothing(x):
    pass

blue_min = (90, 155, 60)
blue_max = (160, 255, 255)

#cv2.namedWindow("Sliders")
#cv2.createTrackbar("minH", "Sliders", 100, 255, nothing)
#cv2.createTrackbar("minS", "Sliders", 155, 255, nothing)
#cv2.createTrackbar("minV", "Sliders", 60 , 255, nothing)
#cv2.createTrackbar("maxH", "Sliders", 160, 255, nothing)
#cv2.createTrackbar("maxS", "Sliders", 255, 255, nothing)
#cv2.createTrackbar("maxV", "Sliders", 255, 255, nothing)
#cv2.resizeWindow("Sliders", 400, 500)

screenCnt = np.zeros((4,2), dtype="uint32")
lastContour = np.zeros((4,2), dtype="uint32")
zeros = np.zeros((300,300, 3), "float32")
zoom = zeros.copy()

def main():
    while True:
        start_time = time.time()
        #640, 480
        image = vs.read()
        if image is None:
            continue
        ratio = image.shape[0] / 400.0 # 1.???
        orig = image.copy()
        
        #400, 300
        image = imutils.resize(image, height = 400)
        
        gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)

        #f = cv2.getTrackbarPos("Filter", "Sliders")
        _, mask= cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
        mask = cv2.GaussianBlur(mask, (3,3), cv2.BORDER_DEFAULT)

        cnts = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
        
        square_cnt = find_best_contour(cnts)
        
        if square_cnt is not None:
            zoom = cut_square(orig, square_cnt, ratio)

        mask_ball = zeros.copy()
        try:
            hsv = cv2.cvtColor(zoom.copy(), cv2.COLOR_BGR2HSV)
            mask_ball = cv2.inRange(hsv, blue_min, blue_max)
            # Found it lmao
            (x,y), radius = find_ball(zoom, mask_ball)
            # Normalize that shit
            x_norm = x / zoom.shape[1]
            y_norm = y / zoom.shape[0]

            # Point to it
            cv2.putText(zoom, str(round(x_norm, 3))+","+str(round(y_norm, 3)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)
        
            #print("X: " + str(x_norm) + " Y: " + str(y_norm))    
        except Exception:
            pass

        cv2.imshow("Input feed", orig)
        cv2.imshow("Mask", mask)
        
        try:
            cv2.imshow("Ball mask", mask_ball)
            cv2.imshow("Zoom", zoom)
        except Exception:
            pass
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
