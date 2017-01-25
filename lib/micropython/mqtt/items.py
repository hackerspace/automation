import time
import machine
import esp
import gc
import os
from machine import Pin


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
            self.try_init()

    def publish(self, topic, msg):
        if self.is_connected:
            self.mqtt.publish(topic, msg)

    def try_init(self):

        try:
            self.mqtt.connect()
            self._subscribe_all()
            self.is_connected = True
            return
        except OSError:
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
    def __init__(self, com, cfg, items):
        self.com = com
        self.sub_topic = '/info/send'
        self.ctl_pub_topic = '/info/ctl'
        self.hp_pub_topic = '/info/hp'
        self.desc_pub_topic = '/info/desc'
        self.cfg = cfg
        self.items = items

        com.subscribe(self.sub_topic, self._on_msg)

    def _on_msg(self, msg):

        if msg.startswith(u"ctl"):
            msgs = list()
            topic = self.ctl_pub_topic

            for item in self.items:

                if item == self:
                    continue

                msgs.extend([",".join(info) for info in item.gather_info()])

        elif msg.startswith(u"hp"):
            msgs = self.gather_health_info()
            topic = self.hp_pub_topic

        elif msg.startswith(u"desc"):
            msgs = [self.cfg.description]
            topic = self.desc_pub_topic

        else:
            print("bad topic for info")
            return

        for msg in msgs:
            self.com.publish(topic, self.cfg.dev_name + ":" + msg)

    def gather_health_info(self):
        return [
            "flash id, " + str(esp.flash_id()),
            "cpu freq, " + str(machine.freq()),
            "unique id, " + str(machine.unique_id()),
            "mem alloc, " + str(gc.mem_alloc()),
            "mem gree, " + str(gc.mem_free()),
            "statvfs, " + ",".join([str(x) for x in os.statvfs("")]),
        ]

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

            print("button times", now, self._lasttime)

            if time.ticks_diff(now, self._lasttime) > self.debounce:

                self.com.publish(self.topic, b'1')

                self.cb()

                self._lasttime = now

        self._laststate = pin_value

    def gather_info(self):
        return (('pub', 'button', self.topic, 'sends char 1 when pressed'), )


class ComLight:
    def __init__(self, com, pin, name, room):
        self.pin = Pin(pin, Pin.OUT)
        self.pin.low()
        self.com = com
        self.ctl_topic = '/' + room + '/lights/ctl/' + name
        self.event_topic = '/' + room + '/lights/events/' + name
        com.subscribe(self.ctl_topic, self._on_msg)

    def _on_msg(self, msg):
        val = msg[0] - 48

        if val == 1:
            self.pin.high()
            self.com.publish(self.event_topic, b'1')
        elif val == 0:
            self.pin.low()
            self.com.publish(self.event_topic, b'0')

    def gather_info(self):
        return (('sub', 'light', self.ctl_topic,
                 'Send char of 0 or 1 to turn off or on'),
                ('pub', 'light', self.event_topic,
                 'Sned char of 0 or 1 when light tunerd off or on'))

    def tick(self):
        pass
