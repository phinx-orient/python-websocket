from llama_index.core.tools import FunctionTool
from bs4 import BeautifulSoup
from typing import Dict, List, Union
from loguru import logger
import asyncio
import aiohttp
import requests


async def process_search_results(input: str):
    """
    Processes a list of search queries to collect URLs, their frequencies, descriptions, and ages from search results.

    Note:
    - This function must be invoked **only once** per query. It fetches search results,
    Parameters:
    input (str): The query to process.

    Returns:
    List[str]: A list of string with containing urls from brave search engine.
    """
    logger.info("Before generate")
    logger.info("Use Web")
    queries = [input]
    logger.info(f"English question: {queries}")
    print("Queries:", queries)
    logger.info("After generate")
    url_frequency = {}
    url_age = {}
    url_description = {}
    logger.info("Before get_search_results")
    for query in queries:
        search_results = await async_get_search_results(query)

        if isinstance(search_results, dict):
            results_list = search_results.get("web", {}).get("results", [])

            if isinstance(results_list, list):
                for result in results_list:
                    url = result.get("url")
                    age = result.get("age")
                    description = result.get("description")
                    if url:
                        url_frequency[url] = url_frequency.get(url, 0) + 1
                        url_age[url] = age
                        url_description[url] = description

    url_list = [
        {
            "url": url,
            "description": url_description[url],
            "age": url_age[url],
            "frequency": url_frequency[url],
        }
        for url in url_frequency
    ]

    sorted_url_list = sorted(url_list, key=lambda item: item["frequency"], reverse=True)
    return [url_list[key] for key in ["url"] for url_list in sorted_url_list]


async def async_get_search_results(
    input: str, freshness: Union[str, None] = None
) -> List:
    """
    Fetches search results from Brave's search API based on the input query and freshness parameter.

    Note: This function must only be called **only once** per question to avoid exceeding rate limits.

    Parameters:
    input (str): The search query.
    freshness (Optional[str]): Optional freshness parameter for filtering results.

    Returns:
    List: JSON response containing search results.

    Raises:
    HTTPStatusError: If the API request fails
    """
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": "BSA2RsJ9dtiGZPslnwzU2CClAn9FvWb",  # Insert valid API token
    }
    params: Dict[str, str] = {}

    if input:
        params["q"] = str(input)
    params["count"] = "3"
    params["country"] = "ALL"

    if freshness:
        params["freshness"] = str(freshness)

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                "https://api.search.brave.com/res/v1/web/search",
                params=params,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise aiohttp.ClientResponseError(
                        response.request_info,
                        response.history,
                        status=response.status,
                        message=f"HTTP error {response.status}: {error_text}",
                    )

                await asyncio.sleep(0.5)

                return await response.json()

        except aiohttp.ClientError as e:
            raise
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            raise


def get_page_content(input: str) -> str:
    """
    Fetches and extracts the main content from a webpage.

    Note: This function must be used **only once** per URL to minimize redundant requests.

    Parameters:
    input (str): The URL to fetch.

    Returns:
    str: Extracted text content of the webpage.
    """
    html = requests.get(input).text
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(strip=True, separator="\n")


async def fetch(session, url, timeout=8):
    async with session.get(url, timeout=timeout) as response:
        return await response.text()


def parse(html):
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(strip=True, separator="\n")


async def fetch_and_parse(session, url):
    logger.info(f"Fetch url: {url}")
    try:
        html = await fetch(session, url)
        paras = parse(html)
        return paras
    except Exception as e:
        return f"Can not fetch the {url}"


async def async_get_page_content(url):
    """
    Fetches and extracts the main content from a webpage asynchronously.

    Note: This function must be used **only once** if you found enough information.

    Parameters:
    url (str): The URL to fetch.

    Returns:
    str: Extracted text content of the webpage.
    """
    async with aiohttp.ClientSession() as session:
        return await fetch_and_parse(session, url)


# Configure tools
web_search_tool = FunctionTool.from_defaults(async_fn=process_search_results)

web_fetch_tool = FunctionTool.from_defaults(async_fn=async_get_page_content)

web_tools = [web_fetch_tool, web_search_tool]
