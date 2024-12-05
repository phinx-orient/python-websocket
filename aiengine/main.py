from agent import agent
from agent.PhiAgent import ResponseStreamEvent, ToolCallEvent
from fastapi import FastAPI
from publisher import rabbitmq_main_publisher
import uvicorn  # Import uvicorn for running the app
import json
app = FastAPI()

@app.post("/streaming")
async def streaming(content: str, conversation_id):
    phi_agent = agent.run_agent()
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
            # send thought_update through rabbitmq
            await rabbitmq_main_publisher(json.dumps(thought_update))

        elif isinstance(ev, ResponseStreamEvent):
            content = ev.text
            full_response += content

    bot_response = {
        "type": "bot_response",
        "role": "assistant",
        "content": full_response,
        "conversationId": conversation_id,  # Include the client ID in the response
    }
    # send bot_response through rabbitmq
    await rabbitmq_main_publisher(json.dumps(bot_response))
    return {"message": "Success"}

if __name__ == "__main__":  # Add this block to run the app
    uvicorn.run(app, host="0.0.0.0", port=8007)  # Run the FastAPI app
