import time
from utime import ticks_ms
from machine import Pin
from umqtt.robust import MQTTClient
from config import mqtt as mqttConfig

def set_switch_state(state):
	global mqttClient
	led = Pin(0, Pin.OUT)
	led.value(state)
	print('Setting switch to', state)
	# Now publish the state on the state topic
	mqttClient.publish(mqttConfig['state_topic'], b'1' if state else b'0', retain=True, qos=1)

def handle_msg(topic, msg):
	try:
		set_switch_state(int(msg))
	except ValueError:
		print("Message not a number")

ticks_at_last_heartbeat = ticks_ms()
def heartbeat():
	global ticks_at_last_heartbeat
	if ticks_ms() - ticks_at_last_heartbeat > 3000:
		global mqttClient
		# print('Sending heartbeat...')
		ticks_at_last_heartbeat = ticks_ms()
		mqttClient.ping()

def main():
	# TODO I'm pretty sure globals are still evil in MicroPython. Need a better solution
	global mqttClient
	mqttClient = MQTTClient(mqttConfig['client_id'], mqttConfig['server'], keepalive=5)

	# Setup the conneciton
	mqttClient.set_callback(handle_msg)
	mqttClient.set_last_will(mqttConfig['state_topic'], msg=b'0', retain=True, qos=1) # Last Will message is that the light is now off.
	mqttClient.connect()
	mqttClient.subscribe(mqttConfig['set_topic'], 1)
	print("Connected to %s, subscribed to %s topic" % (mqttConfig['server'], mqttConfig['set_topic']))

	# Off on reboot
	set_switch_state(0)

	# Now await messages
	try:
		while True:
			mqttClient.check_msg()
			heartbeat()
			time.sleep_ms(50)
	except Exception as e:
		print(e)
	finally:
		mqttClient.disconnect()

if __name__ == "__main__":
	main()