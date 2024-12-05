import os
from dotenv import load_dotenv

import tiktoken

from llama_index.agent.openai import OpenAIAgent
from llama_index.core.agent import ReActAgent
from llama_index.core.callbacks import CallbackManager
from llama_index.core.callbacks import TokenCountingHandler
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.llms.gemini import Gemini
from llama_index.llms.openai import OpenAI
from llama_index.multi_modal_llms.openai import OpenAIMultiModal

from .ai_config_schema import EMBEDDING
from .ai_config_schema import LLM

load_dotenv()

token_counter = TokenCountingHandler(
    tokenizer=tiktoken.get_encoding("cl100k_base").encode
)

callback_manager = CallbackManager([token_counter])


# Get llm with Azure Open AI api
def get_llm_azure():
    llm = AzureOpenAI(
        engine="gpt-4o-mini",
        model="gpt-4o-mini",
        temperature=0.0,
        callback_manager=callback_manager,
        max_tokens=4096,
    )
    return llm


# def get_llm(model_name: str):
#     if model_name in ["gpt-4o-mini", "gpt-4-turbo", "gpt-4"]:
#         llm = OpenAI(
#             model=LLM[model_name]["model"],
#             temperature=0,
#             max_tokens=LLM[model_name]["max_tokens"],
#             callback_manager=callback_manager,
#         )
#     elif model_name in ["gemini-pro", "gemini-flash"]:
#         llm = Gemini(
#             model_name=LLM[model_name]["model"],
#             max_tokens=LLM[model_name]["max_tokens"],
#             callback_manager=callback_manager,
#         )
#     elif model_name in ["claude-pro", "claude-fast", "claude-medium"]:
#         llm = Anthropic(
#             model=LLM[model_name]["model"],
#             max_tokens=LLM[model_name]["max_tokens"],
#             callback_manager=callback_manager,
#         )

#     return llm
