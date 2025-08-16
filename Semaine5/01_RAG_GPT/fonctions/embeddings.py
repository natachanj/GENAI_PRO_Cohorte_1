from fonctions.config import OPENAI_EMBEDDING_MODEL, EMBEDDING_BACKEND, HF_EMB_MODEL
from langchain_openai import OpenAIEmbeddings

# Optionnel : support HF si tu repasses dessus plus tard
def get_embedding():
    if EMBEDDING_BACKEND == "openai":
        return OpenAIEmbeddings(model=OPENAI_EMBEDDING_MODEL)
    # fallback HF (évite l'erreur si jamais la var change)
    from langchain_huggingface import HuggingFaceEmbeddings
    return HuggingFaceEmbeddings(
        model_name=HF_EMB_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
