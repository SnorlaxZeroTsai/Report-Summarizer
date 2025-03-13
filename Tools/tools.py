from langchain_core.tools import tool
from typing import List, Literal


@tool
def queries_formatter(thought: str, queries: List[str]):
    """Summary
    Take thoughts and a list of queries convert them into Queries object
    Args:
        thought:str : the thought of these queries
        queries:List[str]: the queries in a list
    """
    return {"search_queries": queries}


@tool
def feedback_formatter(grade: Literal["pass", "fail"], follow_up_queries: List[str]):
    """Summary
    Take grad and follow up queries convert them into Feedback object
    Args:
        grade (Literal[pass,fail]): Evaluation result indicating whether the response meets requirements ('pass') or needs revision ('fail').
        follow_up_squeries (List[str]): List of follow-up search queries.
    """
    ...


@tool
def section_formatter(name: str, description: str, research: bool, content: str):
    """Summary
    Take name, description, research, content and convert them into Section object
    Args:
        name (str): Name for this section of the report.
        description (str): Brief overview of the main topics and concepts to be covered in this section.
        research (bool): Whether to perform web research for this section of the report.
        content (str): The content of the section.
    """
    return {
        "name": name,
        "description": "description",
        "research": research,
        "content": content,
    }
