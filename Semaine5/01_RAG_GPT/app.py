import os
import re
import html
import gradio as gr

from fonctions.config import TOP_K
from fonctions.rag_pipeline import RAGPipeline

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Init pipeline
PIPELINE = None
INIT_ERROR = None
try:
    PIPELINE = RAGPipeline(top_k=TOP_K)
except Exception as e:
    INIT_ERROR = str(e)

def _messages_to_pairs(msgs):
    if not msgs:
        return []
    pairs, buf_user = [], None
    for m in msgs:
        role = (m.get("role") or "").lower()
        content = m.get("content") or ""
        if role == "user":
            if buf_user is not None:
                pairs.append((buf_user, ""))
            buf_user = content
        elif role == "assistant":
            if buf_user is None:
                continue
            pairs.append((buf_user, content))
            buf_user = None
    if buf_user is not None:
        pairs.append((buf_user, ""))
    return pairs

def clean_table_noise(text: str) -> str:
    if not text:
        return ""
    t = text
    t = re.sub(r'([A-Za-z])\s*\|\s*([A-Za-z])', r'\1\2', t)  # recolle mots
    t = re.sub(r'\s*\|\s*', ' ', t)                          # retire pipes
    t = re.sub(r'[ \t]{2,}', ' ', t)
    t = re.sub(r'\n{2,}', '\n', t)
    return t.strip()

def first_sentences(text: str, max_sentences: int = 2) -> str:
    t = (text or "").strip().replace("\n", " ")
    parts = re.split(r'(?<=[\.\!\?])\s+', t)
    out = " ".join(parts[:max_sentences]).strip()
    return out if out else t[:400]

def build_sources_md(hits, display_mode: str = "Détaillé", clean: bool = True) -> str:
    if not hits:
        return "_Aucune source à afficher._"
    lines = ["### 📚 Sources récupérées", ""]
    for i, h in enumerate(hits, start=1):
        page = h.get("page", "?")
        score = float(h.get("score", 0.0))
        src = h.get("source") or ""
        typ = h.get("type") or ""
        fname = os.path.basename(src) if src else "document"
        raw = h.get("text") or ""
        snippet = clean_table_noise(raw) if clean else raw
        snippet = first_sentences(snippet, 2)
        snippet = html.escape(snippet)
        head = f"p. {page} — {fname}"
        if typ:
            head += f" — {typ}"
        head += f" — score {score:.3f}"
        if display_mode == "Minimal":
            lines.append(f"- **{head}**")
        elif display_mode == "Compact":
            lines.append(f"**{i}. {head}**\n\n> {snippet}\n")
        else:
            lines.append(
                f"<details><summary><strong>{i}. {head}</strong></summary>\n\n"
                f"<blockquote style='margin:8px 0'>{snippet}</blockquote>\n"
                f"</details>"
            )
    return "\n\n".join(lines)

def submit_message(user_msg, chat_messages, top_k, display_mode, clean_extracts):
    if INIT_ERROR:
        err = f"⚠️ Initialisation impossible :\n\n> {INIT_ERROR}\n\nAssure-toi d'avoir `OPENAI_API_KEY`."
        chat_messages = chat_messages + [
            {"role": "user", "content": (user_msg or '').strip()},
            {"role": "assistant", "content": err},
        ]
        return "", chat_messages, chat_messages, "_Erreur d’init_"

    q = (user_msg or "").strip()
    if not q:
        return "", chat_messages, chat_messages, "_Saisis une question pour commencer._"

    try:
        PIPELINE.top_k = int(top_k)
        history_pairs = _messages_to_pairs(chat_messages)
        result = PIPELINE.answer(q, history_pairs)
    except Exception as e:
        err = f"❌ Erreur pendant l’inférence : {e}"
        chat_messages = chat_messages + [
            {"role": "user", "content": q},
            {"role": "assistant", "content": err},
        ]
        return "", chat_messages, chat_messages, "_Erreur pendant l’inférence_"

    answer = result.get("answer", "Aucun passage pertinent trouvé.")
    hits = result.get("hits", [])
    sources_md = build_sources_md(hits, display_mode=display_mode, clean=bool(clean_extracts))

    chat_messages = chat_messages + [
        {"role": "user", "content": q},
        {"role": "assistant", "content": answer},
    ]
    return "", chat_messages, chat_messages, sources_md

def clear_chat():
    return [], [], ""

theme = gr.themes.Soft(primary_hue="blue", neutral_hue="gray")

custom_css = """
#app-title h1 { margin: 0; }
#app-subtitle { color: #6b7280; margin-top: 4px; }
.gradio-container { max-width: 1200px !important; }
.card {
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: 14px;
  padding: 14px;
  background: white;
  box-shadow: 0 1px 8px rgba(10, 37, 64, 0.04);
}
"""

with gr.Blocks(theme=theme, css=custom_css) as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown(
                "<div id='app-title'><h1>📈 Tesla Q1 2023 — Analyste Financier IA</h1></div>"
                "<div id='app-subtitle'>Q&A financier sur le rapport trimestriel (RAG sur texte + tableaux)</div>",
                elem_classes=["card"]
            )

    with gr.Row():
        with gr.Column(scale=7):
            chatbot = gr.Chatbot(label="Assistant financier", type="messages", height=520, elem_classes=["card"])
            with gr.Row():
                user_box = gr.Textbox(placeholder="Ex: Quel est le Total revenues au T1 2023 ?", label="Question", lines=1, scale=6)
                send_btn = gr.Button("Envoyer", variant="primary", scale=1)
                clear_btn = gr.Button("Effacer", variant="secondary", scale=1)

        with gr.Column(scale=5):
            with gr.Group(elem_classes=["card"]):
                gr.Markdown("### ⚙️ Paramètres")
                top_k = gr.Slider(label="k (documents)", minimum=1, maximum=12, step=1, value=TOP_K)
                display_mode = gr.Radio(["Minimal", "Compact", "Détaillé"], label="Affichage des sources", value="Détaillé")
                clean_extracts = gr.Checkbox(value=True, label="Nettoyer les extraits (recommandé)")
                gr.Markdown("Astuce : **Détaillé** pour inspecter, **Compact/Minimal** pour un rendu léger.")
            with gr.Group(elem_classes=["card"]):
                sources_md = gr.Markdown("— Aucune source —", elem_id="sources-md")

    messages_state = gr.State([])

    send_btn.click(
        submit_message,
        inputs=[user_box, messages_state, top_k, display_mode, clean_extracts],
        outputs=[user_box, messages_state, chatbot, sources_md],
    )
    user_box.submit(
        submit_message,
        inputs=[user_box, messages_state, top_k, display_mode, clean_extracts],
        outputs=[user_box, messages_state, chatbot, sources_md],
    )
    clear_btn.click(
        clear_chat,
        inputs=[],
        outputs=[messages_state, chatbot, sources_md],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
