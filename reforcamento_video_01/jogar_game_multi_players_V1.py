import math
import random
import time

import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    global jogar, total_rewards, rodada, total_players, resultados, player_actions,\
        resetar, wait_response, high_scores, recorde, indice_recorde, delay, delay_period
    #print(msg.topic + " " + str(msg.payload.decode("utf-8")))

    if msg.topic == "rewards":
        total_rewards += int(msg.payload.decode("utf-8"))
        #print("Total rewards:", total_rewards)
        if not int(msg.payload.decode("utf-8")) == 100:
            wait_response = False
            if delay:
                time.sleep(delay_period)

    if msg.topic == "done" and msg.payload == b"1":
        mqttc.publish("done", "reset")
        print(rodada, "de", total_players)

        if total_rewards > recorde:
            recorde = total_rewards
            print("recorde", recorde)
            indice_recorde = rodada

        rodada += 1




        resultados.append([total_rewards, player_actions.copy()])
        high_scores.append(total_rewards)

        resetar = True
        if resetar:
            # reseta valores
            total_rewards = 0
            player_actions.clear()
            resetar = False

        if total_players == rodada:
            jogar = False


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


jogar = True
resetar = False
total_rewards = 0

total_players = 100
player_actions = []

rodada = 0

resultados = []
high_scores = []
recorde = -math.inf
indice_recorde = 0

wait_response = False

delay = False
delay_period = 0.1

print("Waiting")
time.sleep(1)
print("Starting")

while jogar:
    if not wait_response:
        action = random.choice(["up", "down", "left", "right"])

        player_actions.append(action)

        mqttc.publish("actions", action)
        wait_response = True
    mqttc.loop()

for index, resultado in enumerate(resultados):
    #print(index, "Resultado", len(resultado[1]), resultado)
    print(index, "Resultado", resultado)

print("indice", indice_recorde, "maior_pontuacao", max(high_scores))
#print("maior_pontuacao2", max(resultados[0,]))
print("Fim")



