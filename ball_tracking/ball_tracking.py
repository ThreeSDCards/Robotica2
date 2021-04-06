from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

cv2.setNumThreads(0)
def nothing(x):
    pass
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="Path to optional video file")
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

greenLower = np.array([142, 138, 15]) # RGB = 142, 138, 15
greenUpper = np.array([255, 255, 131]) # RGB = 255, 255, 131
pts = deque(maxlen=args["buffer"])

# if videopath is not supplied, open webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# else get video file
else:
    vs = cv2.VideoCapture(args["video"])

# Allow camera or video file to "warm up"
time.sleep(2.0)

# Create detection sliders
cv2.namedWindow("Sliders")
cv2.createTrackbar("minR", "Sliders", 0, 255, nothing)
cv2.createTrackbar("minG", "Sliders", 0, 255, nothing)
cv2.createTrackbar("minB", "Sliders", 0, 255, nothing)
cv2.createTrackbar("maxR", "Sliders", 0, 255, nothing)
cv2.createTrackbar("maxG", "Sliders", 0, 255, nothing)
cv2.createTrackbar("maxB", "Sliders", 0, 255, nothing)


# BALL TRACKING HERE
while True:
    start_time = time.time()

    # grab current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    #If we are viewing a video and next frame does not exist, exit
    if frame is None:
        break

    # resize frame, blur, convert to HSV color space
    frame = imutils.resize(frame, width=600)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    # make mask for color "green", apply dilations and erosions to fix errors
    mask = cv2.inRange(hsv, (cv2.getTrackbarPos("minR", "Sliders"),
            cv2.getTrackbarPos("minG", "Sliders"),
            cv2.getTrackbarPos("minB", "Sliders")), 
            (cv2.getTrackbarPos("maxR", "Sliders"),
            cv2.getTrackbarPos("maxG", "Sliders"),
            cv2.getTrackbarPos("maxB", "Sliders")))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

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

    # Update point queue
    pts.appendleft(center)

    # Draw over the set of tracked points
    for i in range(1, len(pts)):
        if pts[i-1] is None or pts[i] is None:
            continue

        thickness = int(np.sqrt(args["buffer"] / float(i+1)) * 2.5)
        cv2.line(frame, pts[i-1], pts[i], (0,0,255), thickness)
    
    # Keep track of FPS
    newtime = time.time()
    print("Delta: {}".format(  str(1/( newtime - start_time))))
    start_time = newtime

    # Show data on schreen
    cv2.imshow("Mask", mask)
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF
    
    # Exit on q
    if key == ord("q"):
        break

# If we are not using a video file, stop the camera video stream
if not args.get("video", False):
    vs.stop()

# Else, release camera
else:
    vs.release()

# Die
cv2.destroyAllWindows()
