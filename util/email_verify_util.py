import random
import time

import pika

from util.rabbitmq_util import RabbitMQUtil
from util.redis_util import RedisUtil
import smtplib
from email.mime.text import MIMEText
from conf.conf import conf

class EmailVerifyUtil:
    def __init__(self):
        self.redis = RedisUtil()
        self.rabbitmq = RabbitMQUtil()

    def _get_redis_key(self, email: str) -> str:
        return f"email_verify_code:{email}"

    def _send_email(self, recipient_email: str, verify_code: str):
        msg = MIMEText(f'Please use the following code to reset your password: {verify_code}', 'plain', 'utf-8')
        msg['Subject'] = 'Password Reset Verification Code'
        msg['From'] = conf.email.username
        msg['To'] = recipient_email

        try:
            with smtplib.SMTP(
                    host=conf.email.host,
                    port=conf.email.port,
            ) as smtp:
                if conf.email.use_tls:
                    smtp.starttls()
                if conf.email.username != '' and conf.email.password != '':
                    smtp.login(conf.email.username, conf.email.password)
                smtp.send_message(msg)
        except Exception as e:
            pass
        finally:
            pass

        self.redis.set(self._get_redis_key(recipient_email), verify_code, expire=300)

    def send_verify_code(self, recipient_email: str):
        verify_code = str(random.uniform(0, 1))[2:8]
        self.rabbitmq.publish_message(
            queue_name='email_verify_queue',
            message=f'{recipient_email}::{verify_code}'
        )

    def verify(self, recipient_email: str, code: str) -> bool:
        saved_code = self.redis.get(self._get_redis_key(recipient_email))
        if saved_code is None:
            return False
        if code == saved_code:
            self.redis.delete(self._get_redis_key(recipient_email))
            return True

    def email_consumer(self):
        def callback(ch, method, properties, body):
            recipient_email, verify_code = body.decode().split('::')
            self._send_email(recipient_email, verify_code)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.rabbitmq.consume_message(
            queue_name='email_verify_queue',
            callback=callback,
            auto_ack=False
        )


