from message_bus import RabbitMQClient
from aio_pika import Message, connect
import asyncio

RABBITMQ_DEFAULT_USER = "admin"
RABBITMQ_DEFAULT_PASS = "admin"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
EXCHANGE_NAME = "NeurondAssistantMessageBus"
QUEUE_NAME = "TitleSumarize"


# Publisher code
async def main_publisher():
    amqp_url = "amqp://admin:admin@localhost/"
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    await client.send_message("Hello, RabbitMQ!")
    print("[x] Message sent. Waiting for messages. To exit press CTRL+C")
    await client.close()


asyncio.run(main_publisher())
