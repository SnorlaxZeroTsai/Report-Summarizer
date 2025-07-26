from langchain_core.tools import tool
from typing import List, Literal


@tool
def searching_grader_formatter(
    grade: Literal["pass", "fail"], follow_up_queries: List[str]
):
    """Summary
    Take grade and follow up queries convert them into suitable format
    Args:
        grade (Literal[pass,fail]): Evaluation result indicating whether the context meets requirements ('pass') or needs revision ('fail').
        follow_up_squeries (List[str]): List of follow-up search queries.
    """
    ...


@tool
def searching_budget_formatter(budget: int):
    """Summary
    Take the value of seraching budget of query list
    Args:
        budget (int): the value of seraching budget
    """
    return {"budget": budget}


@tool
def quality_formatter(score: int):
    """Summary
    Take the score of searching results of a query
    Args:
        score:int = the score of query document pair
    """
    return {"score": score}


@tool
def summary_formatter(summary_content: str):
    """Summary
    Take the summarized content of search results of a query
    Args:
        summary_content:str = the summarized content of raw document
    """
    return {"summary_content": summary_content}


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
    Take grade and follow up queries convert them into Feedback object
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
        "description": description,
        "research": research,
        "content": content,
    }
