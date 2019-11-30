# This file is executed on every boot (including wake-boot from deepsleep)

import gc
gc.collect()

def startWebRepl():
    import webrepl
    webrepl.start()

# Only need to be called once, the ESP8266 will recall the network
def do_connect():
    import network
    import time
    from machine import Pin, Signal
    sta_if = network.WLAN(network.STA_IF)

    # LED is used to indicate connection state
    led = Signal(Pin(13, Pin.OUT), invert=True)
    led.value(0)

    #Wait to see if connection forms
    for i in range(0,4):
        if sta_if.isconnected():
            break
        time.sleep_ms(500)

    if not sta_if.isconnected():
        from config import wifi
        print('Connecting to %s...' %(wifi['ssid']))
        sta_if.active(True)
        sta_if.connect(wifi['ssid'], wifi['password'])
        while not sta_if.isconnected():
            pass
    network.WLAN(network.AP_IF).active(False)
    led.value(1)
    print('Network config:', sta_if.ifconfig())

do_connect()
startWebRepl()
