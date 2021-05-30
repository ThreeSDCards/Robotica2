from Image import Image
from imutils.video import VideoStream

class Camera:
    def __init__(self, is_rpi, res, fps):
        self._vs = VideoStream(src=0, usePiCamera=is_rpi,
        resolution=res, framerate=fps).start()

    def getImage(self):
        return self._vs.read()
