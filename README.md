# 🧠 Deep Research Agent
> ⚠️ This project draws inspiration from LangChain's open_deep_research, and specializes it for domain-specific research automation. It features task-tailored prompt engineering, along with a redesigned web search postprocessing pipeline to control context size and ensure cleaner input for LLMs during section generation.


A modular and automated research report generation tool designed for **in-depth topic analysis** using Retrieval-Augmented Generation (RAG), human-in-the-loop verification, and multi-agent LLM coordination. Built with [LangGraph](https://github.com/langchain-ai/langgraph) for structured, dynamic execution.

---

## 🚀 Features

- 🔍 Hybrid retrieval from web search and local database
- 🧱 YAML-configurable report structure & prompt style
- 🤖 Multi-agent design:
  - Query & Section Writer (LLM)
  - Section Grader & Verifier
  - Web/Local Retriever
- 👤 Optional human feedback to regenerate report plans
- 📑 Parallel section generation for efficient execution
- 💬 Supports structured prompt styles: `"industry"` or `"research"`

---

## 📁 File Overview

| File/Folder             | Description                                                                     |
| ----------------------- | ------------------------------------------------------------------------------- |
| `report_writer.py`      | Main logic for planning and writing reports via LangGraph                       |
| `Prompt/`               | Prompt templates for industry or research report styles                         |
| `State/`                | Definitions of section state, report state, and transitions                     |
| `Tools/`                | Formatters for feedback, query generation, and section output                   |
| `Utils/`                | Utility functions including search deduplication, web API wrappers, pdf parsing |
| `retriever.py`          | Hybrid retriever using local embedding search + keyword web search              |
| `report_config.yaml`    | Model settings, report prompt structure, and generation style                   |
| `retriever_config.yaml` | Retriever behavior, chunking parameters, and embedding model                    |

---

## ⚙️ Configuration

### `report_config.yaml`

```yaml
PROMPT_STYLE: "industry"
VERIFY_MODEL_NAME: deepseek/deepseek-chat
MODEL_NAME: gpt-4o-mini
WRITER_MODEL_NAME: deepseek/deepseek-chat
CONCLUDE_MODEL_NAME: deepseek/deepseek-chat
REPORT_STRUCTURE: |
  Use this structure and Traditional Chinese to create a report on the user-provided topic:

  1. Brief Summary (No Research Needed)
  2. Main Body Sections (With Subtopics and Research)
  3. Future Areas of Focus (No Research Needed)
```

### `retriever_config.yaml`

```yaml
raw_file_path:
split_chunk_size: 1500
split_chunk_overlap: 250
embedding_model: "BAAI/bge-m3"
top_k: 5
hybrid_weight: [0.4, 0.6]
```

Ensure you have a `.env` file with your LLM tokens:

```env
OPENAI_API_KEY = 
GEMINI_API_KEY = 
DEEPSEEK_API_KEY = 
REPLICATE_API_KEY = 
TAVILY_API_KEY = 
SEARCH_HOST = 
SEARCH_PORT = 
```

---
## 📄 Advanced Information Retrieval

###  PDF Processing Engine 
Utils/pdf_preprocessor.py

This module provides a powerful PDF processing pipeline designed to convert unstructured pdf files into structured, RAG-optimized JSON data. It uses LLMs to intelligently parse, analyze, and enrich the content, making complex information within PDFs easily accessible for your agent.

#### Core Features:
`High-Fidelity Conversion`: Uses the marker library to accurately convert PDFs into structured Markdown, preserving tables and document layout.

`Automated Metadata Extraction`: An LLM automatically extracts and formats key information from each pdf file(the first 5000 characters).
The implemented options include metadata for institutional investment reports and academic research papers.

`Context-Aware Table Summarization`: Instead of just extracting tables, the system identifies their surrounding context (headings and paragraphs). It then uses an LLM to generate a natural language summary for each table, explaining its purpose and contents. This makes complex tabular data highly discoverable via semantic search.

---

### Audio Process Engine
Doing...

---
### Information Retrieval Strategy
---
Our RAG process, inspired by Ilya Rice's award-winning strategy

`retriever.py` : Enhances retrieval quality by indexing content in small, overlapping chunks (300-character size, 50-character overlap) for precise search results.


`Utils/utils.py track_expanded_context function` : When a relevant chunk is found, we retrieve a larger "window" of text surrounding it from the original document. This "small-to-large" approach provides the LLM with complete, coherent context, avoiding fragmented information and significantly improving the accuracy of the final output. 

During web searches, if a single webpage contains too much information, we also apply the method mentioned above. We perform information retrieval on the webpage's content instead of directly passing the entire content to the LLM agent.

---

## 🧪 Usage

### 1. Configure the research

```python
from langgraph_core.runnables import RunnableConfig
from State.state import ReportStateInput
from report_writer import graph, DEFAULT_REPORT_STRUCTURE

config = RunnableConfig({
    "thread_id": "textile-industry",
    "number_of_queries": 5,
    "use_web": True,
    "use_local_db": False,
    "max_search_depth": 5,
    "report_structure": DEFAULT_REPORT_STRUCTURE,
})

topic = "An in-depth analysis of .... as of 2025/04/15..."
input = ReportStateInput(topic=topic)
```

### 2. Launch the graph

```python
for event in graph.stream(input, config, stream_mode="updates"):
    if "__interrupt__" in event:
        print(event["__interrupt__"][0].value)
```

### 3. Interaction

```python
from langgraph.types import Command
for event in graph.stream(Command(resume='Refine the ... section with more information about ... '), config, stream_mode="updates"):
    print(dict(event))
```

### 4. Export the report

```python
with open("report.md", "w") as f:
    f.write(event["compile_final_report"]["final_report"])
```

