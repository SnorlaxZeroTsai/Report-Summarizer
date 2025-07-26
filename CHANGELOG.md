# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-07-23

### Added
- Created a separate LangGraph for agentic web search in `agentic_search.py`.
- Introduced asynchronous processing in the web search graph to improve performance of search quality checks.

### Changed
- Refactored `report_writer.py` to delegate web search tasks to the new agentic search graph.
- Moved the `call_llm` function to `Utils/utils.py` for better code reuse and created an asynchronous version `call_llm_async`.