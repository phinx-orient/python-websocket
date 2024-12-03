from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import json
from agent import agent
from agent.PhiAgent import ResponseStreamEvent, ToolCallEvent, ToolStreamEvent

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

    try:
        while True:
            phi_agent = agent.run_agent()
            data = await websocket.receive_text()
            response_data = json.loads(data)
            if response_data.get("type") == "bot_response":
                conversation_id = response_data.get("conversationId")
                content = response_data.get("content")
                print(
                    f"Received bot response for conversation {conversation_id}: {content}"
                )
            print(f"Received message from client {conversation_id}: {data}")
            full_response = ""
            # Simulate a thought update and bot response
            async for ev in agent.stream_chat_gen(phi_agent, content):
                # Agent thought
                if isinstance(ev, ToolCallEvent):
                    content_list = [
                        {
                            "tool_name": tool_call.tool_name,
                            "tool_kwargs": tool_call.tool_kwargs,
                        }
                        for tool_call in ev.tool_calls
                    ]
                    thought_update = {
                        "type": "thought_update",
                        "role": "assistant",
                        "content": str(content_list),
                        "conversationId": conversation_id,
                    }
                    await websocket.send_text(json.dumps(thought_update))

                elif isinstance(ev, ResponseStreamEvent):
                    content = ev.text
                    full_response += content

            bot_response = {
                "type": "bot_response",
                "role": "assistant",
                "content": full_response,
                "conversationId": conversation_id,  # Include the client ID in the response
            }
            await websocket.send_text(json.dumps(bot_response))
            # Reset agent
            # phi_agent.memory.reset()

    except (WebSocketDisconnect, KeyboardInterrupt):
        manager.disconnect(conversation_id)
        print(f"Client {conversation_id} disconnected.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
