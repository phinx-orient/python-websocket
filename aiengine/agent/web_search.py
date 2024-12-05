from bs4 import BeautifulSoup
from time import sleep
from typing import List
import requests
from typing import Union
from .get_llm import get_llm_azure
from llama_index.program.openai import OpenAIPydanticProgram
from .schema import SearchTranslatedQueries
from .ai_config_schema import PROMPT, QUESTION_GEN_TEMPLATE
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.core import QueryBundle
from llama_index.core.tools import ToolMetadata
from llama_index.core.tools import FunctionTool
import datetime
from asyncer import asyncify

def get_page_content(input: str) -> str:
    html = requests.get(input).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(strip=True, separator="\n")


def get_search_results(input: str, freshness: Union[str, None] = None) -> List:
    """
    Fetches search results from Brave's search API based on the input query and freshness parameter.
    """
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": "BSA2RsJ9dtiGZPslnwzU2CClAn9FvWb",
    }
    response = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        params={
            "q": input,
            "count": 3,  # 2 generated queries ==> 4 in total, 3 --> 6 in totial. etc
            "country": "ALL",  # Max number of results to return
            "freshness": freshness,
        },
        headers=headers,
        timeout=10,
    )
    if not response.ok:
        raise Exception(f"HTTP error {response.status_code}")
    sleep(1)  # avoid Brave rate limit
    return response.json()


def generate_queries_search_engine(query_str: str) -> list:
    llm = get_llm_azure()
    # prompt = PROMPT["search_query_gen"]["template"]
    # output = llm.complete(prompt.format(USER_QUESTION=query_str))
    # return output.text
    program = OpenAIPydanticProgram.from_defaults(
        output_cls=SearchTranslatedQueries,
        prompt_template_str=PROMPT["search_query_gen"]["template"],
        verbose=False,
        llm=llm,
    )
    output = program(user_question=query_str)
    return output.Output


def decompose_queries_search_engine(query_str: str) -> list:
    llm = get_llm_azure()
    question_gen = LLMQuestionGenerator.from_defaults(
        llm=llm, prompt_template_str=QUESTION_GEN_TEMPLATE
    )

    tool_choices = [
        ToolMetadata(
            name="web_search_tool",
            description=(
                f"Used to retrieve information about up-to-date information, website or the information out of LLM's knowledge, arg input is 'query'"
            ),
        ),
        ToolMetadata(
            name="web_fetch_tool",
            description=(f"Used to fetch information of specific url"),
        ),
    ]

    choices = question_gen.generate(tool_choices, QueryBundle(query_str=query_str))
    sub_questions = [choice.sub_question for choice in choices]

    return sub_questions


def process_search_results(input: str):
    """
    Processes search results based on the input query string.

    This function decomposes the input query into sub-questions, retrieves search results for each sub-question,
    and compiles a list of URLs along with their frequency of occurrence, age, and description.

    Args:
        input (str): The input query string to be processed.

    Returns:
        list: A sorted list of dictionaries containing URLs, each with its frequency of occurrence.
    """
    # queries = generate_queries_search_engine(input)
    # queries = decompose_queries_search_engine(input)
    queries = [input]
    print("sub question:", queries)
    # queries = [input]
    url_frequency = {}
    url_age = {}
    url_description = {}
    for query in queries:
        search_results = get_search_results(query)

        # Debugging: Print the search_results to understand its structure
        # print(f"Search results for query '{query}': {search_results}")

        if isinstance(search_results, dict):
            results_list = search_results.get("web", {}).get("results", [])

            if isinstance(results_list, list):
                # Collect URLs, their frequencies, and ages
                for result in results_list:
                    url = result.get("url")
                    age = result.get("age")  # Get the date posted in the internet
                    description = result.get("description")
                    if url:
                        url_frequency[url] = url_frequency.get(url, 0) + 1
                        url_age[url] = age  # Store the age for the URL
                        url_description[url] = description
    # Create a list of dictionaries with URL, frequency, and age
    url_list = [
        {
            "url": url,
            "description": url_description[url],
            "age": url_age[url],
            "frequency": url_frequency[url],
        }
        for url, freq in url_frequency.items()
    ]

    # Sort the list by frequency (high to low)
    sorted_url_list = sorted(url_list, key=lambda item: item["frequency"], reverse=True)
    return [{key: url_list[key] for key in ["url"]} for url_list in sorted_url_list]


web_search_tool = FunctionTool.from_defaults(
    fn=process_search_results,
    name="web_search_tool",
    description=(
        f"Used to retrieve information about up-to-date information in {str(datetime.datetime.now().date())}, \
            website or the information out of LLM's knowledge."
    ),
)

web_fetch_tool = FunctionTool.from_defaults(
    fn=get_page_content,
    name="web_fetch_tool",
    description="Used to fetch information of specific url",
)

web_tools = [web_fetch_tool, web_search_tool]
