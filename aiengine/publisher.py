from rabbitmq_client import RabbitMQClient, QUEUE_NAME, AMQP_URL
import asyncio


# Publisher code
async def main_publisher():
    amqp_url = AMQP_URL
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    await client.send_message("toi la chien!")
    print("[x] Message sent.")
    await client.close()


# Run the publisher
if __name__ == "__main__":
    asyncio.run(main_publisher())
