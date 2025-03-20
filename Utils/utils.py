import json
import math
from typing import List, Literal, TypedDict

import requests
from langchain.schema import Document
from tavily import TavilyClient
from State.state import Section
import os

host, port = os.environ.get("SEARCH_HOST", None), os.environ.get("SEARCH_PORT", None)
tavily_client = TavilyClient()


def format_human_feedback(feedbacks: list[str]) -> str:
    """Format a list of human feedbacks into string"""
    formatted_str = ""
    for idx, feedback in enumerate(feedbacks):
        formatted_str += f"""
        {"="*60}
        feedback {idx} : {feedback}
        
        """
    return formatted_str


def format_sections(sections: list[Section]) -> str:
    """Format a list of sections into a string"""
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
        {'='*60}
        Section {idx}: {section.name}
        {'='*60}
        Description:
        {section.description}
        Requires Research: 
        {section.research}

        Content:
        {section.content if section.content else '[Not yet written]'}

        """
    return formatted_str


def format_search_results(results: List[Document], char_limit: int = 500):
    formatted_text = "Sources:\n\n"
    if char_limit is None:
        char_limit = math.inf
    for doc in results:
        formatted_text += f"Source {doc.metadata['path']}:\n===\n"
        formatted_text += f"Content from source:"
        raw_content = doc.page_content
        if len(raw_content) > char_limit:
            raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += (
                f"Full source content limited to {char_limit} chars: {raw_content}\n\n"
            )
        else:
            formatted_text += f"{raw_content}\n\n"

    return formatted_text


def tavily_search(search_queries, include_raw_content: True):
    search_docs = []
    for query in search_queries:
        search_docs.append(
            tavily_client.search(
                query,
                max_results=3,
                include_raw_content=include_raw_content,
                topic="general",
            )
        )
    return search_docs


def selenium_api_search(search_queries, include_raw_content: True):
    search_docs = []
    for query in search_queries:
        output = requests.get(
            f"http://{host}:{port}/search_and_crawl",
            params={
                "query": query,
                "include_raw_content": include_raw_content,
                "max_results": 5,
                "timeout": 40,
            },
        )
        search_docs.append(json.loads(output.content))
    return search_docs


def web_search_deduplicate_and_format_sources(
    search_response, max_tokens_per_source, include_raw_content=True
):
    # Collect all results
    sources_list = []
    for response in search_response:
        sources_list.extend(response["results"])

    # Deduplicate by URL
    unique_sources = {source["url"]: source for source in sources_list}

    # Format output
    formatted_text = "Sources:\n\n"
    for i, source in enumerate(unique_sources.values(), 1):
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += (
            f"Most relevant content from source: {source['content']}\n===\n"
        )
        if include_raw_content:
            # Using rough estimate of 4 characters per token
            char_limit = max_tokens_per_source * 4
            # Handle None raw_content
            raw_content = source.get("raw_content", "")
            if raw_content is None:
                raw_content = ""
                print(f"Warning: No raw_content found for source {source['url']}")
            if len(raw_content) > char_limit:
                raw_content = raw_content[:char_limit] + "... [truncated]"
            formatted_text += f"Full source content limited to {max_tokens_per_source} tokens: {raw_content}\n\n"

    return formatted_text.strip()
