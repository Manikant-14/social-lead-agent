import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), "data", "knowledge_base.md")

_vectorstore = None

def load_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore
    with open(KNOWLEDGE_BASE_PATH, "r") as f:
        raw_text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=60)
    chunks = splitter.split_text(raw_text)
    docs = [Document(page_content=chunk) for chunk in chunks]
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    _vectorstore = FAISS.from_documents(docs, embeddings)
    return _vectorstore

def retrieve_context(query: str, k: int = 3) -> str:
    vectorstore = load_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results])
