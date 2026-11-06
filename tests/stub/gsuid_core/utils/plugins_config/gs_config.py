class StringConfig:
    _instances = {}

    def __init__(self, config_name, CONFIG_PATH, config_list):
        self.config_name = config_name
        self.CONFIG_PATH = CONFIG_PATH
        self.config = dict(config_list)
        StringConfig._instances[config_name] = self

    def get_config(self, key):
        return self.config[key]

    def set_config(self, key, value):
        self.config[key].data = value
        return True
