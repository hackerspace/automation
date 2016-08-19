""" mockup module to use when running on unix system """

import time as p_time

class Pin:

    IN = 'in'
    OUT = 'out'
    PULL_UP = 'pull_up'

    def __init__(self, n, way, pullup=False):
        self.n = n
        self.way = way

        self._val = 0

        self._get_counter = 0

    def high(self):
        self.value(1)

    def low(self):
        self.value(0)

    def value(self, val=None):
        if val is None:
            if self.way == self.IN:
                if self._get_counter == 2000000:
                    self._get_counter = 0
                    print("sending random 1 from pin " + str(self.n))
                    return 1
                else:
                    self._get_counter += 1
                    return 0
            else:
                return self._val

        assert val in [0, 1]
    
        self._val = val

        print(" value of pin {} set as {}".format(self.n, val))


STA_IF = 'STA_IF'


class WLAN:

    def __init__(self, t):
        self.t = t

    def isconnected(self):
        return True

