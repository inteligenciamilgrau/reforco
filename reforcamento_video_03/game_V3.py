import random
import time

import pygame
import threading
import subprocess
import paho.mqtt.client as mqtt

class Grid_game():
    def __init__(self, size=(4,4)):

        pygame.init()
        self.window_size = (size[0] * 100, size[1] * 100)
        self.window_center = (self.window_size[0] / 2, self.window_size[1] / 2)
        self.window = pygame.display.set_mode(self.window_size)
        pygame.display.set_caption("Inteligencia Mil Grau - Grid Game")

        self.action = "right"
        self.state = [0,0] # x, y
        self.size = size
        #self.rewards = [(0,1),(0,2)]
        self.rewards = set([])
        self.rewards_table = set([])
        self.generate_rewards(total=20)
        self.rewards = self.rewards_table.copy()
        self.end = (size[0] - 1, size[1] - 1)

        self.topic_rewards = "rewards"

        self.temMqtt = True
        self.mqttc = mqtt.Client()
        self.mqttc.on_message = self.on_message
        self.mqttc.on_connect = self.on_connect

        self.roda_subprocess = True
        mqtt_thread = threading.Thread(target=self.start_subprocess)
        mqtt_thread.start()

        self.running = True

        self.done = False

        pygame.font.init()  # you have to call this at the start,
        self.my_font = pygame.font.SysFont('Comic Sans MS', 30)

        while self.running:
            self.update()

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.temMqtt = False
                pygame.display.quit()
                pygame.quit()
                exit()



        self.draw()

        pygame.time.delay(30)
        pygame.display.update()

    def play(self, action):
        actual_state = self.state.copy()
        if action == ["right"]:
            self.state[0] = self.state[0] + 1
            if self.state[0] >= self.size[0]:
                self.state[0] = self.size[0] - 1
        elif action == ["left"]:
            self.state[0] = self.state[0] - 1
            if self.state[0] <= 0:
                self.state[0] = 0
        elif action == ["down"]:
            self.state[1] = self.state[1] + 1
            if self.state[1] >= self.size[1]:
                self.state[1] = self.size[1] - 1
        elif action == ["up"]:
            self.state[1] = self.state[1] - 1
            if self.state[1] < 1:
                self.state[1] = 0

        #reward = 0
        reward = self.verify_rewards()
        if tuple(self.state) == self.end:
            self.done = True
            reward = 100
            self.mqttc.publish("states", str(action) + "_" + str(actual_state) + "_" + str(reward) + "_" + "1" + "_" + str(self.state))
            self.state = [0, 0]
            time.sleep(0.1)
            #self.mqttc.publish("done", 1)
            print("mqtt done")
        elif not action == ["reset"]:
            self.mqttc.publish("states", str(action) + "_" + str(actual_state) + "_" + str(reward) + "_" + "0" + "_" + str(self.state))

        print(self.state)

        #return self.verify_rewards()


    def draw(self):
        #clear screen
        self.window.fill((255, 255, 255))

        # dram texts
        for index_x in range(self.size[0]):
            for index_y in range(self.size[1]):
                for index, reward in enumerate(self.rewards):
                    if (index_x, index_y) == reward:
                        reward_color = (0,255,0)
                        pygame.draw.circle(self.window, reward_color, ((index_x * 100) + 50, (index_y * 100) + 50), 20)
                text_surface = self.my_font.render("(" + str(index_x) + "," + str(index_y) + ")", False, (0, 0, 0))
                self.window.blit(text_surface, ((index_x * 100) + 20, (index_y * 100) + 50))
        if self.done:
            text_surface = self.my_font.render("Finished!", False, (0, 0, 0))
            self.window.blit(text_surface, (10,10))

        # draw images
        player_color = (0,0,255)
        pygame.draw.circle(self.window, player_color, [(i * 100) + 50 for i in self.state], 20)


    def verify_rewards(self):
        print("!!!!! VERIFY !!!!!!!!!", self.rewards)
        for index, reward in enumerate(self.rewards):
            if tuple(self.state) == reward:
                print("RECOMPENSANDO 1", self.state, reward)

                #print("reward", 1)

                #print("rew1", self.rewards)
                #del self.rewards[index]
                self.rewards.remove(reward)
                #print("rew2", self.rewards)

                return 1

            print("RECOMPENSANDO -1", self.state, reward)
        #print("reward", -1)
        return -1

        #if self.rewards == []:

            #print("reward", -1)
        #    return -1

    def generate_rewards(self, total = 0):
        if total > 0:
            if total > (self.size[0] * self.size[1]):
                total = total // 3
            self.rewards_table = set([])
            while len(self.rewards_table) < total:
                self.rewards_table.add((random.randrange(0,self.size[0]),random.randrange(0,self.size[1])))
            print("rewards generated", self.rewards_table, "tamanho", len(self.rewards_table), "maximo", total)
        else:
            for item1 in range(self.size[0]):
                for item2 in range(self.size[1]):
                    if item1 + item2 == 5:
                        self.rewards_table.add((item1, item2))

    def start_subprocess(self):
        #mqtt_sub = subprocess.Popen(["C:\Program Files\mosquitto\mosquitto.exe", "-v"])
        #mqtt_sub = subprocess.Popen(["C:\Program Files\mosquitto\mosquitto.exe"])

        try:
            self.mqttc.connect("127.0.0.1", port=1883)
        except:
            self.temMqtt = False
            print("Sem MQTT")

        while self.temMqtt:
            self.mqttc.loop()

        self.mqttc.loop_stop()
        #mqtt_sub.kill()

    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload.decode("utf-8")))
        if msg.topic == "actions":
            self.play([str(msg.payload.decode("utf-8"))])

        elif msg.topic == "done" and msg.payload == b"reset":
            self.state = [0, 0]  # x, y
            #self.rewards = [(0, 1), (0, 2)]
            self.rewards = set([])
            self.rewards = self.rewards_table.copy()
            #self.generate_rewards(total=20)
            self.done = False

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.mqttc.subscribe("actions")
        self.mqttc.subscribe("done")


if __name__ == '__main__':
    game = Grid_game(size=(4,4))
    game.roda_subprocess = False