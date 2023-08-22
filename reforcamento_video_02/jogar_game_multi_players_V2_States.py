import ast
import math
import random
import time

import paho.mqtt.client as mqtt

history = {}
learned_history = {}

def on_message(client, userdata, msg):
    global jogar, total_rewards, rodada, total_players, resultados, player_actions,\
        resetar, wait_response, high_scores, recorde, indice_recorde, delay, delay_period, history, learned_history,\
        estado_atual
    #print(msg.topic + " " + str(msg.payload.decode("utf-8")))

    if msg.topic == "rewards":
        pass
    mensagem = msg.payload.decode("utf-8").split("_")
    #print("############## mens", mensagem)
    if msg.topic == "states":
        ## rewards topic
        rewd= int(mensagem[2])
        total_rewards += rewd
        # print("Total rewards:", total_rewards)
        if not rewd == 100:
            # wait_response = False
            if delay:
                time.sleep(delay_period)
        ## rewards topic

        acao = mensagem[0]
        #estado_atual = mensagem[1]
        estado_acao = mensagem[1]
        recompensa = mensagem[2]
        estado_atual = mensagem[4]

        #print("msg.payload", msg.payload)
        #print("states", mensagem)
        if estado_acao in history:
            #dic = history[estado_atual].copy()
            #dic[mensagem[0]] = mensagem[2]
            #history[estado_atual] = dic.copy()

            history[estado_acao][acao] = recompensa
            #print("history[estado_atual][mensagem[0]]", history[estado_atual][mensagem[0]])
        else:
            history[estado_acao] = {acao : recompensa}
        #print(mensagem[0], "history", history)


        #if msg.topic == "done" and msg.payload == b"1":
        if mensagem[3] == "1":
            mqttc.publish("done", "reset")
            print(rodada, "de", total_players)
            #print("history", history)


            if total_rewards > recorde:
                recorde = total_rewards
                print("recorde", recorde)

                indice_recorde = rodada
                #learned_history.clear()

                learned_history = history.copy()
                #learned_history["recorde"] = recorde



                    #asdas

                #print("history", history)
                #print("learned_history", learned_history)
                #ads
            #print("######## nova rodada", rodada)
            rodada += 1
            resultados.append([total_rewards, player_actions.copy()])
            high_scores.append(total_rewards)


            #if resetar:
                # reseta valores
            #    total_rewards = 0
            #    player_actions.clear()
            #    resetar = False
            resetar = True

            if total_players == rodada:
                jogar = False

        else:#time.sleep(0.3)
            wait_response = False



            #print("estado atual", estado_atual)
            #print("learned_history", learned_history)
            if learned_history:
                #print("learned_history", learned_history)

                # print("learn", learned_history)
                # print("estado atual", estado_atual, type(estado_atual))
                # time.sleep(0.5)
                # print("learn choices", learned_history[estado_atual].keys())

                rd_choice = random.choice(list(learned_history[estado_atual].keys()))
                #print("list(learned_history[estado_atual].keys())", list(learned_history[estado_atual].keys()))
                #print("rd_choice", rd_choice)
                # print("random", ast.literal_eval(rd_choice)[0], type(rd_choice))

                action = ast.literal_eval(rd_choice)[0]
            else:
                action = random.choice(["up", "down", "left", "right"])
            #print("sent action", action, "estado_atual", estado_atual)

            player_actions.append(action)

            mqttc.publish("actions", action)
        #time.sleep(0.1)









def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #mqttc.subscribe("rewards")
    mqttc.subscribe("states")
    #mqttc.subscribe("done")

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
print("pedindo reset")


jogar = True
resetar = True
total_rewards = 0

total_players = 10
player_actions = []

rodada = 0

resultados = []
high_scores = []
recorde = -math.inf
indice_recorde = 0

wait_response = False

estado_atual = None

delay = False
delay_period = 0.4

print("Waiting")
#time.sleep(1)
print("Starting")



while jogar:

    if resetar:
        total_rewards = 0
        player_actions.clear()
        estado_atual = "[0, 0]"


        if learned_history:
            #print("learned_history", learned_history)

            # print("learn", learned_history)
            # print("estado atual", estado_atual, type(estado_atual))
            # time.sleep(0.5)
            # print("learn choices", learned_history[estado_atual].keys())

            rd_choice = random.choice(list(learned_history[estado_atual].keys()))
            #print("list(learned_history[estado_atual].keys())", list(learned_history[estado_atual].keys()))
            #print("rd_choice", rd_choice)
            # print("random", ast.literal_eval(rd_choice)[0], type(rd_choice))

            action = ast.literal_eval(rd_choice)[0]
        else:
            action = random.choice(["up", "down", "left", "right"])

        #print("primeira sent action", action, "estado_atual", estado_atual)
        history.clear()
        history["[0, 0]"] = {str([action]): "-1"}

        player_actions.append(action)
        mqttc.publish("actions", action)
        resetar = False
    if not wait_response:

        wait_response = True
    mqttc.loop()

for index, resultado in enumerate(resultados):
    #print(index, "Resultado", len(resultado[1]), resultado)
    print(index, "Resultado", resultado)

print("indice", indice_recorde, "maior_pontuacao", max(high_scores))
#print("maior_pontuacao2", max(resultados[0,]))
print("Fim")



