from rabbitmq_client import RabbitMQClient, QUEUE_NAME, AMQP_URL
import asyncio
from fastapi import WebSocket
from starlette.websockets import WebSocketState
import json
import ast


# async def on_message_callback(websocket: WebSocket, message_body: str):
#     print("Received new message:", message_body)  # Log the received message

#     try:
#         # Attempt to fix the content field if it contains single quotes
#         # message_body = message_body.replace(
#         #     "'", '"'
#         # )  # Replace single quotes with double quotes

#         # # Escape double quotes in the content field
#         # message_body = message_body.replace('"', '\\"')  # Escape double quotes

#         # # Escape apostrophes to avoid issues
#         # message_body = message_body.replace("'", "\\'")  # Escape apostrophes

#         # Parse the message body as JSON
#         message_json = ast.literal_eval(message_body)

#         # Check if the message type is 'thought_update' or 'bot_response' and send as JSON
#         if message_json.get("type") in ["thought_update", "bot_response"]:
#             if (
#                 websocket.client_state == WebSocketState.CONNECTED
#             ):  # Check if the websocket is still connected
#                 print(
#                     "Sending message to WebSocket:", message_json
#                 )  # Log the message being sent
#                 await websocket.send_text(json.dumps(message_json))
#     except json.JSONDecodeError:
#         print(
#             "Failed to decode JSON:", message_body
#         )  # Log the error if JSON decoding fails
#         if (
#             websocket.client_state == WebSocketState.CONNECTED
#         ):  # Check if the websocket is still connected
#             await websocket.send_text(message_body)


async def on_message_callback(websocket: WebSocket, message: str):
    print("Sending message to WebSocket:", message)  # Log the message being sent
    await websocket.send_text(message)


async def rabbitmq_main_consumer(websocket: WebSocket):
    amqp_url = AMQP_URL
    queue_name = QUEUE_NAME  # Replace QUEUE_NAME with an actual queue name

    client = RabbitMQClient(amqp_url, queue_name)

    await client.connect()
    print("[*] Waiting for messages. To exit press CTRL+C")
    await client.consume_messages(lambda msg: on_message_callback(websocket, msg))


# Run only the consumer
if __name__ == "__main__":
    asyncio.run(rabbitmq_main_consumer())
