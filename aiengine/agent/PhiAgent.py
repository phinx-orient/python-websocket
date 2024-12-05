from llama_index.core.llms import ChatMessage
from llama_index.core.tools import ToolSelection, ToolOutput
from llama_index.core.workflow import Event
from typing import Any, List, Union
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools.types import BaseTool
from llama_index.core.workflow import Context, Workflow, StartEvent, StopEvent, step
from llama_index.core.llms.llm import LLM


class InputEvent(Event):
    chat_history: list[ChatMessage]


class ToolCallEvent(Event):
    tool_calls: list[ToolSelection]


class FunctionOutputEvent(Event):
    output: ToolOutput


class ResponseStreamEvent(Event):
    text: str


class ToolStreamEvent(Event):
    text: str


class PhiAgent(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: Union[LLM, None] = None,
        tools: Union[List[BaseTool], None] = None,
        system_prompt: Union[str, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.tools = tools or []
        self.llm = llm
        self.system_prompt = system_prompt
        self.memory = ChatMemoryBuffer.from_defaults(llm=llm)

    @step
    async def prepare_chat_history(self, ev: StartEvent) -> InputEvent:
        user_input = ev.get("input")
        self.memory.put(ChatMessage(role="user", content=user_input))
        chat_history = self.memory.get()
        return InputEvent(chat_history=chat_history)

    @step
    async def handle_llm_input(
        self, ctx: Context, ev: InputEvent
    ) -> Union[ToolCallEvent, StopEvent]:
        context_msg = ChatMessage(role="system", content=self.system_prompt)

        llm_input = [context_msg] + ev.chat_history
        # print(llm_input)
        stream = await self.llm.astream_chat_with_tools(
            self.tools, chat_history=llm_input
        )

        found_answer = False

        async for response in stream:
            # print(response.raw)
            # if the content is the string --> final response
            if isinstance(response.raw.choices[0].delta.content, str):
                found_answer = True
                ctx.write_event_to_stream(ResponseStreamEvent(text=response.delta))

        self.memory.put(response.message)

        tool_calls = self.llm.get_tool_calls_from_response(
            response, error_on_no_tool_call=False
        )
        if not found_answer:
            ctx.write_event_to_stream(ToolCallEvent(tool_calls=tool_calls))
        if not tool_calls:
            return StopEvent(result={"response": response})
        else:
            return ToolCallEvent(tool_calls=tool_calls)

    @step
    async def handle_tool_calls(self, ctx: Context, ev: ToolCallEvent) -> InputEvent:
        self.tools = self.tools

        tool_calls = ev.tool_calls
        tools_by_name = {tool.metadata.get_name(): tool for tool in self.tools}

        tool_msgs = []

        # call tools -- safely!
        for tool_call in tool_calls:
            tool = tools_by_name.get(tool_call.tool_name)
            additional_kwargs = {
                "tool_call_id": tool_call.tool_id,
                "name": tool.metadata.get_name(),
            }
            if not tool:
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Tool {tool_call.tool_name} does not exist",
                        additional_kwargs=additional_kwargs,
                    )
                )
                continue

            try:
                tool_output = tool(**tool_call.tool_kwargs)
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=tool_output.content,
                        additional_kwargs=additional_kwargs,
                    )
                )
            except Exception as e:
                tool_msgs.append(
                    ChatMessage(
                        role="tool",
                        content=f"Encountered error in tool call: {e}",
                        additional_kwargs=additional_kwargs,
                    )
                )

        for msg in tool_msgs:
            self.memory.put(msg)

        chat_history = self.memory.get()
        return InputEvent(chat_history=chat_history)

