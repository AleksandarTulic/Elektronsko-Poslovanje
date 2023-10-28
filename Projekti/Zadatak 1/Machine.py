from paho.mqtt import client as mqtt
from threading import Thread
from FormattedOutput import formatOut
import time

class Machine:
    broker = "localhost"
    port = 1883
    FIRST_MACHINE = 1
    LAST_MACHINE = 3

    def __init__(self, id, topicListen):
        self.id = id ### with this id , the machine knows if the values published by Main.py are intended for it
        self.message = "" ### what message is the machine outputting
        self.wait = 0.0 ### how long does the operation take
        self.number = 1000000.0 ### how many elements does the machines need to create(i give a default value if something goes wrong)
        self.flag = False ### should the machines work(or continue to work)
        self.topicListen = topicListen ### on what topics should my machine listen(for more look direct machine examples)
        self.numberOfMaterialAvailable = 0 ### how many elements can i create(if this is not the first machines than i depend on the previous machine and need to wait until it finishes it's work)

        self.client = mqtt.Client(f"{id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.sub = Thread(target=self.listening, args=()) ### create a thread that will always listen for messages from publisher
        self.sub.start()

    def __str__(self):
        return f"ID: {self.id}, Message: {self.message}, Working: {self.wait}, Number: {self.number}"

    ####################################################
    ############## Broker Communication ################
    ####################################################

    def listening(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_forever()

    def on_message(self, client, userdata, message):
        formatOut(f"Received `{message.payload.decode()}` from `{message.topic}` topic")
        
        if message.topic.__eq__("control-topic"):
            if message.payload.decode().split("#")[0].__eq__("RUN_TIME"):
                if int(message.payload.decode().split("#")[1]) == self.id:
                    self.wait = float(message.payload.decode().split("#")[2])
                    formatOut(self.__str__())
            elif message.payload.decode().split("#")[0].__eq__("MESSAGE"):
                if int(message.payload.decode().split("#")[1]) == self.id:
                    self.message = message.payload.decode().split("#")[2]
                    formatOut(self.__str__())
            elif message.payload.decode().split("#")[0].__eq__("STOP"):
                if message.payload.decode().split("#")[1].__eq__("ALL") or int(message.payload.decode().split("#")[1]) == self.id:
                    self.flag = False
                    formatOut(f"ID: {self.id} stopped working ...")
            elif message.payload.decode().split("#")[0].__eq__("START"):
                if message.payload.decode().split("#")[1].__eq__("ALL") or int(message.payload.decode().split("#")[1]) == self.id:
                    self.flag = True
                    formatOut(f"ID: {self.id} started working ...")
            elif message.payload.decode().split("#")[0].__eq__("NUMBER_OF_PRODUCTS"):
                self.number = int(message.payload.decode().split("#")[1])

                if self.id == self.FIRST_MACHINE:
                    self.numberOfMaterialAvailable = self.number
        elif message.topic.__eq__("finished-topic"):
            formatOut(f"Stopping machine with ID = {self.id} ...")
            self.stop()
        else:
            self.numberOfMaterialAvailable = int(message.payload.decode())

        if message.payload.decode().__eq__("quit"):
            formatOut(f"Stopping machine with ID = {self.id} ...")
            self.stop()
    
    def on_connect(self, client, userdata, flags, rc):
        formatOut("connected")
        self.subscribe(self.topicListen)

    def subscribe(self, topic):
        self.client.subscribe(topic)

    ### run(), meaning = publish
    def run(self, topic):
        formatOut(f"Machined with ID = {self.id} started working ...")
        num = 0;
        while num < self.number:
            if self.flag and self.numberOfMaterialAvailable > 0:
                formatOut(f"{self.message}")
                if self.id != self.LAST_MACHINE: ### if this is not the last machine publish that you have finished you part and then tell that to the next machine
                    self.client.publish(topic, f"{num + 1}")
                time.sleep(self.wait) ### waiting for the product to be fininshed
                num += 1 ### number of products that this instance of machines has created is increased by one
            else:
                time.sleep(0.100) ### check every 0.1s if the state has changed
        
        ### when i get info that the last machine finished, i don't need to work anymore
        if self.id == self.LAST_MACHINE:
            self.client.publish(topic, "Finished product(or products)")
            self.client.disconnect()
    
    def stop(self):
        self.client.disconnect()