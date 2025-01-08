import os

import yaml


class FlaskConfig:
    def __init__(self, host, port, debug):
        self.host = host
        self.port = port
        self.debug = debug


class LimiterConfig:
    def __init__(self, namespace, rate, cap):
        self.namespace = namespace
        self.rate = rate
        self.cap = cap


class MySQLConfig:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database


class RedisConfig:
    def __init__(self, host, port, db, password):
        self.host = host
        self.port = port
        self.db = db
        self.password = password


class RabbitMQConfig:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class Conf:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Conf, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'conf.yaml')
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)

        self.flask = FlaskConfig(**config_data['flask'])
        self.limiters = [LimiterConfig(**limiter_config) for limiter_config in config_data['limiters']]
        self.mysql = MySQLConfig(**config_data['database']['mysql'])
        self.redis = RedisConfig(**config_data['database']['redis'])
        self.rabbitmq = RabbitMQConfig(**config_data['messaging']['rabbitmq'])


conf = Conf()
