import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Chargement .env
_here = Path(__file__).resolve().parent.parent
_env_local = _here / ".env"
if _env_local.exists():
    load_dotenv(_env_local, override=True)
else:
    load_dotenv(find_dotenv(usecwd=True), override=True)

# Dossiers
DATA_DIR = _here / "data"
PERSIST_DIR = Path(".chroma")        # unique pour notebook ET app
COLLECTION_NAME = "pdf_collection"

# Backends
EMBEDDING_BACKEND = os.getenv("EMBEDDING_BACKEND", "openai").lower()  # openai | hf
LLM_BACKEND = os.getenv("LLM_BACKEND", "openai").lower()

# Modèles OpenAI
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# (optionnel) HF si jamais tu le veux plus tard
HF_EMB_MODEL = os.getenv("SENTENCE_TRANSFORMERS_MODEL", "all-MiniLM-L6-v2")

# Retrieval
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
TOP_K = int(os.getenv("TOP_K", "8"))

# OCR / Tables (facultatif)
ENABLE_OCR = os.getenv("ENABLE_OCR", "true").lower() in ["1", "true", "yes", "on"]
OCR_MIN_TEXT_CHARS = int(os.getenv("OCR_MIN_TEXT_CHARS", "120"))
POPPLER_PATH = os.getenv("POPPLER_PATH", "") or None
TESSERACT_CMD = os.getenv("TESSERACT_CMD", "") or None
