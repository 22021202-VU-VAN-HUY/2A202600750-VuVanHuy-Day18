"""Shared configuration for Lab 18."""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys / OpenAI-compatible LLM ---
RAW_OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
MIMO_BASE_URL = os.getenv("MIMO_BASE_URL", "")
MIMO_MODEL = os.getenv("MIMO_MODEL", "mimo-v2.5-pro")

OPENAI_API_KEY = MIMO_API_KEY or RAW_OPENAI_API_KEY
LLM_API_KEY = OPENAI_API_KEY
LLM_BASE_URL = MIMO_BASE_URL if MIMO_API_KEY else os.getenv("OPENAI_BASE_URL", "")
LLM_MODEL = MIMO_MODEL if MIMO_API_KEY else os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if LLM_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", LLM_API_KEY)
if LLM_BASE_URL:
    os.environ.setdefault("OPENAI_BASE_URL", LLM_BASE_URL)
    os.environ.setdefault("OPENAI_API_BASE", LLM_BASE_URL)


def create_llm_client():
    """Create an OpenAI-compatible client for OpenAI or Mimo."""
    if not LLM_API_KEY:
        return None
    from openai import OpenAI
    kwargs = {"api_key": LLM_API_KEY, "timeout": 30}
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return OpenAI(**kwargs)

# --- Qdrant ---
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "lab18_production"
NAIVE_COLLECTION = "lab18_naive"

# --- Embedding ---
EMBEDDING_MODEL = "BAAI/bge-m3"
EMBEDDING_DIM = 1024

# --- Chunking ---
HIERARCHICAL_PARENT_SIZE = 2048
HIERARCHICAL_CHILD_SIZE = 256
SEMANTIC_THRESHOLD = 0.85

# --- Search ---
BM25_TOP_K = 20
DENSE_TOP_K = 20
HYBRID_TOP_K = 20
RERANK_TOP_K = 3

# --- Paths ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TEST_SET_PATH = os.path.join(os.path.dirname(__file__), "test_set.json")
