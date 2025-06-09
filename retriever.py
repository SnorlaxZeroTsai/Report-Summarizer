# %%
import os
import glob
import json

import omegaconf
import torch
from langchain.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger("AgentLogger")
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# %%
def process_date(information):
    date = information["date"]
    if date is None or date == "None":
        logger.critical(file)
        logger.critical(
            "Can not get date information by first 5000 strngs. Try to parse the date information by file name"
        )
        try:
            date = name.split("-")[-1]
            if "_" in date:
                date = date.split("_")[0]

        except Exception as e:
            logger.critical(
                "Can not get date information by file name. Set date to None"
            )
        finally:
            date = "None"
    return date


def process_document(name, date, information):
    if "table" in information:
        if len(information["table"]) >= 100000:
            logger.critical(
                f"File:{file}.\n\n The length of table string longer than 100000"
            )
            return None

        metadata = {
            "path": name,
            "date": date,
            "context_heading": (
                information["context_heading"]
                if information["context_heading"]
                else "None"
            ),
            "context_paragraph": (
                information["context_paragraph"]
                if information["context_paragraph"]
                else "None"
            ),
            "summary": information["summary"],
            "table": information["table"],
        }
        doc = Document(
            information["summary"],
            metadata=metadata,
        )

    else:
        doc = Document(
            information["full_content"],
            metadata={
                "path": name,
                "content": information["full_content"],
                "date": date,
            },
        )
    return doc


def track_expanded_context(
    original_context: str,
    critical_context: str,
    forward_capacity: int = 10000,
    backward_capacity: int = 2500,
):
    start_idx = original_context.find(critical_context)
    if start_idx != -1:
        end_idx = start_idx + len(critical_context)
        desired_start_idx = max(0, start_idx - backward_capacity)
        desired_end_idx = min(len(original_context), end_idx + forward_capacity)
        start_boundary_pos = original_context.rfind("\n\n", 0, desired_start_idx)
        if start_boundary_pos == -1:
            final_start_idx = 0
        else:
            final_start_idx = start_boundary_pos + 2  # 長度 of '\n\n' is 2

        end_boundary_pos = original_context.find("\n\n", desired_end_idx)
        if end_boundary_pos == -1:
            final_end_idx = len(original_context)
        else:
            final_end_idx = end_boundary_pos
        expanded_context = original_context[final_start_idx:final_end_idx]

        return expanded_context

    else:
        logger.critical("Can not find critical content")
        return None


# %%
config = omegaconf.OmegaConf.load("retriever_config.yaml")
files = []
if config["raw_file_path"] is not None:
    for f in config["raw_file_path"]:
        files.extend(glob.glob(f))

    documents, table_documents = [], []
    for file in files:
        name = os.path.split(file)[-1]
        name, extension = os.path.splitext(name)
        with open(file, "rb") as f:
            information = json.load(f)

        date = process_date(information)
        doc = process_document(file, date, information)

        if doc is None:
            continue

        if "table" in doc.metadata:
            table_documents.append(doc)

        else:
            documents.append(doc)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["split_chunk_size"],
        chunk_overlap=config["split_chunk_overlap"],
        separators=["\n\n\n\n", "\n\n\n", "\n\n", "\n"],
    )
    doc_splits = text_splitter.split_documents(documents) + table_documents
    embeddings = HuggingFaceEmbeddings(model_name=config["embedding_model"])
    vectorstore = Chroma.from_documents(
        documents=doc_splits,
        collection_name="rag-chroma",
        embedding=embeddings,
    )
    torch.cuda.empty_cache()
    bm25_retriever = BM25Retriever.from_documents(doc_splits)
    bm25_retriever.k = config["top_k"]
    hybrid_retriever = EnsembleRetriever(
        retrievers=[
            vectorstore.as_retriever(search_kwargs={"k": config["top_k"]}),
            bm25_retriever,
        ],
        weights=config["hybrid_weight"],
    )
else:
    hybrid_retriever = None
