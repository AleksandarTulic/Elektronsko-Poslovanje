from Machine import Machine

class BodyshopMachine(Machine):
    topicListen = [("control-topic", 1), ("finished-topic", 1), ("finished-topic-1-2", 1)];
    topicPublish = "finished-topic-2-3";

    def __init__(self, id):
        super().__init__(id, self.topicListen)

    def run(self):
        super().run(self.topicPublish)

machine = BodyshopMachine(2)
machine.run()