from __future__ import annotations
import os
from pathlib import Path
from typing import List

from fonctions.config import DATA_DIR, PERSIST_DIR, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP
from fonctions.embeddings import get_embedding

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_chroma import Chroma

# --- Helpers ---

def _list_pdfs() -> List[Path]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return sorted(DATA_DIR.glob("*.pdf"))

def _load_text_docs(pdf_path: Path) -> List[Document]:
    loader = PyPDFLoader(str(pdf_path))
    docs = loader.load()  # chaque page = 1 Document, avec metadata 'source' et 'page'
    for d in docs:
        d.metadata = d.metadata or {}
        d.metadata.setdefault("type", "text")  # on marque texte
    return docs

def _load_tables_docs(pdf_path: Path) -> List[Document]:
    """Essaie d'extraire des tableaux avec Camelot. Si indisponible, renvoie []."""
    try:
        import camelot  # nécessite ghostscript/opencv selon OS
    except Exception:
        return []
    try:
        tables = camelot.read_pdf(str(pdf_path), pages="all", flavor="lattice")
    except Exception:
        try:
            tables = camelot.read_pdf(str(pdf_path), pages="all", flavor="stream")
        except Exception:
            return []

    docs: List[Document] = []
    for t in tables:
        text = t.df.to_csv(index=False)  # table -> csv texte (lisible pour le LLM)
        meta = {
            "source": str(pdf_path),
            "page": t.page,              # camelot renvoie page
            "type": "table_flat",
        }
        docs.append(Document(page_content=text, metadata=meta))
    return docs

def _split_docs(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks: List[Document] = []
    for d in docs:
        # ne pas re-splitter les tables CSV déjà concises
        if (d.metadata or {}).get("type") in ("table", "table_flat"):
            chunks.append(d)
        else:
            for c in splitter.split_documents([d]):
                c.metadata = c.metadata or {}
                c.metadata.setdefault("type", "text")
                chunks.append(c)
    return chunks

# --- Ingestion principale ---

def ingest_all_pdfs():
    pdfs = _list_pdfs()
    if not pdfs:
        raise FileNotFoundError(f"Aucun PDF trouvé dans {DATA_DIR.resolve()}")

    all_docs: List[Document] = []
    for pdf in pdfs:
        text_docs = _load_text_docs(pdf)
        table_docs = _load_tables_docs(pdf)  # peut être vide si Camelot indisponible
        all_docs.extend(text_docs + table_docs)

    chunks = _split_docs(all_docs)
    PERSIST_DIR.mkdir(parents=True, exist_ok=True)

    emb = get_embedding()
    vs = Chroma.from_documents(
        documents=chunks,
        embedding=emb,
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIR),
    )
    return vs
