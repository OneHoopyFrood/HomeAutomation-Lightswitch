from config import mqtt as mqtt_config
from mqtt_switch import MQTTSwitch

def main():
	switch = MQTTSwitch(
		12, 0,
		primary_topic=mqtt_config['primary_topic'],
		server_address=mqtt_config['server'],
		keepalive=10)

	# Run
	switch.run()

if __name__ == "__main__":
	main()