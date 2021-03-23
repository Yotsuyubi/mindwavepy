import serial
from .parser import Parser


class Mindwave:

    def __init__(self):
        self.hoge = []
        self.serial = None

    def connect(self, dev):
        self.serial = serial.Serial(dev, 57600)

    def close(self):
        self.serial.close()

    def read_byte(self):
        return self.serial.read()
