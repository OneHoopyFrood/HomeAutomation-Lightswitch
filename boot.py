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
    sta_if = network.WLAN(network.STA_IF)

    #Wait to see if connection forms
    for i in range(0,3):
        if sta_if.isconnected():
            break
        time.sleep_ms(600)

    if not sta_if.isconnected():
        import wifi_details
        print('Connecting to %s...' %(wifi_details.ssid))
        sta_if.active(True)
        sta_if.connect(wifi_details.ssid, wifi_details.password)
        while not sta_if.isconnected():
            pass
    network.WLAN(network.AP_IF).active(False)
    print('Network config:', sta_if.ifconfig())

# startWebRepl()
do_connect()
