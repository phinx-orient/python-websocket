from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import pika
import asyncio


def rabbitmq_callback(ch, method, properties, body):
    message = body.decode()
    # Send the message to all connected WebSocket clients
    for client in clients:
        asyncio.run(client.send_text(message))


def start_rabbitmq_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    channel.basic_consume(
        queue=QUEUE_NAME, on_message_callback=rabbitmq_callback, auto_ack=True
    )

    print("Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


@asynccontextmanager
async def lifespan():
    # Start the RabbitMQ consumer in a separate thread
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, start_rabbitmq_consumer)
    yield
    # After handling request, we can do something like cleaning up memory if necessary


app = FastAPI(lifespan=lifespan)

# RabbitMQ connection parameters
RABBITMQ_HOST = "localhost"
QUEUE_NAME = "your_queue_name"

# Store connected WebSocket clients
clients = []


@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            # Keep the connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)
        print("Client disconnected")
