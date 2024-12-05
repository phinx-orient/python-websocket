from rabbitmq_client import RabbitMQClient, QUEUE_NAME, AMQP_URL
import asyncio


# Consumer code
async def example_on_message_callback(message_body: str):
    print(f"Processing message: {message_body}")


async def main_consumer():
    amqp_url = AMQP_URL
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    print("[*] Waiting for messages. To exit press CTRL+C")
    await client.consume_messages(example_on_message_callback)


# Run only the consumer
if __name__ == "__main__":
    asyncio.run(main_consumer())
