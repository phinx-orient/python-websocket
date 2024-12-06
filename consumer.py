from message_bus import RabbitMQClient
import asyncio
from aio_pika import Message, connect

RABBITMQ_DEFAULT_USER = "admin"
RABBITMQ_DEFAULT_PASS = "admin"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
EXCHANGE_NAME = "NeurondAssistantMessageBus"
QUEUE_NAME = "TitleSumarize"


# Consumer code
async def example_on_message_callback(message_body: str):
    print(f"Processing message: {message_body}")


async def main_consumer():
    amqp_url = "amqp://admin:admin@localhost/"
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    print("[*] Waiting for messages. To exit press CTRL+C")
    await client.consume_messages(example_on_message_callback)


# Run both publisher and consumer
async def main():
    await asyncio.gather(main_consumer())


asyncio.run(main())
