from machine import Pin

from simple import MQTTClient

import time
import network

import config as cfg

#
#   set:
#       [0] = 0, [1] - n of led, [2-4] - RGB values
#
#   write:
#       [0] = 1, [1] - id, this is send in ack after it's done
#

wlan = network.WLAN(network.STA_IF)

button_topic = b"/dev/" + cfg.dev_name + b"/buttons/" + str(cfg.button_pin)
button_pin = Pin(cfg.button_pin, Pin.IN)

lights_pins = dict()

for pin_n in cfg.lights_pins:
    lights_pins[pin_n] = Pin(pin_n, Pin.OUT)


def on_message(topic, msg):

    print( "got msg " + str(msg) + " on: " + str(topic) )

    if msg[0] not in [0, 1]:
        print( "msg value bad" )
        return

    pin = int(chr(topic[-1]))

    if pin in lights_pins.keys():
        print( "setting pin " + pin + " to " + str(msg[0]))
        lights_pins[pin].value(msg[0])


while not wlan.isconnected():
    time.sleep(0.1)

mqtt = MQTTClient('dev-' + cfg.dev_name, cfg.broker_host)
mqtt.cb = on_message

mqtt.connect()


for light_pin in cfg.lights_pins:
    mqtt.subscribe(b'/dev/' + cfg.dev_name + b"/lights/" + str(light_pin))

while True:
    mqtt.check_msg()

    if button_pin.value() == 0:
        mqtt.publish(button_topic, bytearray([1]))

        disable = False

        for pin in lights_pins.values():
            if pin.value() == 1:
                disable = True
                break

        if disable:
            for pin in lights_pins.values():
                pin.low()
