import math
from typing import List, Literal, TypedDict
from langchain.schema import Document
from State.state import Section


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
