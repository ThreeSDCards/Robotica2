import time

class Timer:
    def __init__(self):
        self.start_time = time.time()

    def print(self):
        new_time = time.time()
        print(f"FPS: {1 / (new_time - self.start_time)}")
        self.start_time = new_time