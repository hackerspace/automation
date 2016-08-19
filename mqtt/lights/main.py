""" esp8266 module to control 'n' lights and one button
    use config.py to configure"""

try:
    import webrepl
    webrepl.start()
except ImportError:
    pass

import time
import gc

try:
    from machine import Pin, 
    from network import WLAN, STA_IF
    import config as cfg
except ImportError:
    from mock import Pin, WLAN, STA_IF
    import config_local as cfg

from simple import MQTTClient


GC_LAST = time.ticks_ms()
GC_PERIOD = 1000

WLAN = WLAN(STA_IF)

BUTTON_TOPIC = b"/dev/" + cfg.dev_name + b"/buttons/" + str(cfg.button_pin)
BUTTON_PIN = Pin(cfg.button_pin, Pin.IN, Pin.PULL_UP)
BUTTON_LASTSTATE = 0
BUTTON_LASTTIME = time.ticks_ms()
BUTTON_DEBOUNCE = int(cfg.button_debounce * 1000)  # config in s, code in ms

LIGHTS_PINS = list()

for pin_n in cfg.lights_pins:
    pin_obj = Pin(pin_n, Pin.OUT)
    pin_obj.low()

    LIGHTS_PINS.append(pin_obj)

LED_PIN = Pin(cfg.led_pin, Pin.OUT)
LED_PIN.low()

MQTT = MQTTClient('dev-' + cfg.dev_name, cfg.broker_host)

def on_message(topic, msg):
    """ executed on every MQTT message received, have to explore the topic"""


    # we expect char representing number '0', '1', so we can just 'shift' it's
    # real value
    val = int(msg[0]) - 48

    if val not in [0, 1]:
        return

    # for now only receiveing topics are for lights itself, so this hack
    # to get light pin from topic works
    pin_number = int(chr(topic[-1]))

    if pin_number < len(LIGHTS_PINS):
        print("setting pin on channel " + str(pin_number) + " to value " + str(val) )
        LIGHTS_PINS[pin_number].value(val)

MQTT.cb = on_message


def mqtt_init():
    """ message to init mqtt connection with broker and subscribe to
    all required topics """
    while True:
        try:
            print("MQTT connection init")
            MQTT.connect()

            for i in range(len(LIGHTS_PINS)):
                topic_name = b'/dev/' + cfg.dev_name + b"/lights/" + str(i)
                print("Subscribing to topic:")
                print(topic_name)
                MQTT.subscribe(topic_name)

            MQTT.subscribe(INFO_SEND_TOPIC)

            return
        except OSError as err:
            print("Error during initialization of mqtt")
            print(err)
            time.sleep(1)


def loop():
    """ main loop section """
    global BUTTON_LASTSTATE
    global BUTTON_LASTTIME
    global BUTTON_DEBOUNCE
    global BUTTON_TOPIC
    global LIGHTS_PINS
    global MQTT
    global GC_LAST
    global GC_PERIOD

    try:
        # this won't work if mqtt.connect() was not called before!
        MQTT.check_msg()
    except OSError as err:
        print("error during check_msg")
        print(err)
        mqtt_init()

    button_pin_value = BUTTON_PIN.value()
    now = time.ticks_ms()

    if (BUTTON_LASTSTATE == 0 and button_pin_value == 1):
        if time.ticks_diff(BUTTON_LASTTIME, now) > BUTTON_DEBOUNCE:
            print("button pressed")
            MQTT.publish(BUTTON_TOPIC, b'1')

            disable = False

            for pin in LIGHTS_PINS:
                if pin.value() == 1:
                    disable = True
                    break

            if disable:
                print("disabling lighs")
                for pin in LIGHTS_PINS:
                    pin.low()
            else:
                print("enabling lights")
                for pin in LIGHTS_PINS:
                    pin.high()

            BUTTON_LASTTIME = now
        
        else:
            print("debounce")
            print(time.ticks_diff(BUTTON_LASTTIME, now))

    BUTTON_LASTSTATE = button_pin_value

    if time.ticks_diff(GC_LAST, now) > GC_PERIOD:
        gc.collect()
        GC_LAST = now


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
