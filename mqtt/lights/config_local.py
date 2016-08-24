""" config for  esp """

dev_name = 'esplana'
broker_host = '127.0.0.1'

room="workroom"

""" topics will be subscribed with pins name !"""
lights = (
        (4,"table_left"), 
        (5,"table_right")
        )

button = (13, 'table')
button_debounce = 0.2

led_pin = 15
