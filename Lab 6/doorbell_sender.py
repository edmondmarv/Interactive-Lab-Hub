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

topic = 'IDD/rsl252/doorbell'

i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)

while True:
    for i in range(12):
        if mpr121[i].value:
            val = f"{i}"
            print(val)
            if val == "6":
                msg = "Someone is ringing your doorbell at the side door"
                print(msg)
                client.publish(topic, msg)
            elif val == "9":
                msg = "Someone is ringing your doorbell at the back door"
                print(msg)
                client.publish(topic, msg)
            elif val == "11":
                msg = "Someone is ringing your doorbell at the front door"
                print(msg)
                client.publish(topic, msg)
            client.publish(topic, msg)
    time.sleep(0.25)