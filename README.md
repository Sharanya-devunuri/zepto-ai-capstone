# Zepto AI Capstone Project

An end-to-end AI and data engineering capstone project covering data processing, analytics, and an AI-powered support assistant.

## Project Components

### 1. Data Pipeline
Handles data collection, cleaning, transformation, validation, and preparation for downstream analytics.

### 2. Analytics
Provides analysis and insights from the processed dataset.

### 3. Support Assistant
An AI-powered policy question-answering system using FastAPI, LangGraph, Sentence Transformers, and ChromaDB.

## Repository Structure

zepto-ai-capstone/
├── README.md
├── requirements.txt
├── analytics/
├── data_pipeline/
└── support_assistant/
    ├── README.md
    ├── Dockerfile
    ├── docs/
    ├── chroma_db/
    └── support_assistant.py

## Support Assistant

The /ask API accepts policy-related questions and returns an answer, retrieved source documents, and a confidence score.

The Support Assistant has been tested successfully with a policy query and returned a valid response with retrieved sources.

## Technologies

- Python
- Pandas
- SQLite
- FastAPI
- LangGraph
- ChromaDB
- Sentence Transformers
- Docker