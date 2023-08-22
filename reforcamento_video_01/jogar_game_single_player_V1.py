import random
import time

import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    global temMqtt, total_rewards
    print(msg.topic + " " + str(msg.payload.decode("utf-8")))

    if msg.topic == "rewards":
        total_rewards += int(msg.payload.decode("utf-8"))
        print("Total rewards:", total_rewards)

    if msg.topic == "done" and msg.payload == b"1":
        temMqtt = False


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    mqttc.subscribe("rewards")
    mqttc.subscribe("done")

temMqtt = True
mqttc = mqtt.Client()
mqttc.on_message = on_message
mqttc.on_connect = on_connect

try:
    mqttc.connect("127.0.0.1", port=1883)
except:
    temMqtt = False
    print("Sem MQTT")

mqttc.publish("done", "reset")

total_rewards = 0

print("Waiting")
time.sleep(5)
print("Starting")

while temMqtt:
    action = random.choice(["up", "down", "left", "right"])

    mqttc.publish("actions", action)

    mqttc.loop()

    time.sleep(0.4)

print("Recompensa total", total_rewards)
print("Fim")



