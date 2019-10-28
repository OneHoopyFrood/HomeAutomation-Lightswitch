# This file is executed on every boot (including wake-boot from deepsleep)

import gc
gc.collect()

def startWebRepl():
    import webrepl
    webrepl.start()

def do_connect():
    import network
    import wifi_details
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(wifi_details.ssid, wifi_details.password)
        while not sta_if.isconnected():
            pass
    ap_if.active(False)
    print('network config:', sta_if.ifconfig())

startWebRepl()
do_connect()
