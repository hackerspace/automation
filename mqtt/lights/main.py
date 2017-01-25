""" esp8266 module to control 'n' lights and one button
    use config.py to configure"""

try:
    import webrepl
    webrepl.start()
except ImportError:
    pass

import time

try:
    from network import WLAN, STA_IF
    import config as cfg
except ImportError:
    from mock import WLAN, STA_IF
    import config_local as cfg

from mqtt.simple import MQTTClient
from mqtt.items import MQTTCom, ComInfo,  ComButton, ComLight
from utils import ManualGC

GC = ManualGC(1000)

WLAN = WLAN(STA_IF)

while not WLAN.isconnected():
    time.sleep(0.1)

print("Connecting to " + cfg.broker_host)
MQTT = MQTTClient('dev-' + cfg.dev_name, cfg.broker_host)

COM = MQTTCom(MQTT)

BUTTON = ComButton(
        com=COM, 
        pin=cfg.button[0], 
        name=cfg.button[1], 
        debounce=cfg.button_debounce,
        room=cfg.room)

LIGHTS = list()

for pin, name in cfg.lights:
    LIGHTS.append(
                ComLight(
                    com=COM, 
                    pin=pin, 
                    name=name,
                    room=cfg.room)
            )

ITEMS = list()
INFO = ComInfo(COM, cfg, ITEMS)

ITEMS.append(INFO)
ITEMS.append(BUTTON)
ITEMS.extend(LIGHTS)


def on_button():

    disable = False

    for light in LIGHTS:
        if light.pin.value() == 1:
            disable = True
            break

    if disable:
        for light in LIGHTS:
            light.pin.low()
    else:
        for light in LIGHTS:
            light.pin.high()

BUTTON.cb = on_button


def loop():
    """ main loop section """
    global MQTT
    global BUTTON
    global GC

    COM.check()

    for item in ITEMS:
        item.tick()

    GC.tick()

COM.try_init()


while True:
    loop()
