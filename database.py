from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from logger import logger
import pickle
import re

def clean_pdf_text(text: str) -> str:
    #Removing page numbers like "Page 1", "Page 2 of 5"
    text = re.sub(r'Page\s+\d+(\s+of\s+\d+)?', '', text, flags=re.IGNORECASE)

    #Removing repeated headers/footers
    text = re.sub(r'(Refund Policy|Cancellation Policy|Shipping Policy)', 
                  lambda m: m.group(0), text)

    #Removing extra newlines
    text = re.sub(r'\n{2,}', '\n', text)

    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def prepare_database():
    logger.info("Starting database preparation")
    loader=DirectoryLoader("data", glob = "./*.pdf", loader_cls= PyPDFLoader)
    data=loader.load()
    logger.info(f"Just loaded {len(data)} pages")
    for doc in data:
        doc.page_content = clean_pdf_text(doc.page_content)
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=150)
    splitted_data = splitter.split_documents(data)
    logger.info("Just completed splitting the data")
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    db = FAISS.from_documents(splitted_data, embedding)
    file_path="vector_index.pkl"
    with open(file_path, "wb") as f:
        pickle.dump(db, f)
    logger.info("FAISS vector store created and saved successfully")    