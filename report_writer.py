# %%
from dotenv import load_dotenv

load_dotenv(".env")
from typing import Literal

from langchain_community.chat_models import ChatLiteLLM
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.constants import Send
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from Prompt.prompt import (
    query_writer_instructions,
    report_planner_instructions,
    report_planner_query_writer_instructions,
    section_grader_instructions,
    section_writer_instructions,
    final_section_writer_instructions,
)
from retriever import hybrid_retriever
from State.state import (
    ReportState,
    ReportStateInput,
    ReportStateOutput,
    Section,
    SectionOutputState,
    SectionState,
)
from langgraph.checkpoint.memory import MemorySaver
from Tools.tools import feedback_formatter, queries_formatter, section_formatter
from Utils.utils import format_human_feedback, format_search_results, format_sections

# %%
VERIFY_MODEL_NAME = "gpt-4o-mini"
MODEL_NAME = "gpt-4o-mini"
CONCLUDE_MODEL_NAME = "gpt-4o-mini"
# "gemini/gemini-2.0-flash"

# %%
DEFAULT_REPORT_STRUCTURE = """Use this structure and Traditional Chinese to create a report on the user-provided topic:

1. Introduction (no research needed)
   - Brief overview of the topic area (around 1000 words)

2. Main Body Sections:
   - Each section should focus on a sub-topic of the user-provided topic
   
3. Conclusion
   - Aim for structural element (either a list of table) that distills the main body sections 
   - Provide a concise summary of the report"""


# %%
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
    return Section(
        name=name, description=description, research=research, content=content
    )


def search_relevance_doc(queries):
    info = []
    for q in queries:
        if q == "":
            continue
        results = hybrid_retriever.get_relevant_documents(q)
        for res in results:
            if res not in info:
                info.append(res)
    return info


def generate_report_plan(state: ReportState, config: RunnableConfig):
    topic = state["topic"]
    feedback = state.get("feedback_on_report_plan", None)

    if feedback is not None:
        feedback = format_human_feedback(feedback)

    # Get configuration
    configurable = config["configurable"]
    report_structure = configurable["report_structure"]
    number_of_queries = configurable["number_of_queries"]

    # Convert JSON object to string if necessary
    if isinstance(report_structure, dict):
        report_structure = str(report_structure)

    # Set writer model (model used for query writing and section writing)
    writer_model = ChatLiteLLM(model=MODEL_NAME, temperature=0)
    structured_llm = writer_model.bind_tools(
        tools=[queries_formatter], tool_choice="required"
    )

    # Format system instructions
    system_instructions_query = report_planner_query_writer_instructions.format(
        topic=topic,
        report_organization=report_structure,
        number_of_queries=number_of_queries,
        feedback=feedback,
    )

    # Generate queries
    results = structured_llm.invoke(
        [SystemMessage(content=system_instructions_query)]
        + [
            HumanMessage(
                content="Generate search queries that will help with planning the sections of the report."
            )
        ]
    )
    query_list = results.tool_calls[0]["args"]["queries"]
    results = search_relevance_doc(query_list)
    source_str = format_search_results(results, 1000)

    # Format system instructions
    system_instructions_sections = report_planner_instructions.format(
        topic=topic,
        report_organization=report_structure,
        context=source_str,
        feedback=feedback,
    )

    # Generate sections
    planner_llm = ChatLiteLLM(model=MODEL_NAME, temperature=0)
    structured_llm = planner_llm.bind_tools([section_formatter], tool_choice="required")
    report_sections = structured_llm.invoke(
        [SystemMessage(content=system_instructions_sections)]
        + [
            HumanMessage(
                content="Generate the sections of the report. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, plan, research, and content fields."
            )
        ]
    )
    # Get sections
    sections = [
        Section(**tool_call["args"]) for tool_call in report_sections.tool_calls
    ]
    return {"sections": sections}


def human_feedback(
    state: ReportState, config: RunnableConfig
) -> Command[Literal["generate_report_plan", "build_section_with_web_research"]]:
    sections = state["sections"]
    sections_str = "\n\n".join(
        f"Section: {section.name}\n"
        f"Description: {section.description}\n"
        f"Research needed: {'Yes' if section.research else 'No'}\n"
        for section in sections
    )
    feedback = interrupt(
        f"Please provide feedback on the following report plan. \n\n{sections_str}\n\n Does the report plan meet your needs? Pass 'true' to approve the report plan or provide feedback to regenerate the report plan:"
    )
    if isinstance(feedback, bool):
        return Command(
            goto=[
                Send(
                    "build_section_with_web_research",
                    {"section": s, "search_iterations": 0},
                )
                for s in sections
                if s.research
            ]
        )
        # return Command(goto=END)
    elif isinstance(feedback, str):
        return Command(
            goto="generate_report_plan",
            update={"feedback_on_report_plan": [feedback]},
        )
    else:
        raise TypeError(f"Interrupt value of type {type(feedback)} is not supported.")


def generate_queries(state: SectionState, config: RunnableConfig):

    section = state["section"]

    configurable = config["configurable"]
    number_of_queries = configurable["number_of_queries"]

    llm = ChatLiteLLM(model=MODEL_NAME, temperature=0)
    structure_llm = llm.bind_tools(tools=[queries_formatter], tool_choice="required")

    system_instruction = query_writer_instructions.format(
        topic=section.description, number_of_queries=number_of_queries
    )
    kwargs = structure_llm.invoke(
        [SystemMessage(content=system_instruction)]
        + [HumanMessage(content="Generate search queries on the provided topic.")]
    )

    tool_calls = kwargs.tool_calls[0]["args"]
    return queries_formatter.invoke(tool_calls)


def search_db(state: SectionState, config: RunnableConfig):
    query_list = state["search_queries"]
    results = search_relevance_doc(query_list)
    source_str = format_search_results(results, None)
    return {
        "source_str": source_str,
        "search_iterations": state["search_iterations"] + 1,
    }


def write_section(
    state: SectionState, config: RunnableConfig
) -> Command[Literal[END, "search_db"]]:
    # Get state
    section = state["section"]
    source_str = state["source_str"]

    configurable = config["configurable"]
    max_search_depth = configurable["max_search_depth"]

    # Format system instructions
    system_instructions = section_writer_instructions.format(
        section_title=section.name,
        section_topic=section.description,
        context=source_str,
        section_content=section.content,
    )
    # Generate section
    writer_model = ChatLiteLLM(model=MODEL_NAME, temperature=0)
    section_content = writer_model.invoke(
        [SystemMessage(content=system_instructions)]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to the section object
    section.content = section_content.content

    # Grade prompt
    section_grader_instructions_formatted = section_grader_instructions.format(
        section_topic=section.description, section=section.content
    )

    # Feedback
    structured_llm = ChatLiteLLM(model=VERIFY_MODEL_NAME, temperature=0).bind_tools(
        tools=[feedback_formatter], tool_choice="required"
    )
    feedback = structured_llm.invoke(
        [SystemMessage(content=section_grader_instructions_formatted)]
        + [
            HumanMessage(
                content="Grade the report and consider follow-up questions for missing information"
            )
        ]
    )
    feedback = feedback.tool_calls[0]["args"]
    print(feedback["grade"])
    if feedback["grade"] == "pass" or state["search_iterations"] >= max_search_depth:
        # Publish the section to completed sections
        return Command(update={"completed_sections": [section]}, goto=END)
    else:
        # Update the existing section with new content and update search queries
        return Command(
            update={
                "search_queries": feedback["follow_up_queries"],
                "section": section,
            },
            goto="search_db",
        )


def gather_complete_section(state: ReportState):
    completed_sections = state["completed_sections"]
    completed_report_sections = format_sections(completed_sections)
    return {"report_sections_from_research": completed_report_sections}


def initiate_final_section_writing(state: ReportState):

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send(
            "write_final_sections",
            {
                "section": s,
                "report_sections_from_research": state["report_sections_from_research"],
            },
        )
        for s in state["sections"]
        if not s.research
    ]


def write_final_sections(state: SectionState, config: RunnableConfig):

    section = state["section"]
    completed_report_sections = state["report_sections_from_research"]
    system_instructions = final_section_writer_instructions.format(
        section_title=section.name,
        section_topic=section.description,
        context=completed_report_sections,
    )
    writer_model = ChatLiteLLM(model=CONCLUDE_MODEL_NAME, temperature=0)
    section_content = writer_model.invoke(
        [SystemMessage(content=system_instructions)]
        + [
            HumanMessage(
                content="Generate a report section based on the provided sources."
            )
        ]
    )

    # Write content to section
    section.content = section_content.content
    return {"completed_sections": [section]}


def compile_final_report(state: ReportState):
    # Get sections
    sections = state["sections"]
    completed_sections = {s.name: s.content for s in state["completed_sections"]}

    # Update sections with completed content while maintaining original order
    for section in sections:
        section.content = completed_sections[section.name]

    # Compile final report
    all_sections = "\n\n".join([s.content for s in sections])

    return {"final_report": all_sections}


section_builder = StateGraph(SectionState, output=SectionOutputState)
section_builder.add_node("generate_queries", generate_queries)
section_builder.add_node("search_db", search_db)
section_builder.add_node("write_section", write_section)

section_builder.add_edge(START, "generate_queries")
section_builder.add_edge("generate_queries", "search_db")
section_builder.add_edge("search_db", "write_section")
# %%
builder = StateGraph(ReportState, input=ReportStateInput, output=ReportStateOutput)
builder.add_node("generate_report_plan", generate_report_plan)
builder.add_node("human_feedback", human_feedback)
builder.add_node("build_section_with_web_research", section_builder.compile())
builder.add_node("gather_complete_section", gather_complete_section)
builder.add_node("write_final_sections", write_final_sections)
builder.add_node("compile_final_report", compile_final_report)

builder.add_edge(START, "generate_report_plan")
builder.add_edge("generate_report_plan", "human_feedback")
builder.add_edge("build_section_with_web_research", "gather_complete_section")
builder.add_conditional_edges(
    "gather_complete_section",
    initiate_final_section_writing,
    ["write_final_sections"],
)
builder.add_edge("write_final_sections", "compile_final_report")
builder.add_edge("compile_final_report", END)
graph = builder.compile(checkpointer=MemorySaver())
