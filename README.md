# 📄Policy QA Assistant(RAG Mini Project)

## Overview

This project is a Retrieval-Augmented Generation(RAG) based QA(question answering) assistant built over company policy documents(like Refund,Cancellation,Shipping,Return,etc.).
It retrieves relevant policy contents for the given documents and generates accurate,grounded answers while avoiding hallucinations.

This project mainly focuses on:

-Prompt engineering

-Retrieval quality

-Evaluation and reasoning over LLM outputs

# Setup Instructions
## 1.Clone the Repository
```bash
git clone <repo-url>
cd policy-qa-rag
```
## 2.Install Dependencies
``` bash
pip install -r requirements.txt
```
## 3.Environment Variables
```env
GROQ_API_KEY=copy_and_paste_your_api_key_here
```
## 4.Run the App
```bash
streamlit run app.py
```

# Architecture Overview
```text
PDF's of Policy Documents
        ↓
Text Cleaning & Chunking
        ↓
Converting into embeddings
        ↓
FAISS Vector Store
        ↓
Top-K Semantic Retrieval
        ↓
Simple Re-ranking of chunks 
        ↓
Prompt+Grounded Context given to LLM 
        ↓
LLM Answer
```
# Data Preparation

-First Documents are loaded using PyPDFLoader and DirectoryLoader

-Text cleaning includes:

    -Removing page numbers

    -Normalizing whitespace

    -Removing repeated headers/footers

    -Removing newlines

-Chunking strategy:

chunk_size = 800

chunk_overlap = 150

### Why this chunk size?
I choose a chunk size of 800 characters because policy rules often extend to multiple sentences if we use smaller chunks (like 200–300) can seperate a policy rule into half, separating the main rule from its exceptions, which can lead to incomplete or misleading answers. So, I choose 800 as chuck size,800 characters usually capture a complete policy rule and if we want we can use 1000 also. Policy documents are usually written in full paragraphs, and those paragraphs often explains one complete rule. With this large chuck size, most chunks naturally contain a whole idea instead of cutting it into half.

If the chunks is too small then, important details like exceptions or conditions could get separated, which would confuse the system during retrieval. If they were too big, the model might give extra, unrelated information. The chunk_overlap makes sure that nothing important information gets lost between chunks.

Overall, this chunk size just felt like the right value to use because it keeps the policy text together in a way that makes sense,and because no important information will get seperated,which leads to accurate and, more reliable answers.

# RAG Pipeline

This project implements a Retrieval-Augmented Generation(RAG) flow:

### Embedding Generation

-Model used:sentence-transformers/all-MiniLM-L6-v2

-Lightweight, fast, and suitable for semantic search

### Vector Storage

-FAISS vector store is used for semantic indexing

-And it is Stored as vector_index.pkl

### Semantic Retrieval

-Top-K retrieval using cosine similarity

-K is selected by user via sidebar(which has default value as 4)

### Re-ranking

After initial retrieval, results are reordered based on relevance signals(content quality).
This helps:

-Improve grounding

-Provide cleaner context to the LLM

### Context Injection

-Retrieved chunks are concatenated with explicit source names.

-Passed the combined chunks directly into the LLM prompt along with the user query.

-This ensures responses are grounded strictly in retrieved policy text.

# Prompt Engineering

### Initial Prompt

-Simple instruction to answer the user query from context.

-Used as a baseline to observe hallucination issues.

### Improved Prompt(Rule-Based)

-Given explicit rules to prevent hallucination.

-Clear fallback for missing information.

-Structured output format.

### Refined Prompt(Human-Friendly)

-More natural language.

-Same strict grounding constraints.

-Improved clarity and readability.

### What Changed and Why
The initial prompt simply telling the model to answer questions using the provided context.In this prompt,I did not restrict the model from using outside knowledge or guessing the answer when the answer is unclear.It also does not specify how the final answer should be displayed.And also it doesn't include how the model should response when the answer is missing.

In the improved prompt,I added explicit rules that clearly tell the model to rely only on the retrieved context and not make any assumptions.I also included a structured response for cases where the information is missing or unclear,which helps prevent hallucinated answers.Additionally,the improved prompt enforces a structured output format,making the responses easier to read,more consistent,and easier to understand.

In the Refined prompt,Better readability without losing control.

Overall, these changes make the assistant more reliable,and aligned with the goal of accurate policy-based question answering.

# Evaluation

-A small evaluation set was created to know the system behavior.

### Evaluation Criteria

1)Accuracy

2)Hallucination Avoidance

3)Answer Clarity

### Scoring Rubric

✅ Correct

⚠️ Partially correct/unclear

❌ Incorrect or unsupported

### Evaluation Results

| Question                                | Coverage Type | Accuracy | Hallucination | Clarity |
| --------------------------------------- | ------------- | -------- | ------------- | ------- |
| Does Flipkart deliver items internationally?  | Answerable    | ✅        | ✅             | ✅       |
| What is the maximum order value allowed for COD? | Answerable    | ✅        | ✅             | ✅       |
| How long does Flipkart take to resolve customer complaints? | Partial       | ⚠️       | ✅             | ⚠️      |
| What happens if an international shipment is lost in transit?| Unanswerable  | ❌        | ✅             | ✅       |
| Who is the CEO of Flipkart?             | Out of Scope  | ❌        | ✅             | ✅       |

# Edge Case Handling
### No Relevant Documents Found

-LLM call is skipped

-Safe fallback message is returned

### Outside Knowledge Base

Model responds with:

"I could not find this information in the provided policy documents."

# Optional Features Implemented

-Prompt templating with LangChain

-Prompt comparison(initial vs improved vs refined)

-Simple reranking of chunks.

-Source-aware responses

-Basic logging and tracing

# Key Trade-offs & Future Improvements
## Trade-offs

-FAISS is chosen for simplicity and speed.

-Manual evaluation preferred over automated metrics for interpretability.

-Lightweight embedding model is used for speed.

### With More Time,I can 

-Add cross-encoder or LLM-based reranking

-Enforce JSON output validation

-Add automated evaluation metrics

-Add metadata-based filtering

-Cache repeated queries
