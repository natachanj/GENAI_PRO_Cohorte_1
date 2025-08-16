from typing import List, Tuple, Dict, Any
import os

from fonctions.config import TOP_K, LLM_BACKEND, OPENAI_MODEL
from fonctions.retrieval import get_vectorstore
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

SYSTEM_PROMPT = """Tu es un analyste financier expert spécialisé dans l'analyse des résultats trimestriels d'entreprise.
Tu analyses et synthétises les données financières du rapport fourni (texte, tableaux, OCR).
Réponds toujours en français, de manière claire, précise et chiffrée lorsque c'est possible.
Cite les pages entre crochets, ex: [p. 4, 6].
Si l'information n'est pas dans le contexte, dis-le explicitement."""

USER_PROMPT_QA = """Question:
{question}

Historique:
{history}

Contexte:
{context}

Consignes:
- Appuie-toi uniquement sur le contexte.
- Donne les valeurs exactes lorsqu'elles apparaissent (montants, marges, volumes, etc.).
- Si l'information n'est pas disponible dans le contexte, dis-le clairement.
"""

def _load_llm() -> ChatOpenAI:
    if LLM_BACKEND != "openai":
        raise ValueError(f"Backend LLM non supporté: {LLM_BACKEND}. Utilisez 'openai'.")
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY manquante pour le backend OpenAI.")
    return ChatOpenAI(model=OPENAI_MODEL, temperature=0.1)

def _normalize_score(s: float) -> float:
    if s < 0:
        s = (s + 1.0) / 2.0
    elif s > 1:
        s = 1.0 / (1.0 + s)
    return max(0.0, min(1.0, s))

class RAGPipeline:
    def __init__(self, top_k: int = TOP_K):
        self.vs = get_vectorstore()
        self.top_k = top_k
        self.llm = _load_llm()
        self._qa_prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("user", USER_PROMPT_QA),
        ])
        self._parser = StrOutputParser()

    # --- Retriever "table-first" ---
    def retrieve(self, query: str) -> List[Tuple[Document, float]]:
        hits: List[Tuple[Document, float]] = []

        # 1) d'abord les tableaux (si filtre supporté)
        try:
            tab_raw = self.vs.similarity_search_with_relevance_scores(
                query,
                k=self.top_k,
                filter={"type": {"$in": ["table", "table_flat"]}},
            )
            hits.extend(tab_raw)
        except Exception:
            pass

        # 2) compléter avec recherche générale
        if len(hits) < self.top_k:
            try:
                mmr_raw = self.vs.max_marginal_relevance_search_with_score(
                    query, k=self.top_k, fetch_k=max(40, self.top_k * 8), lambda_mult=0.1
                )
                hits.extend(mmr_raw)
            except Exception:
                sim_raw = self.vs.similarity_search_with_relevance_scores(query, k=self.top_k)
                hits.extend(sim_raw)

        # 3) dédup + normalisation + tri
        dedup: Dict[tuple, Tuple[Document, float]] = {}
        for doc, sc in hits:
            meta = doc.metadata or {}
            key = (meta.get("source"), meta.get("page"), (doc.page_content or "")[:120])
            if key not in dedup:
                dedup[key] = (doc, sc)

        out: List[Tuple[Document, float]] = []
        for doc, sc in dedup.values():
            out.append((doc, _normalize_score(sc)))

        out.sort(key=lambda x: x[1], reverse=True)
        return out[: self.top_k]

    def _format_history(self, history_pairs: List[Tuple[str, str]], max_turns: int = 6) -> str:
        if not history_pairs:
            return "—"
        clipped = history_pairs[-max_turns:]
        lines = []
        for u, a in clipped:
            u = (u or "").strip()
            a = (a or "").strip()
            if u:
                lines.append(f"Utilisateur: {u}")
            if a:
                lines.append(f"Assistant: {a}")
        return "\n".join(lines) if lines else "—"

    def answer(self, question: str, history_pairs: List[Tuple[str, str]] | None = None) -> Dict[str, Any]:
        hits = self.retrieve(question)
        if not hits:
            return {"answer": "Aucun passage pertinent trouvé.", "pages": [], "hits": []}

        def _fmt(doc: Document) -> str:
            txt = (doc.page_content or "").strip()
            typ = (doc.metadata or {}).get("type", "text")
            if typ not in ("table", "table_flat") and len(txt) > 1600:
                txt = txt[:1600] + " ..."
            return f"(p. {doc.metadata.get('page')}) {txt}"

        context = "\n\n".join([_fmt(h[0]) for h in hits])
        pages = sorted({
            h[0].metadata.get('page')
            for h in hits
            if (h[0].metadata or {}).get('page') is not None
        })
        hist = self._format_history(history_pairs or [])

        chain = self._qa_prompt | self.llm | self._parser
        answer = chain.invoke({"question": question, "context": context, "history": hist})

        return {
            "answer": answer,
            "pages": pages,
            "hits": [{
                "page": h[0].metadata.get("page"),
                "text": h[0].page_content,
                "score": float(h[1]),
                "source": h[0].metadata.get("source"),
                "type": h[0].metadata.get("type"),
            } for h in hits]
        }
