import time
import gc
try:
    from machime import Pin
except ImportError:
    from mock import Pin


class MQTTCom:


    def __init__(self, mqtt):

        self.mqtt = mqtt
        self.subs = dict()
        self.is_connected = False
        mqtt.cb = self._on_cb

    def check(self):
        try:
            self.mqtt.check_msg()
        except OSError:
            self.is_connected = False
            self.init(infinite=False)

    def publish(self, topic, msg):
        if self.is_connected:
            self.mqtt.publish(topic, msg)

    def init(self, infinite=True):

        while True:
            try:
                self.mqtt.connect()
                self._subscribe_all()
                self.is_connected = True
                return
            except OSError:
                if not infinite:
                    return

    def _subscribe_all(self):
        for key in self.subs.keys():
            self.mqtt.subscribe(key)

    def subscribe(self, topic, cb):

        print("subscribing ", topic)

        self.subs[topic.encode('utf-8')] = cb
        if self.is_connected:
            self.mqtt.subscribe(topic)

    def _on_cb(self, topic, msg):
        print("got ", topic, msg)
        try:
            self.subs[topic](msg)
        except KeyError:
            print("cb not found")
            print(topic)


class ComInfo:
    def __init__(self, com, items):
        self.com = com
        self.sub_topic = '/info/send'
        self.pub_topic = '/info'
        self.items = items

        com.subscribe(self.sub_topic, self._on_msg)

    def _on_msg(self, msg):

        if msg[0] != 1 + 48:
            return

        for item in self.items:

            if item == self:
                continue

            for info in item.gather_info():
                self.com.publish(self.pub_topic, ",".join(info))

    def tick(self):
        pass


class ComButton:
    def __init__(self, com, pin, name, debounce, room):
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.com = com
        self.topic = '/' + room + '/buttons/' + name
        self._laststate = 0
        self._lasttime = time.ticks_ms()
        self.debounce = debounce
        self.cb = lambda: None

    def tick(self):
        pin_value = self.pin.value()
        now = time.ticks_ms()

        if self._laststate == 0 and pin_value == 1:

            if time.ticks_diff(self._lasttime, now) > self.debounce:

                self.com.publish(self.topic, b'1')

                self.cb()

                self._lasttime = now

        self._laststate = pin_value

    def gather_info(self):
        return (('pub', 'button', self.topic, 'sends char 1 when pressed'),)


class ComLight:
    def __init__(self, com, pin, name, room):
        self.pin = Pin(pin, Pin.OUT)
        self.pin.low()
        self.com = com
        self.topic = '/' + room + '/lights/' + name
        com.subscribe(self.topic, self._on_msg)

    def _on_msg(self, msg):
        val = msg[0] - 48

        if val == 1:
            self.pin.high()
        elif val == 0:
            self.pin.low()

    def gather_info(self):
        return (('sub', 'light', self.topic, 'Send char of 0 or 1 to turn off or on'),)

    def tick(self):
        pass

