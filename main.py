import time
from machine import Pin

led = Pin(0, Pin.OUT)

def flicker():
	for i in range(0, 50):
		led.value(not led.value())
		time.sleep_ms(300)
