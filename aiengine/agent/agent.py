# Standard library imports
from .PhiAgent import PhiAgent
import datetime
from typing import List, Optional
from .system_prompt import DEFAULT_SYSTEM_PROMPT
from .web_search import web_tools
from .PhiAgent import ResponseStreamEvent, ToolCallEvent
from .get_llm import get_llm_azure
from dotenv import load_dotenv

load_dotenv()

DEFAULT_SYSTEM_PROMPT_WITH_TIME = DEFAULT_SYSTEM_PROMPT.format(
    date=str(datetime.datetime.now().date())
)


DEFAULT_SYSTEM_PROMPT_WITH_TIME = DEFAULT_SYSTEM_PROMPT.format(
    date=str(datetime.datetime.now().date())
)
model_name = "gpt-4o-mini"


def run_agent(
    model_name: str = "gpt-4o-mini",
    system_prompt: str = DEFAULT_SYSTEM_PROMPT_WITH_TIME,
    tools: Optional[List] = web_tools,
    history: Optional[List] = None,
):
    if model_name in ["gpt-4o-mini", "gpt-4-turbo", "gpt-4"]:
        agent = PhiAgent(
            tools=tools,
            system_prompt=system_prompt,
            # chat_history=history,
            llm=get_llm_azure(),
            verbose=False,
            timeout=60,
        )

    return agent


# agent.reset()
agent = run_agent(
    model_name=model_name,
    system_prompt=DEFAULT_SYSTEM_PROMPT_WITH_TIME,
    tools=web_tools,
    history=None,
)


async def stream_chat_gen(agent, input):
    handler = agent.run(input=input, timeout=60)
    async for ev in handler.stream_events():
        if isinstance(ev, ToolCallEvent):
            print("#Reasoning:")
            yield (ev)
        elif isinstance(ev, ResponseStreamEvent):
            yield (ev)
