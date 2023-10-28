from paho.mqtt import client as mqtt_client
from FormattedOutput import formatOut

class MyClient:
    broker = "localhost"
    port = 1883
    topics = [("control-topic", 0), ("finished-topic", 0), ("finished-topic-1-2", 0), ("finished-topic-2-3", 0)]

    def __init__(self):
        formatOut("MyClient created ...")

        self.client = mqtt_client.Client(f"{100}")
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker, self.port)

    def run(self):
        self.subscribe(self.client)
        self.client.loop_forever()

    def subscribe(self, client: mqtt_client):
        client.subscribe(self.topics)
        client.on_message = self.on_message

    def on_message(self, client, userdata, message):
        formatOut(f"Received `{message.payload.decode()}` from `{message.topic}` topic")

        if message.topic.__eq__("finished-topic"):
            self.client.disconnect()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            formatOut("Connected to MQTT Broker!")
        else:
            formatOut("Failed to connect, return code %d\n", rc)

myClient = MyClient()
myClient.run()