
import os
from typing import TypedDict

import chromadb
from fastapi import FastAPI
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, START, END


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
CHROMA_DIR = os.path.join(BASE_DIR, "chroma_db")

MOCK_LLM = os.getenv("MOCK_LLM", "1")


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------------------------------------------------
# ChromaDB
# ---------------------------------------------------------

chroma_client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = chroma_client.get_or_create_collection(
    name="zepto_policies",
    metadata={"hnsw:space": "cosine"}
)


# ---------------------------------------------------------
# Load policy documents if collection is empty
# ---------------------------------------------------------

if collection.count() == 0:

    documents = []
    doc_ids = []
    metadatas = []

    for filename in sorted(os.listdir(DOCS_DIR)):

        if filename.startswith("doc_") and filename.endswith(".txt"):

            path = os.path.join(DOCS_DIR, filename)

            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()

            documents.append(text)
            doc_ids.append(filename.replace(".txt", ""))
            metadatas.append({"source": filename})

    embeddings = embedding_model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    collection.upsert(
        ids=doc_ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )


# ---------------------------------------------------------
# LangGraph state
# ---------------------------------------------------------

class SupportState(TypedDict, total=False):
    query: str
    intent: str
    retrieved_context: str
    sources: list
    answer: str
    confidence: float


# ---------------------------------------------------------
# Intent classification node
# ---------------------------------------------------------

def classify_intent(state: SupportState):

    query = state["query"].lower()

    policy_keywords = [
        "delivery",
        "return",
        "refund",
        "membership",
        "tracking",
        "track",
        "cancel",
        "cancellation",
        "gift card",
        "giftcard",
        "support hours",
        "support"
    ]

    if any(keyword in query for keyword in policy_keywords):
        intent = "policy"
    else:
        intent = "general"

    return {"intent": intent}


# ---------------------------------------------------------
# Policy retrieval + answer node
# ---------------------------------------------------------

def retrieve_and_answer(state: SupportState):

    query = state["query"]

    query_embedding = embedding_model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    retrieved_documents = results["documents"][0]
    retrieved_ids = results["ids"][0]

    top_chunk = retrieved_documents[0].strip()

    # Avoid cutting the response in the middle of a sentence.
    sentences = top_chunk.split(". ")

    snippet = ""

    for sentence in sentences:
        candidate = sentence if not snippet else snippet + ". " + sentence

        if len(candidate) > 500:
            break

        snippet = candidate

    if not snippet:
        snippet = top_chunk[:500].rstrip()

    if MOCK_LLM == "1":

        answer = f"Based on the retrieved context: {snippet}"

    else:

        # Optional real-LLM branch.
        answer = f"Based on the retrieved context: {snippet}"

    return {
        "retrieved_context": "\n\n".join(retrieved_documents),
        "sources": retrieved_ids,
        "answer": answer,
        "confidence": 0.9
    }


# ---------------------------------------------------------
# General-answer node
# ---------------------------------------------------------

def direct_answer(state: SupportState):

    return {
        "answer": "I can only answer questions about Zepto policies right now.",
        "sources": [],
        "confidence": 1.0
    }


# ---------------------------------------------------------
# Conditional routing
# ---------------------------------------------------------

def route_intent(state: SupportState):

    if state["intent"] == "policy":
        return "retrieve_and_answer"

    return "direct_answer"


# ---------------------------------------------------------
# Build LangGraph
# ---------------------------------------------------------

workflow = StateGraph(SupportState)

workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

workflow.add_edge(START, "classify_intent")

workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "retrieve_and_answer": "retrieve_and_answer",
        "direct_answer": "direct_answer"
    }
)

workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

support_graph = workflow.compile()


# ---------------------------------------------------------
# Pydantic API models
# ---------------------------------------------------------

class AskRequest(BaseModel):
    query: str


class SupportResponse(BaseModel):

    answer: str

    sources: list[str]

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="Zepto Support Assistant",
    description="Policy-based Zepto customer support assistant",
    version="1.0"
)


@app.post("/ask", response_model=SupportResponse)
def ask(request: AskRequest):

    result = support_graph.invoke({
        "query": request.query
    })

    return SupportResponse(
        answer=result["answer"],
        sources=result["sources"],
        confidence=result["confidence"]
    )
