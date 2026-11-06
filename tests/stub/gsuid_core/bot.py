class Bot:
    def __init__(self, sends=None):
        self.sends = sends if sends is not None else []

    async def send(self, message):
        self.sends.append(message)
        return message
