import time
import board
import busio
import adafruit_mpr121

import paho.mqtt.client as mqtt
import uuid

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

topic = 'IDD/rsl252/gesture/test'

#i2c = busio.I2C(board.SCL, board.SDA)

#mpr121 = adafruit_mpr121.MPR121(i2c)

#while True:
#    for i in range(12):
#        if mpr121[i].value:
#            val = f"Twizzler {i} touched!"
#            print(val)
#            client.publish(topic, val)
#    time.sleep(0.25)


import board
from adafruit_apds9960.apds9960 import APDS9960

i2c = board.I2C()

apds = APDS9960(i2c)
apds.enable_proximity = True
apds.enable_gesture = True

# Uncomment and set the rotation if depending on how your sensor is mounted.
# apds.rotation = 270 # 270 for CLUE

while True:
    gesture = apds.gesture()

    if gesture == 0x01:
        val = "up"
        print("up")
        client.publish(topic, val)
    elif gesture == 0x02:
        val = "down"
        print("down")
        client.publish(topic, val)
    elif gesture == 0x03:
        val = "left"
        print("left")
        client.publish(topic, val)
    elif gesture == 0x04:
        val = "right"
        print("right")
        client.publish(topic, val)