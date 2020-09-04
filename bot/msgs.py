import yaml

class MessageTemplates():
    def __init__(self):
        with open("bot/messages.yaml") as f:
            self.yaml = yaml.load(f)
    def __getattr__(self, name: str):
        return self.yaml[name]


templates = MessageTemplates()
