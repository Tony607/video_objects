import serial.tools.list_ports
from enum import Enum
from queue import Queue
from threading import Thread
import codecs

class QueueSignal(Enum):
    EXIT = 0

class CMD:
    ABSOLUTE = 0xFE
    DELTA = 0xFF

class ArduGimbal:
    """
    A singleton class for ArduGimbal
    """

    __on_angle_listener = None
    __port = None
    __baudrate = 9600
    serPortObj = None

    def __new__(cls,port=None, baudrate=9600, on_angle_listener=None):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ArduGimbal, cls).__new__(cls)
        else:
            cls.instance.cleanup()
        return cls.instance

    def __init__(self,port=None, baudrate=9600, on_angle_listener=None):
        self.__port = port
        self.__baudrate = baudrate
        self.__open_arduino_port(searchPort=self.__port)
        self.rx = Thread(target=self.__async_worker_rx)
        self.tx = Thread(target=self.__async_worker_tx)
        self.rx.daemon = True
        self.tx.daemon = True
        self.__q = Queue()
        if on_angle_listener is not None and callable(on_angle_listener):
            self.__on_angle_listener = on_angle_listener
        
        self.running = True
        self.rx.start()
        self.tx.start()
    def __del__(self):
        self.cleanup()
    
    def __open_arduino_port(self, searchPort=None):
        ports = list(serial.tools.list_ports.comports())
        for p in ports:
            if "arduino" in p.description.lower():
                print("Found Arduino at port {}".format(p.device))
                self.__port = p.device
                # Timeout set to 1 second.
                print('>>>Try Port open.')
                self.serPortObj = serial.Serial(port=self.__port,baudrate=self.__baudrate, timeout=1)
                print('>>>Port open.')
                return True
        return False
    
    def _stop_reader(self):
        """Stop reader thread only, wait for clean exit of thread"""
        if hasattr(self.serPortObj, 'cancel_read'):
            self.serPortObj.cancel_read()
        self.tx.join()
        self.rx.join()

    def cleanup(self):
        self.running = False
        self.__q.put(QueueSignal.EXIT)
        if self.serPortObj is not None:
            self._stop_reader()
            self.serPortObj.close()
            print('close port')

    def __async_worker_rx(self):
        
        while self.running:
            s = self.serPortObj.readline()
            content = s.decode().rstrip().strip().split('-')
            if len(content) == 2:
                print('Servo:', content[0], ' is at angle:', content[1])
                if self.__on_angle_listener:
                    self.__on_angle_listener(content)
    def __async_worker_tx(self):
        while self.running:
            item = self.__q.get()
            if item == QueueSignal.EXIT:
                self.running = False
                break
            else:
                data = self._sendCommand(item)
    def turn(self, angle, absolute = False,axis=0):
        packet = bytearray()
        if absolute:
            angle = self._clamp(angle)
            packet.append(angle)
            packet.append(CMD.ABSOLUTE)
        else: # Relative angle could be positive or negative.
            angle = self._clamp(angle, min = -90, max=90)
            packet.append(angle + 90)
            packet.append(CMD.DELTA)
        self.__q.put(packet)
    
    @classmethod
    def _clamp(cls, v, max=180, min=0):
        if v > max:
            return max
        if v < min:
            return min
        return v

    def _sendCommand(self, cmd):
        self.serPortObj.write(cmd)
        return

if __name__ == "__main__":
    gimbal = ArduGimbal()
    from time import sleep
    while True:
        # gimbal.turn(-10)
        # sleep(4)
        # gimbal.turn(50)
        # sleep(4)
        gimbal.turn(90, absolute=True)
        sleep(4)
        gimbal.turn(70, absolute=True)
        sleep(4)
        gimbal.turn(110, absolute=True)
        sleep(4)
        print('Starting over again...')
