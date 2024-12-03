LLM = {
    "gpt-3.5-turbo": {
        "model": "gpt-3.5-turbo",
        "price_in": 0.001,
        "price_out": 0.002,
        "max_tokens": 2048,
    },
    "gpt-4-turbo": {
        "model": "gpt-4o-2024-08-06",
        "price_in": 0.005,
        "price_out": 0.015,
        "max_tokens": 16384,
    },
    "gpt-4o-mini": {
        "model": "gpt-4o-mini",
        "price_in": 0.00015,
        "price_out": 0.0006,
        "max_tokens": 16384,
    },
    "gpt-4": {
        "model": "gpt-4",
        "price_in": 0.03,
        "price_out": 0.06,
        "max_tokens": 2048,
    },
    "gemini-pro": {
        "model": "models/gemini-1.5-pro-latest",
        "price_in": 0.00175,
        "price_out": 0.0105,
        "max_tokens": 8192,
    },
    "gemini-flash": {
        "model": "models/gemini-1.5-flash-latest",
        "price_in": 0.00035,
        "price_out": 0.00105,
        "max_tokens": 8192,
    },
    "claude-pro": {
        "model": "claude-3-opus-20240229",
        "price_in": 0.015,
        "price_out": 0.075,
        "max_tokens": 4096,
    },
    "claude-fast": {
        "model": "claude-3-haiku-20240307",
        "price_in": 0.00025,
        "price_out": 0.00125,
        "max_tokens": 4096,
    },
    "claude-medium": {
        "model": "claude-3-5-sonnet-20240620",
        "price_in": 0.003,
        "price_out": 0.015,
        "max_tokens": 8192,
    },
}

EMBEDDING = {
    "embedv3-small": {"model": "text-embedding-3-small", "price": 0.00002},
    "embedv3-large": {"model": "text-embedding-3-large", "price": 0.00013},
    "adav2": {"model": "text-embedding-ada-002", "price": 0.0001},
}

PROMPT = {
    "context": {
        "template": """Context information is below.
---------------------
{context_str}
---------------------""",
        "token": 29,
    },
    "query_gen": {
        "template": """Given the original query: {query}.
Translate 2 search queries in Vietnamese and English based on original query.
Preserve the main key point and don't generate any additional information.
Vietnamese query:
English query:""",
        "token": 51,
    },
    "pnc_system": {
        "template": """You are a chatbot named PnC Assistant of Orient company.
Informations are from all the documents of the company.
Your job is answer based on that information to users.
If the context is unhelpful, you can also answer the question on your own.""",
        "token": 0,
    },
    "rerank": {
        "template": """Search Query: {query}. \nRank the {num} passages above
based on their relevance to the search query. The passages
should be listed in descending order using identifiers.
The most relevant passages should be listed first.
The output format should be [] > [], e.g., [1] > [2].
Only response the ranking results,
do not say any word or explain""",
        "token": 70,
    },
    "search_query_gen":{
        "template": """Generate 2 more search questions (1 in Vietnamese, 1 in English) for the Brave search engine based on the user's question which is relevant to use query.
Output only valid list containing 2 generated questions.
- Input and output examples can be made more complex based on variations in user questions and context, ensuring realistic scenarios are provided.
Input: 
User question: {user_question}
Output:
""",
        "token": 79
    }
}


DEFAULT_SYSTEM_PROMPT = """You are a REALLY helpful assistant.
If using web_search_tool, please don't rewrite user's instruction.
If you are about to generate code, please follow these code instructions:
=====Set of code instructions=====
* Require the return result in a single source code.
* If it is JavaScript code, the component name should always be 'App'. Return the JavaScript script as JSX. Use Tailwind CSS as the default styling choice. There is no need to include any steps to set up TailwindCSS with Create React App.
=====End of code instructions======="""

RAG_SYSTEM_PROMPT = """You are a REALLY helpful assistant.
Your task is to provide information based on provided context and user's query, as well as provide native conversation.
You should use 'document_retrieval_tool' to retrieve information then use that information to answer user.
Remember to use the original user's query as input, you MUST not rewrite it in yout own."""

MEMORY_SYSTEM_PROMPT = """You are a REALLY helpful assistant.
If using web_search_tool, please don't rewrite user's instruction.
If you are about to generate code, please follow these code instructions:
=====Set of code instructions=====
* Require the return result in a single source code.
* If it is JavaScript code, the component name should always be 'App'. Return the JavaScript script as JSX. Use Tailwind CSS as the default styling choice. There is no need to include any steps to set up TailwindCSS with Create React App.
=====End of code instructions=======

Below are a set of relevant information about a specific user:
=====Relevant information about user=====
{memory}
=====End of relevant information======="""

SEO_SYSTEM_PROMPT = """**Proposed Instruction:**  
- Your task is to craft an engaging and informative SEO blog post based on the provided instructions, as well as provide native conversation. Only write a blog if the user asks you to do so; otherwise, just have a native conversation.
- Focus on delivering practical insights, highlighting key trends, advantages, and disadvantages, or comparisons relevant to the topic. Use clear and structured language to ensure the content is accessible to decision-makers in the tech industry. Aim to enhance understanding and support informed decision-making, while also considering current trends and practical applications in technology and business.
- Never start the introduction with “In today's rapidly evolving digital landscape”. It’s detected as AI generated content. Provide an explanation for every statement. Divide the body content by sub-headings, each sub-heading represents a trend. Provide more explanations for statements. For example, rather than saying “Regular code reviews and audits are essential for identifying and rectifying security flaws. Peer reviews, automated static code analysis, and third-party audits can uncover hidden vulnerabilities that might be overlooked during development. These reviews should be systematic and thorough, ensuring that all code adheres to security best practices and industry standards.” We can say “Code reviews mean having multiple developers examine code systematically to find errors, inefficiencies, and potential security vulnerabilities. It's like a peer-review process for code. Meanwhile, audit refers to a more in-depth examination of the codebase, often conducted by specialized security experts, to identify vulnerabilities, compliance issues, and overall security posture. As security flaws are often introduced unintentionally during development. Regular code reviews can catch these issues early in the development cycle, making them less costly to fix. These reviews should be systematic and thorough, ensuring that all code adheres to security best practices and industry standards.”
- Provide citation for each information you use from internet in format: [information](link)

Here are the references from internet that you could use for writing the blog:
{reference}

**Proposed Prefix For Output Field:**  
"Here is a comprehensive SEO blog post that explores the topic in detail:

---

Follow the following format.

Instruction: ${{instruction}}
Here is a comprehensive SEO blog post that explores the topic in detail: often between 2000 and 2500 words"""


QUESTION_GEN_TEMPLATE = """Given a user question, and a list of tools, output a list of relevant sub-questions in json markdown that when composed can help answer the full user question:

# Example 1
<Tools>
```json
{{
    "web_search_tool": "Used to retrieve information about up-to-date information, website or the information out of LLM's knowledge",
    "web_fetch_tool": "Used to fetch information of specific url. Must be run after wearch_search is run"
}}
```

<User Question>
What are the advantages and disadvantages of working from home?


<Output>
```json
{{
    "items": [
        {{
            "sub_question": "What is the advantages of working from home?",
            "tool_name": "web_search",
        }},
        {{
            "sub_question": "What are the advantages and disadvantages of working from home?",
            "tool_name": "web_search"
        }},
        
    ]
}}
```
# Note: Maximum subquestions are 2 and minimum one is 1.
# Example 2
<Tools>
```json
{tools_str}
```

<User Question>
{query_str}

<Output>
"""