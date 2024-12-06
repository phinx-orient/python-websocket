from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from consumer import rabbitmq_main_consumer
import asyncio

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[
            str, WebSocket
        ] = {}  # Store connections with client IDs

    async def connect(self, websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        self.active_connections[conversation_id] = websocket

    def disconnect(self, conversation_id: str):
        if conversation_id in self.active_connections:
            del self.active_connections[conversation_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, sender_id: str):
        for conversation_id, connection in self.active_connections.items():
            if (
                conversation_id != sender_id
            ):  # Don't send the message back to the sender
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    # Now that we have a valid conversation_id, connect the WebSocket
    await manager.connect(websocket, conversation_id)
    # Start the RabbitMQ consumer in the background using asyncio.Future
    future = asyncio.ensure_future(rabbitmq_main_consumer(websocket))
    try:
        while True:
            data = await websocket.receive_text()
            print("receive from frontend:", data)
    except (WebSocketDisconnect, KeyboardInterrupt):
        manager.disconnect(conversation_id)
        print(f"Client {conversation_id} disconnected.")
        future.cancel()  # Cancel the future if the connection is closed


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8081)
