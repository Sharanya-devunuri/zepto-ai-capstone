# Zepto Support Assistant

A policy-based customer support assistant built using Sentence Transformers, ChromaDB, LangGraph, Pydantic, and FastAPI.

## Architecture

User Query -> classify_intent -> policy/general routing

Policy queries -> retrieve_and_answer -> top-3 ChromaDB retrieval

General queries -> direct_answer

## Components

### Policy Documents

The docs directory contains eight Zepto policy documents.

- doc_01.txt - Delivery Policy
- doc_02.txt - Returns & Refunds
- doc_03.txt - Membership Tiers
- doc_04.txt - Order Tracking
- doc_05.txt - Order Cancellation Policy
- doc_06.txt - Damaged or Missing Items
- doc_07.txt - Gift Cards
- doc_08.txt - Customer Support Hours

### Embedding Model

The assistant uses the local Sentence Transformers model: all-MiniLM-L6-v2.

### ChromaDB

ChromaDB is used as the local persistent vector database.

Collection: zepto_policies

Similarity metric: cosine similarity.

The system retrieves the top 3 policy documents for policy-related questions.

### LangGraph

The workflow contains three nodes:

1. classify_intent
2. retrieve_and_answer
3. direct_answer

Conditional routing:

- policy -> retrieve_and_answer
- general -> direct_answer

### Structured Prompt

The prompt includes Role, Context, Task, Format, Length, Negative Constraint, and a Few-shot Example.

### MOCK_LLM

The application defaults to MOCK_LLM=1.

In mock mode, policy responses are generated from retrieved policy context.

General questions return: I can only answer questions about Zepto policies right now.

### Pydantic Response

The response contains answer, sources, and confidence.

Confidence is constrained between 0 and 1.

### FastAPI

The application exposes POST /ask.

Example request: {"query": "How much does priority delivery cost?"}

## Running the API

Install dependencies using the root requirements.txt file.

Run with:

uvicorn support_assistant.support_assistant:app --host 0.0.0.0 --port 8000

## Docker

Build from the repository root:

docker build -f support_assistant/Dockerfile .

Run:

docker run -p 8000:8000 -e MOCK_LLM=1 zepto-support-assistant

## Project Structure

support_assistant/
  docs/
  chroma_db/
  support_assistant.py
  Dockerfile
  README.md