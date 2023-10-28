from Machine import Machine

class AssemblyMachine(Machine):
    topicListen = [("control-topic", 1), ("finished-topic-2-3", 1)];
    topicPublish = "finished-topic";
    
    def __init__(self, id):
        super().__init__(id, self.topicListen)

    def run(self):
        super().run(self.topicPublish)

machine = AssemblyMachine(3)
machine.run()