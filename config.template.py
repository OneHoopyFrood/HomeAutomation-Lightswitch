# Use this file to setup a wifi config file for the boot.py script
wifi = {
  'ssid': '',
  'password': '',
}

mqtt = {
  'server': '<serverIP>',
  'client_id': '<mqtt_unique_client_id>',
  'state_topic': b'<topic>',
  'set_topic': b'<topic>/set', # Reccomended pattern
}
