from twilio.rest import Client
import paho.mqtt.client as mqtt
import uuid
import time

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
def twil_set(topic_msg):
    account_sid = 'AC3e9d47ac7d01668599c498ff4cfa2bd9'
    auth_token = '3d6bade54dbfc3d64fda3ffdf45ea72a'
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                        body=topic_msg,
                        from_='+18507798023',
                        to='+13478938366'
                    )
    print(topic_msg)
    print(message.sid)

# MQTT Set Up
topic = 'IDD/rsl252/doorbell'

def on_connect(client, userdata, flags, rc):
    print(f"connected with result code {rc}")
    client.subscribe(topic)

def on_message(client, userdata, msg):
    # if a message is recieved on the colors topic, parse it and set the color
    if msg.topic == topic:
        topic_payload = msg.payload.decode('UTF-8')
        topic_msg = "VISITOR NOTIFICATION: " + topic_payload.upper()
        twil_set(topic_msg)

    return topic_msg

client = mqtt.Client(str(uuid.uuid1()))
client.tls_set()
client.username_pw_set('idd', 'device@theFarm')
client.on_connect = on_connect
client.on_message = on_message

client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

client.loop_start()

# MAIN LOOP
while True:
    time.sleep(.01)