""" esp8266 module to control 'n' lights and one button
    use config.py to configure"""

import time
try:
    from machine import Pin
    from network import WLAN, STA_IF
except ImportError:
    from mock import Pin, WLAN, STA_IF

from simple import MQTTClient


import config as cfg

WLAN = WLAN(STA_IF)

BUTTON_TOPIC = b"/dev/" + cfg.dev_name + b"/buttons/" + str(cfg.button_pin)
BUTTON_PIN = Pin(cfg.button_pin, Pin.IN)

LIGHTS_PINS = dict()

for pin_n in cfg.lights_pins:
    LIGHTS_PINS[pin_n] = Pin(pin_n, Pin.OUT)


MQTT = MQTTClient('dev-' + cfg.dev_name, cfg.broker_host)


def on_message(topic, msg):
    """ executed on every MQTT message received, have to explore the topic"""

    print("got msg " + str(msg) + " on: " + str(topic))

    val = int(msg[0]) - 48

    print("value: " + str(val))

    if val not in [0, 1]:
        print("msg value bad")
        return

    pin_number = int(chr(topic[-1]))

    if pin_number in LIGHTS_PINS.keys():
        print("setting pin " + str(pin_number) + " to " + str(val))
        LIGHTS_PINS[pin_number].value(val)
    else:
        print("unknown pin")

MQTT.cb = on_message


def mqtt_init():
    """ message to init mqtt connection with broker and subscribe to
    all required topics """
    while True:
        try:
            print("MQTT connection init")
            MQTT.connect()

            for light_pin in cfg.lights_pins:
                MQTT.subscribe(
                    b'/dev/' + cfg.dev_name + b"/lights/" + str(light_pin)
                    )

            return
        except OSError as err:
            print("Error during initialization of mqtt")
            print(err)
            time.sleep(1)


def loop():
    """ main loop section """

    try:
        # this won't work if mqtt.connect() was not called before!
        MQTT.check_msg()
    except OSError as err:
        print("error during check_msg")
        print(err)
        mqtt_init()

    if BUTTON_PIN.value() == 0:
        MQTT.publish(BUTTON_TOPIC, bytearray([1]))

        disable = False

        for pin in LIGHTS_PINS.values():
            if pin.value() == 1:
                disable = True
                break

        if disable:
            for pin in LIGHTS_PINS.values():
                pin.low()


def main():
    """ MAINZ! """

    # this is wise to do on startup...
    while not WLAN.isconnected():
        time.sleep(0.1)

    mqtt_init()
    print("connection done, entering main loop")


main()
while True:
    loop()
