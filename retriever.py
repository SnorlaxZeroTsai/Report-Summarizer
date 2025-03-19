# %%
import glob

import omegaconf
import torch
from langchain.retrievers import BM25Retriever
from langchain.retrievers.ensemble import EnsembleRetriever
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# %%
config = omegaconf.OmegaConf.load("retriever_config.yaml")
files = []
if config["raw_file_path"] is not None:
    for f in config["raw_file_path"]:
        files.extend(glob.glob(f))

    documents = []
    for file in files:
        with open(file, "r") as f:
            texts = f.read()
        name = file.split("/")[-1].replace(".txt", "")
        documents.append(Document(texts, metadata={"path": name}))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["split_chunk_size"],
        chunk_overlap=config["split_chunk_overlap"],
        separators=["\n\n\n\n", "\n\n\n", "\n\n"],
    )
    doc_splits = text_splitter.split_documents(documents)

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
