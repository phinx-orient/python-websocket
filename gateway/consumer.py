from rabbitmq_client import RabbitMQClient, QUEUE_NAME, AMQP_URL
import asyncio
from fastapi import WebSocket


async def on_message_callback(websocket: WebSocket, message: str):
    print("Sending message to WebSocket:", message)  # Log the message being sent
    await websocket.send_text(message)


async def rabbitmq_main_consumer(websocket: WebSocket):
    amqp_url = AMQP_URL
    queue_name = QUEUE_NAME 

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    print("[*] Waiting for messages. To exit press CTRL+C")
    await client.consume_messages(lambda msg: on_message_callback(websocket, msg))


# Run only the consumer
if __name__ == "__main__":
    asyncio.run(rabbitmq_main_consumer())
