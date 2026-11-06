class Event:
    def __init__(self, text="", raw_text="", command="", user_id="10000", group_id="20000"):
        self.text = text
        self.raw_text = raw_text
        self.command = command
        self.user_id = user_id
        self.group_id = group_id
        self.bot_id = "bot"
