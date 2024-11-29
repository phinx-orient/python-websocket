from fastapi import FastAPI, Request, BackgroundTasks
from sse_starlette.sse import EventSourceResponse
from typing import Dict, Any, AsyncGenerator, Literal, Union
import json
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


app = FastAPI()

# CORS Middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Queue to store messages for streaming
message_queue = asyncio.Queue()


class ToolData(BaseModel):
    input: str
    tool_name: str


class BaseData(BaseModel):
    conversation_id: str


# Define a concise schema for message data
class ReasoningData(BaseData):
    response: ToolData  # Optional for final response


# Define the schema for reasoning messages
class ReasoningMessage(BaseModel):
    type: Literal["reasoning"]
    data: ReasoningData


class FinalData(BaseData):
    response: str


# Define the schema for final response messages
class FinalResponseMessage(BaseModel):
    type: Literal["final_response"]
    data: FinalData


# Stream messages from the queue
async def stream_messages() -> AsyncGenerator[Dict[str, Any], None]:
    while True:
        # Wait for the next message in the queue
        message = await message_queue.get()
        yield message


@app.get("/stream")
async def stream_sse(request: Request):
    async def event_generator():
        async for message in stream_messages():
            # Check for client disconnection
            if await request.is_disconnected():
                break

            # Send the message as JSON data in SSE format
            yield f"{json.dumps(message)}\n\n"

    return EventSourceResponse(event_generator())


# Update the add_message function to use the schemas
@app.post("/add_message")
async def add_message(message_data: Union[ReasoningMessage, FinalResponseMessage]):
    """
    Endpoint to add a message to the queue.
    This simulates an external trigger to add reasoning steps or final responses.
    """
    # Check the type of message and ensure it is valid
    if message_data.type not in ["reasoning", "final_response"]:
        return {
            "status": "Invalid message type. Must be 'reasoning' or 'final_response'."
        }

    # Additional validation for reasoning data
    if message_data.type == "reasoning":
        if "conversation_id" not in message_data.data:
            return {"status": "Invalid reasoning data. 'conversation_id' is required."}

    # Additional validation for final response data
    if message_data.type == "final_response":
        if "response" not in message_data.data:
            return {"status": "Invalid final response data. 'response' is required."}

    await message_queue.put(message_data.model_dump())
    return {"status": "Message added to the stream"}


@app.post("/add_reasoning")
async def add_reasoning(reasoning_data: ReasoningMessage):
    """
    Endpoint to add a reasoning message to the queue.
    """

    await message_queue.put(reasoning_data.model_dump())
    return {"status": "Reasoning message added to the stream"}


@app.post("/add_final_response")
async def add_final_response(final_response_data: FinalResponseMessage):
    """
    Endpoint to add a final response message to the queue.
    """

    await message_queue.put(final_response_data.model_dump())
    return {"status": "Final response message added to the stream"}


# Example usage to simulate adding messages manually
@app.get("/trigger_streaming")
async def trigger_streaming(background_tasks: BackgroundTasks):
    """
    Simulates a series of events, adding messages to the queue manually.
    """

    async def add_messages():
        # Simulate adding reasoning steps
        for i in range(3):
            reasoning_log = {
                "type": "reasoning",
                "data": {
                    "conversation_id": "example_convo_id",
                    "response": {
                        "input": f"Step {i + 1} input data",
                        "tool_name": f"Tool_{i + 1}",
                    },
                },
            }
            await message_queue.put(reasoning_log)
            await asyncio.sleep(1)  # Simulate a delay between steps

        # Final response
        final_response = {
            "type": "final_response",
            "data": {
                "conversation_id": "example_convo_id",
                "response": "This is the final response.",
            },
        }
        await message_queue.put(final_response)

    background_tasks.add_task(add_messages)
    return {"status": "Streaming triggered"}


# Example usage to simulate adding messages manually
@app.get("/mock_trigger_streaming")
async def mock_trigger_streaming(background_tasks: BackgroundTasks):
    """
    Simulates adding messages from different conversation IDs to the queue simultaneously.
    """

    async def add_messages(conversation_id: str):
        # Simulate adding reasoning steps for a specific conversation ID
        for i in range(3):
            reasoning_log = {
                "type": "reasoning",
                "data": {
                    "conversation_id": conversation_id,
                    "response": {
                        "input": f"Step {i + 1} input data for {conversation_id}",
                        "tool_name": f"Tool_{i + 1}",
                    },
                },
            }
            await message_queue.put(reasoning_log)
            await asyncio.sleep(1)  # Simulate a delay between steps

        # Final response for the specific conversation ID
        final_response = {
            "type": "final_response",
            "data": {
                "conversation_id": conversation_id,
                "response": f"This is the final response for {conversation_id}.",
            },
        }
        await message_queue.put(final_response)

    # Start tasks for different conversation IDs
    conversation_ids = [
        "example_convo_id_1",
        "example_convo_id_2",
        "example_convo_id_3",
    ]
    background_tasks.add_task(
        asyncio.gather(*(add_messages(cid) for cid in conversation_ids))
    )

    return {"status": "Mock streaming triggered for multiple conversation IDs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8100, reload=True)
