from utime import ticks_diff, ticks_ms, sleep_ms, time
from machine import Pin, reset
from umqtt.robust import MQTTClient
from umqtt.simple import MQTTException

class MQTTSwitch(MQTTClient):
  """MQTTSwitch

  Defines a switch that assumes a relay and momentary button are connected to the provided GPIO pins.
  """

  def __init__(self,
      relay_pin_number, button_pin_number,
      primary_topic, server_address='127.0.0.1',
      client_id='', keepalive=30):
    ### Setup MQTT variables ######
    self.state_topic = primary_topic.encode()
    self.set_topic = (primary_topic + '/set').encode()
    self.availability_topic = (primary_topic + '/available').encode()
    self.client_id = client_id
    # Default client ID is "mp_" followed by the mac address
    if self.client_id == '':
      import network
      import ubinascii
      mac = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
      self.client_id = ('mp_' + mac).encode()
    self.server_address = server_address
    ### Initialize the super() ######
    super().__init__(client_id, server_address, keepalive=keepalive)
    ### Setup GPIOs ######
    self.relay = Pin(relay_pin_number, Pin.OUT)
    self.button = Pin(button_pin_number, Pin.IN) # LOW when pressed
    self.ticks_at_last_heartbeat = ticks_ms()


  def run(self):
    """
    Connect to MQTT server, start sending heartbeasts, and await command
    """
    self.start_time = time()
    # Setup MQTT connection
    self.set_callback(self.__handle_msg)
    self.set_last_will(self.availability_topic, msg=b'offline', retain=True, qos=1)
    # TODO What if the MQTT Broker isn't available?
    self.connect()
    self.subscribe(self.set_topic, 1)
    # Set available
    self.publish(self.availability_topic, msg=b'online', retain=True, qos=1)
    print("Connected to %s, subscribed to topic: '%s'" %(self.server_address, self.set_topic.decode()))
    # Start off
    self.off()
    # TODO Setup button IQR

    # Begin main loop
    while True:
      try:
        self.check_msg()
        self.__heartbeat()
        sleep_ms(50)
      except MQTTException as e:
        print("MQTT Error encountered", e)
        print('Attempting to recover')
        print('Disconnecting from server...')
        self.disconnect()
        sleep_ms(100)
        print('Reconnecting...')
        try:
          self.connect()
          print('Recovered. Continuing...')
        except MQTTException as e2:
          print('Recovery failed.')
          raise Exception('Unable to recover from MQTT Error')
      except Exception as e:
        # Write to log
        f = open('Error.log', 'a')
        f.write('Error at %s' %(time()) + e + '\n')
        # Signal problem with LED flash
        led = Pin(13, Pin.OUT)
        while True:
          led.value(led.value() % 2)
          sleep_ms(1000)

    self.disconnect()

  def on(self):
    self.set_value(1)

  def off(self):
    self.set_value(0)

  def state(self):
    return 'ON' if self.relay.value() == 1 else 'OFF'

  def set_value(self, value):
    print('Setting relay pin to %s' %(value))
    self.relay.value(value)
    # Publish to MQTT Topic
    self.publish(self.state_topic, self.state().encode(), retain=True, qos=1)


  def __handle_msg(self, topic, msg):
    try:
      str_msg = msg.decode().upper()
      print('Message recieved: ', str_msg)
      if str_msg == 'ON' or str_msg == '1':
        self.on()
      elif str_msg == 'OFF' or str_msg == '0':
        self.off()
      else:
        print('Message ignored')
    except ValueError:
      print('Something went wrong while receiving a message')

  def __heartbeat(self):
    if ticks_diff(ticks_ms(), self.ticks_at_last_heartbeat) > (self.keepalive * 1000 / 2):
      print('noop', '-', time() - self.start_time)
      self.ticks_at_last_heartbeat = ticks_ms()
      self.ping()

  def __handle_button_press(self):
    pass
