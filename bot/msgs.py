import yaml


class MessageTemplates:
    """
    Message template class that allows dot access notation to the templates.
    """

    def __init__(self):
        with open("messages.yaml") as f:
            self.yaml = yaml.safe_load(f)

    def __getattr__(self, name: str):
        return self.yaml[name]


templates = MessageTemplates()
