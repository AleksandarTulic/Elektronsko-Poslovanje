from Machine import Machine

class StampingMachine(Machine):
    topicListen = [("control-topic", 1), ("finished-topic", 1)];
    topicPublish = "finished-topic-1-2";

    def __init__(self, id):
        super().__init__(id, self.topicListen)

    def run(self):
        super().run(self.topicPublish)

machine = StampingMachine(1)
machine.run()