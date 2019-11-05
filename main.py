import time
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
			mqttClient.wait_msg()
	except Exception as e:
		print(e.__doc__)
	finally:
		mqttClient.disconnect()

if __name__ == "__main__":
	main()