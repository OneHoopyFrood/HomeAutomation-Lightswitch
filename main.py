import time
from machine import Pin
from umqtt.robust import MQTTClient

led = Pin(0, Pin.OUT)
led.off()

def flicker():
	for i in range(0, 10):
		led.value(not led.value())
		time.sleep_ms(100)

def set_light_state(state):
	print('Light: ', bool(state))
	led.value(state)

def handle_msg(topic, msg):
	print(topic, msg)
	try:
		set_light_state(int(msg))
	except ValueError:
		print("Message not a number")

def main(server="localhost"):
	c = MQTTClient("nook_overheadlights", server)
	c.DEBUG = True
	c.set_callback(handle_msg)
	c.connect()
	c.subscribe(b"house/nook/overheadlights")

	while True:
		# Blocking wait
		c.wait_msg()

	c.disconnect()

if __name__ == "__main__":
	main("192.168.0.5")