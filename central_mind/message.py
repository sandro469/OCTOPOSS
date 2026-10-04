class MindMessage:
    def __init__(self, tentacle, action, status, result):
        self.tentacle = tentacle
        self.action = action
        self.status = status
        self.result = result

    def to_dict(self):
        return {
            "tentacle": self.tentacle,
            "action": self.action,
            "status": self.status,
            "result": self.result
        }
