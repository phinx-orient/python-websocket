import asyncio
from aio_pika import Message, connect

RABBITMQ_DEFAULT_USER = "admin"
RABBITMQ_DEFAULT_PASS = "admin"
RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
EXCHANGE_NAME = "NeurondAssistantMessageBus"
QUEUE_NAME = "TitleSumarize"


class RabbitMQClient:
    def __init__(self, amqp_url: str, queue_name: str):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self):
        """Establish a connection to the RabbitMQ server and initialize the queue."""
        self.connection = await connect(self.amqp_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)

    async def send_message(self, message_body: str):
        """Send a message to the RabbitMQ queue."""
        message = Message(body=message_body.encode())
        await self.channel.default_exchange.publish(
            message, routing_key=self.queue_name
        )
        print(f"[x] Sent: {message_body}")

    async def consume_messages(self, on_message_callback):
        """Consume messages from the RabbitMQ queue."""
        async with self.queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(f"[x] Received: {message.body.decode()}")
                    await on_message_callback(message.body.decode())

    async def close(self):
        """Close the connection to RabbitMQ."""
        if self.connection:
            await self.connection.close()


async def example_on_message_callback(message_body: str):
    print(f"Processing message: {message_body}")


async def main():
    amqp_url = "amqp://admin:admin@localhost/"
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    await client.send_message("Hello, RabbitMQ!")
    print("[*] Waiting for messages. To exit press CTRL+C")
    await client.consume_messages(example_on_message_callback)
