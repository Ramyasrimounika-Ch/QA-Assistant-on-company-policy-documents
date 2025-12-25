import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from prompt import return_prompt
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from database import prepare_database
from logger import logger
from dotenv import load_dotenv
import pickle
  
load_dotenv()

st.set_page_config(page_title="Policy QA Assistant",page_icon="📄")
st.title("Flipkart Policy QA Assistant")
logger.info("Policy QA Streamlit app started")
file_path="vector_index.pkl"
if not os.path.exists(file_path):
    prepare_database()

with open(file_path,"rb") as f:
    vectori=pickle.load(f)
logger.info("Vector index loaded")    

prompt_selected=st.sidebar.radio("Select prompt", ["initial_prompt", "improved_prompt1","improved_prompt2"])
prompt=return_prompt(prompt_selected)
k_selected=st.sidebar.slider("Select k value", 1, 10, 4)

llm=ChatGroq(
    model="llama-3.1-8b-instant"
)
 
def content_retrieval(query,k):
    #retrieving more documents than needed for reranking purpose
    result=vectori.similarity_search(query, k*2)
    reranked_docs=simple_rerank(query,result)
    final_docs=reranked_docs[:k]
    content=""

    for doc in result:
        source_path=doc.metadata.get("source", "")
        source_name=os.path.basename(source_path) if source_path else "Unknown source"

        content+=f"Source:{source_name}\n"
        content+=doc.page_content
        content+="\n\n"

    return content

def simple_rerank(query,docs):
    query_terms=set(query.lower().split())
    scored_docs=[]

    for doc in docs:
        doc_terms=set(doc.page_content.lower().split())
        score=len(query_terms&doc_terms)  
        scored_docs.append((score,doc))

    scored_docs.sort(reverse=True,key=lambda x:x[0])
    return [doc for _,doc in scored_docs]

   

query=st.text_input("Enter the question:")
clicked=st.button("generate answer")

if clicked:
    logger.info(f"User query received:{query}")
    logger.info(f"Prompt selected:{prompt_selected}")
    context=content_retrieval(query,k_selected)

    if not context.strip():
        logger.warning("No relevant documents found for query")
        st.warning("No relevant information found in the policy documents.")
    else:
        chain=prompt|llm
        ans=chain.invoke({"context":context,"input":query})

        st.subheader("Answer")
        st.write(ans.content)

        with st.expander("Prompt Used"):
            st.code(prompt.messages[0].prompt.template)
        retrieved_docs=vectori.similarity_search(query,k=k_selected)

        with st.expander("View Retrieved Context"):
            for i,doc in enumerate(retrieved_docs):
                st.markdown(f"Chunk {i+1}:")
                source_path=doc.metadata.get("source", "")
                source_name=os.path.basename(source_path) if source_path else "Unknown source"
                st.markdown(f"Source:{source_name}")
                st.write(doc.page_content[:800]+"...")
    
        
