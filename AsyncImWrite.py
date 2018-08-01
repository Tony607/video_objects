from enum import Enum
from queue import Queue
from threading import Thread
import codecs
import cv2
from collections import namedtuple
import os
Img = namedtuple('Img', ['name', 'data'])
class QueueSignal(Enum):
    EXIT = 0

class AsyncImWrite:
    """
    A singleton class for AsyncImWrite
    """
    __baseDir = None
    def __new__(cls, baseDir='images'):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AsyncImWrite, cls).__new__(cls)
        else:
            cls.instance.cleanup()
        return cls.instance

    def __init__(self, baseDir='images'):
        self.__baseDir = baseDir
        if self.__baseDir:
            os.makedirs(self.__baseDir, exist_ok=True)
        self.__t = Thread(target=self.__async_worker)
        self.__t.daemon = True
        self.__q = Queue()
        self.running = True
        self.__t.start()
    def __del__(self):
        self.cleanup()

    def cleanup(self):
        self.running = False
        self.__q.put(QueueSignal.EXIT)
        self.__t.join()

    def __async_worker(self):
        while self.running:
            item = self.__q.get()
            if item == QueueSignal.EXIT:
                self.running = False
                break
            else:
                result = cv2.imwrite(item.name, item.data)
    def imwrite(self, name, data):
        if (self.__baseDir):
            name = os.path.join(self.__baseDir, name)
        self.__q.put(Img(name=name, data=data))

if __name__ == "__main__":
    writer = AsyncImWrite()    