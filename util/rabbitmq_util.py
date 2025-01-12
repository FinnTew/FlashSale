import pika
import logging
from conf.conf import conf

class RabbitMQUtil:
    def __init__(self,
                 host: str =  conf.rabbitmq.host,
                 port: int = conf.rabbitmq.port,
                 user: str = conf.rabbitmq.user,
                 password: str = conf.rabbitmq.password,
                 ):
        self.conn = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=host,
                port=port,
                credentials=pika.PlainCredentials(user, password)
            )
        )
        self.channel = self.conn.channel()
        self.logger = logging.getLogger(__name__)

    def publish_message(self, queue_name, message, exchange=''):
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_publish(exchange=exchange, routing_key=queue_name, body=message)
        self.logger.info(f"Published message to queue '{queue_name}': {message}")

    def consume_message(self, queue_name, callback, auto_ack=True):
        self.channel.queue_declare(queue=queue_name)
        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=auto_ack)
        self.logger.info(f"Started consuming messages from queue '{queue_name}'")
        self.channel.start_consuming()

    def close(self):
        self.conn.close()
        self.logger.info("RabbitMQ connection closed.")
