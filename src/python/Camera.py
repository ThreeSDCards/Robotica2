import picamera
from picamera.array import PiRGBArray
from .Image import Image


class Camera:
    def __init__(self):
        self.cam = picamera.PiCamera(0)
        self.cam.resolution = (416, 416)
        self.cam.framerate = 40
        self.cam.awb_mode = 'fluorescent'
        self.rawCapture = PiRGBArray(self.cam, size=(416, 416))
        self.capture = self.cam.capture_continuous(self.rawCapture, format='bgr', use_video_port=True)

    def __iter__(self):
        return self

    def __next__(self):
        res = next(sself.capture)
        self.rawCapture.truncate(0)
        return Image(res.array)