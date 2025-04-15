import json
import math
from typing import List, Literal, TypedDict

import requests
from langchain.schema import Document
from tavily import TavilyClient
from State.state import Section
import os
from langchain.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

host = os.environ.get("SEARCH_HOST", None)
port = os.environ.get("SEARCH_PORT", None)
temp_files_path = os.environ.get("temp_dir", "./temp")
os.makedirs(temp_files_path, exist_ok=True)
tavily_client = TavilyClient()


# %%
class ContentExtractor(object):
    def __init__(self, temp_dir=temp_files_path, k=3):
        self.k = k
        self.temp_dir = temp_dir
        embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")
        self.docs = [Document("None", metadata={"path": "None"})]
        self.vectorstore = Chroma.from_documents(
            documents=self.docs,
            collection_name="temp_data",
            embedding=embeddings,
        )
        self.bm25_retriever = BM25Retriever.from_documents(self.docs)
        self.bm25_retriever.k = self.k
        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[
                self.vectorstore.as_retriever(search_kwargs={"k": self.k}),
                self.bm25_retriever,
            ],
            weights=[0.4, 0.6],
        )

    def update_new_docs(self, files):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=5000,
            chunk_overlap=250,
            separators=["\n\n\n\n", "\n\n\n", "\n\n", "\n", ""],
        )
        new_docs = []
        for file in files:
            with open(file, "r") as f:
                texts = f.read()
            name = file.split("/")[-1].replace(".txt", "")
            new_docs.append(Document(texts, metadata={"path": name}))
        new_docs = text_splitter.split_documents(new_docs)
        return new_docs

    def update(self, files):
        new_docs = self.update_new_docs(files)
        self.vectorstore.add_documents(new_docs)
        self.docs.extend(new_docs)

        self.bm25_retriever = BM25Retriever.from_documents(self.docs)
        self.bm25_retriever.k = self.k
        self.hybrid_retriever = EnsembleRetriever(
            retrievers=[
                self.vectorstore.as_retriever(search_kwargs={"k": self.k}),
                self.bm25_retriever,
            ],
            weights=[0.4, 0.6],
        )

    def query(self, q):
        info = []
        results = self.hybrid_retriever.get_relevant_documents(q)
        for res in results:
            if res not in info:
                info.append(res)
        return info


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


content_extractor = ContentExtractor()


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
        output = json.loads(output.content)
        if include_raw_content:
            large_files = []
            for result in output["results"]:
                if result.get("raw_content", "") is None:
                    continue
                try:
                    if len(result.get("raw_content", "")) >= 5000:
                        file_path = f"{temp_files_path}/{result['title']}.txt"
                        with open(file_path, "w") as f:
                            f.write(result["raw_content"])
                        result["raw_content"] = ""
                        large_files.append(file_path)
                except Exception as e:
                    print(e)
                    print(result)

            if len(large_files) > 0:
                content_extractor.update(large_files)
                search_results = content_extractor.query(query)
                for results in search_results:
                    output["results"].append(
                        {
                            "url": results.metadata["path"],
                            "title": results.metadata["path"],
                            "content": "Raw content part has the most relevant information.",
                            "raw_content": results.page_content,
                        }
                    )

        search_docs.append(output)
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
