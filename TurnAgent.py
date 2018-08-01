from ArduGimbal import ArduGimbal

class TurnAgent:
    """
    A singleton class for TurnAgent
    """

    __threshold = 15
    __reverse = False
    serPortObj = None

    def __new__(cls, threshold=15, reverse=False):
        if not hasattr(cls, 'instance'):
            cls.instance = super(TurnAgent, cls).__new__(cls)
        return cls.instance

    def __init__(self,threshold=15, reverse=False):
        self.__threshold = threshold / 100
        self.__reverse = reverse
        self.gimbal = ArduGimbal()
    
    
    def update(self, x):
        x = x - 0.5
        if (self.__reverse):
          x = -x
        if abs(x) > self.__threshold:
          if x > 0:
            self.gimbal.turn(-4)
          else:
            self.gimbal.turn(4)
    def center(self):
        self.gimbal.turn(90, absolute=True)

if __name__ == "__main__":
    agent = TurnAgent()
    from time import sleep
    while True:
        agent.center()
        sleep(2)
        agent.update(0.8)
        sleep(.1)
        agent.update(0.8)
        sleep(.1)
        agent.update(0.8)
        sleep(.1)
        agent.update(0.8)
        sleep(.1)
        agent.update(0.25)
        sleep(.1)
        agent.update(0.25)
        sleep(.1)
        agent.update(0.25)
        sleep(.1)
        print('Starting over again...')
