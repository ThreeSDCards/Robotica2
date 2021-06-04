import serial
import struct

class Manager:
    def __init__(self):
       self.uart = serial.Serial("/dev/ttyUSB0", 115200)

    def send(self, ball, target, delta_time):
        self.uart.write(struct.pack('fffff', ball.x, ball.y, target[0], target[1], delta_time))
