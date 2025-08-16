from fonctions.embeddings import get_embedding
from fonctions.config import PERSIST_DIR, COLLECTION_NAME
from langchain_chroma import Chroma

def get_vectorstore():
    emb = get_embedding()
    vs = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(PERSIST_DIR),
        embedding_function=emb,
    )
    return vs

def retrieve_docs(vs, query: str, k: int = 8):
    try:
        return vs.max_marginal_relevance_search_with_score(
            query, k=k, fetch_k=max(40, k * 8), lambda_mult=0.1
        )
    except Exception:
        return vs.similarity_search_with_relevance_scores(query, k=k)
