import gradio as gr
import asyncio
import re
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from agents import Agent, function_tool, Runner
from openai.types.responses import ResponseTextDeltaEvent
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, TranscriptsDisabled,
    VideoUnavailable, CouldNotRetrieveTranscript
)

# -----------------------------------
# Chargement .env (OPENAI / Gmail)
# -----------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass  # facultatif si tu n'utilises pas python-dotenv

# -----------------------------------
# Config Gmail via .env
# GMAIL_EMAIL, GMAIL_APP_PASSWORD
# -----------------------------------
GMAIL_CONFIG = {
    "email": os.getenv("GMAIL_EMAIL", "").strip(),
    "password": os.getenv("GMAIL_APP_PASSWORD", "").strip(),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
}

# -----------------------------------
# Instructions de l'agent
# -----------------------------------
AGENT_INSTRUCTIONS = (
    "Tu es un assistant expert en analyse de vidéos YouTube et en création de contenu. "
    "Lorsque l'utilisateur te donne une URL, commence par récupérer automatiquement la transcription de la vidéo. "
    "Analyse ensuite le contenu en identifiant les messages clés, le ton employé, les intentions de l'auteur, les cibles et les points marquants.\n\n"
    "Tu peux ensuite répondre à trois types de demandes :\n"
    "1. Poser des questions sur la vidéo : l'utilisateur peut te poser des questions précises pour mieux comprendre ou explorer le contenu.\n"
    "2. Générer des contenus pour les réseaux sociaux :\n"
    "   - Un post LinkedIn (800 à 1200 caractères), structuré, professionnel, avec une bonne accroche et un appel à l'action\n"
    "   - Un post Instagram (300 à 600 caractères), plus direct, percutant et adapté au ton de la plateforme.\n"
    "3. Envoyer les résultats par email :\n"
    "   - L'utilisateur peut demander d'envoyer l'analyse ou tout autre contenu généré par email\n"
    "   - Utilise la fonction send_gmail_email en spécifiant le destinataire, le sujet et le contenu\n"
    "   - Formate le contenu de manière professionnelle avec du HTML si nécessaire\n\n"
    "Adapte toujours le style et le ton à la plateforme cible. Si un message central fort ou un angle original se dégage, utilise-le comme fil conducteur."
)

# -----------------------------------
# Outil: transcript YouTube
# -----------------------------------
@function_tool
def fetch_youtube_transcript(url: str) -> str:
    """Récupère la transcription d'une vidéo YouTube avec timestamps"""
    video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(video_id_pattern, url)
    if not match:
        return "⚠️ URL YouTube invalide."

    video_id = match.group(1)
    print(f"🎥 Récupération de la transcription pour: {video_id}")

    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = None

        # Méthode 1: fetch() fr -> en -> default
        try:
            transcript_data = ytt_api.fetch(video_id, languages=['fr'])
            print("✅ Transcription française récupérée")
        except NoTranscriptFound:
            try:
                transcript_data = ytt_api.fetch(video_id, languages=['en'])
                print("✅ Transcription anglaise récupérée")
            except NoTranscriptFound:
                try:
                    transcript_data = ytt_api.fetch(video_id)
                    print("✅ Transcription par défaut récupérée")
                except Exception as fetch_error:
                    print(f"🔄 fetch() a échoué: {str(fetch_error)}")
                    # Méthode 2: list() -> fetch()
                    try:
                        print("🔄 Essai avec list() puis fetch()...")
                        transcript_list = ytt_api.list(video_id)
                        try:
                            transcript_obj = transcript_list.find_transcript(['fr', 'en'])
                            transcript_data = transcript_obj.fetch()
                            print(f"✅ Transcription {transcript_obj.language} trouvée via list()")
                        except NoTranscriptFound:
                            try:
                                available = list(transcript_list)
                                if available:
                                    first_transcript = available[0]
                                    transcript_data = first_transcript.fetch()
                                    print(f"✅ Première transcription disponible: {first_transcript.language}")
                                else:
                                    return "❌ Aucune transcription trouvée pour cette vidéo"
                            except Exception as list_fetch_error:
                                return f"❌ Erreur lors de fetch() sur transcript: {str(list_fetch_error)}"
                    except Exception as list_error:
                        return f"❌ Erreur list(): {str(list_error)}"

        if not transcript_data:
            return "❌ Aucune donnée de transcription récupérée"

        # Formatage
        formatted_entries = []
        for entry in transcript_data:
            try:
                if hasattr(entry, 'start') and hasattr(entry, 'text'):
                    start = float(entry.start); text = entry.text
                elif isinstance(entry, dict) and 'start' in entry and 'text' in entry:
                    start = float(entry['start']); text = entry['text']
                else:
                    start = float(getattr(entry, 'start', 0)); text = getattr(entry, 'text', str(entry))
                minutes = int(start // 60); seconds = int(start % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                formatted_entries.append(f"{timestamp} {text}")
            except Exception as e:
                print(f"⚠️ Erreur de parsing d'un snippet: {str(e)}")
                continue

        result = "\n".join(formatted_entries)
        print(f"✅ Transcription formatée: {len(formatted_entries)} snippets")
        app_state.last_transcript = result  # mémorise pour envoi manuel
        return result

    except TranscriptsDisabled:
        return "❌ Les transcriptions sont désactivées pour cette vidéo."
    except VideoUnavailable:
        return "❌ Vidéo non disponible."
    except CouldNotRetrieveTranscript:
        return "❌ Impossible de récupérer la transcription pour cette vidéo."
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

# -----------------------------------
# Outil: envoi email Gmail
# -----------------------------------
@function_tool
def send_gmail_email(recipient_email: str, subject: str, content: str, is_html: bool = False) -> str:
    """
    Envoie un email via Gmail (SMTP + mot de passe d'application).
    """
    if not GMAIL_CONFIG["email"] or not GMAIL_CONFIG["password"]:
        return "❌ Configuration Gmail manquante. Renseigne GMAIL_EMAIL et GMAIL_APP_PASSWORD dans le .env."

    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = GMAIL_CONFIG["email"]
        msg["To"] = recipient_email
        msg["Subject"] = subject

        if is_html:
            # Ajoute une version texte simple minimale
            plain = MIMEText("Version texte :\n" + re.sub("<.*?>", "", content), "plain", "utf-8")
            html = MIMEText(content, "html", "utf-8")
            msg.attach(plain)
            msg.attach(html)
        else:
            msg.attach(MIMEText(content, "plain", "utf-8"))

        with smtplib.SMTP(GMAIL_CONFIG["smtp_server"], GMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(GMAIL_CONFIG["email"], GMAIL_CONFIG["password"])
            server.send_message(msg)

        return f"✅ Email envoyé avec succès à {recipient_email}"

    except smtplib.SMTPAuthenticationError:
        return "❌ Erreur d'authentification Gmail. Vérifie GMAIL_EMAIL et GMAIL_APP_PASSWORD."
    except smtplib.SMTPException as e:
        return f"❌ Erreur SMTP : {str(e)}"
    except Exception as e:
        return f"❌ Erreur lors de l'envoi de l'email : {str(e)}"

# -----------------------------------
# Agent
# -----------------------------------
def create_agent():
    return Agent(
        name="YouTube Content Generator",
        instructions=AGENT_INSTRUCTIONS,
        tools=[fetch_youtube_transcript, send_gmail_email],
        model="gpt-4o"
    )

# -----------------------------------
# État global
# -----------------------------------
class AppState:
    def __init__(self):
        self.agent = None
        self.api_key = None
        self.current_video = None
        self.conversation_history = []
        self.session_start = datetime.now()
        self.last_transcript = None
        self.gmail_configured = bool(GMAIL_CONFIG["email"] and GMAIL_CONFIG["password"])

app_state = AppState()

# -----------------------------------
# Setup API
# -----------------------------------
def setup_agent(api_key):
    if not api_key or not api_key.strip():
        return "❌ Veuillez entrer une clé API", "🔴 Non configuré"
    if not api_key.startswith('sk-'):
        return "❌ Format invalide. La clé doit commencer par 'sk-'", "🔴 Erreur"

    try:
        os.environ['OPENAI_API_KEY'] = api_key.strip()
        app_state.api_key = api_key.strip()
        app_state.agent = create_agent()
        app_state.session_start = datetime.now()
        gmail_status = "✅" if app_state.gmail_configured else "⚠️"
        return f"✅ Agent configuré avec la clé sk-...{api_key[-8:]}", f"🟢 Configuré | Gmail: {gmail_status}"
    except Exception as e:
        return f"❌ Erreur lors de la configuration : {str(e)}", "🔴 Erreur"

# -----------------------------------
# Helpers chat
# -----------------------------------
def detect_youtube_url(text):
    pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return bool(re.search(pattern, text))

def format_user_prompt(user_input):
    if detect_youtube_url(user_input):
        app_state.current_video = user_input
        return f"""Nouvelle vidéo YouTube à analyser : {user_input}

Instructions spéciales :
1. Récupère d'abord la transcription avec l'outil
2. Fais une analyse initiale rapide
3. Pose-moi 2-3 questions pertinentes pour approfondir
4. Sois proactif et engage la conversation !"""
    return user_input

# -----------------------------------
# Chat (streaming)
# -----------------------------------
async def chat_with_agent(message, history):
    if not app_state.agent:
        error_msg = "❌ Veuillez d'abord configurer votre clé API dans l'onglet Configuration."
        history.append([message, error_msg])
        yield history, ""
        return

    if not message.strip():
        yield history, ""
        return

    history.append([message, ""])

    input_items = []
    for user_msg, ai_msg in history[:-1]:
        if user_msg and ai_msg:
            input_items.append({"content": user_msg, "role": "user"})
            input_items.append({"content": ai_msg, "role": "assistant"})

    formatted_input = format_user_prompt(message)
    input_items.append({"content": formatted_input, "role": "user"})
    input_items = input_items[-12:]

    response = ""
    try:
        result = Runner.run_streamed(app_state.agent, input=input_items)
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response += event.data.delta
                history[-1][1] = response
                yield history, ""
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    # feedback visuel simple
                    if "send_gmail_email" in str(event.item):
                        history[-1][1] = "📧 Envoi de l'email en cours..."
                    else:
                        history[-1][1] = "🔄 Récupération de la transcription YouTube..."
                    yield history, ""
                elif event.item.type == "tool_call_output_item":
                    if any(emoji in event.item.output for emoji in ["⚠️", "❌"]):
                        history[-1][1] = f"⚠️ Problème : {event.item.output}"
                    elif "✅ Email envoyé" in event.item.output:
                        history[-1][1] = "📧 Email envoyé avec succès !"
                    else:
                        history[-1][1] = "✅ Transcription récupérée ! Analyse en cours...\n"
                    yield history, ""
    except Exception as e:
        history[-1][1] = f"❌ Erreur lors de l'exécution : {str(e)}"
        yield history, ""

def clear_conversation():
    app_state.conversation_history = []
    return []

def get_session_stats():
    if not app_state.session_start:
        return "📊 Aucune session active"
    duration = datetime.now() - app_state.session_start
    video_count = 1 if app_state.current_video else 0
    stats = f"""📊 **Statistiques de Session**
⏱️ Durée : {duration}
🎥 Vidéos analysées : {video_count}
🤖 Agent : {'✅ Actif' if app_state.agent else '❌ Non configuré'}
🔑 API : {'✅ Configurée' if app_state.api_key else '❌ Non configurée'}
📧 Gmail : {'✅ Configuré' if app_state.gmail_configured else '❌ Non configuré'}"""
    if app_state.current_video:
        stats += f"\n📹 Vidéo actuelle : {app_state.current_video[:50]}..."
    return stats

# -----------------------------------
# UI Gradio
# -----------------------------------
def create_interface():
    with gr.Blocks(
        title="🎬 YouTube Transcript Agent",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container { max-width: 1200px !important; }
        .header-text { text-align: center; margin-bottom: 20px; }
        .config-box { background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; }
        """
    ) as app:

        gr.HTML("""
        <div class="header-text">
            <h1 style="color: #2c3e50; font-size: 2.2em;">🎬 YouTube Transcript Agent</h1>
            <p style="color: #7f8c8d;">Analyse YouTube + envoi par email (Gmail SMTP)</p>
        </div>
        """)

        with gr.Tabs():
            # Chat
            with gr.Tab("💬 Chat avec l'IA"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="🤖 Conversation",
                            height=520,
                            show_copy_button=True,
                            bubble_full_width=False
                        )
                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="💭 Votre message",
                                placeholder="Collez une URL YouTube, posez une question, ou dites: 'envoie ça par email à ...'",
                                scale=4, lines=2
                            )
                            send_btn = gr.Button("📤 Envoyer", variant="primary", scale=1)
                        with gr.Row():
                            clear_btn = gr.Button("🗑️ Effacer chat", variant="secondary")
                            stats_btn = gr.Button("📊 Statistiques", variant="secondary")

                    with gr.Column(scale=1):
                        status_display = gr.Textbox(
                            label="📊 Statut",
                            value="🔴 Agent non configuré",
                            interactive=False,
                            lines=3
                        )
                        stats_display = gr.Markdown(
                            value="📊 Configurez d'abord votre clé API",
                            label="📈 Statistiques"
                        )

            # Configuration
            with gr.Tab("🔧 Configuration"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""
                        <div class="config-box">
                            <h3>🔑 Clé API OpenAI</h3>
                            <p>Placez <code>OPENAI_API_KEY</code> dans votre fichier <code>.env</code> puis collez-le ci-dessous une seule fois pour initialiser l’agent.</p>
                        </div>
                        """)
                        api_key_input = gr.Textbox(
                            label="🔐 Clé API OpenAI",
                            placeholder="sk-...",
                            type="password",
                            lines=1
                        )
                        config_btn = gr.Button("✅ Configurer Agent", variant="primary", size="lg")
                        config_status = gr.Textbox(label="📋 Statut", interactive=False, lines=2)

                        gr.HTML(f"""
                        <div class="config-box" style="margin-top: 24px;">
                            <h3>📧 Gmail (auto-config via .env)</h3>
                            <ul>
                                <li><b>GMAIL_EMAIL</b>: {'✅ détecté' if GMAIL_CONFIG['email'] else '❌ manquant'}</li>
                                <li><b>GMAIL_APP_PASSWORD</b>: {'✅ détecté' if GMAIL_CONFIG['password'] else '❌ manquant'}</li>
                            </ul>
                            <p>Éditez votre <code>.env</code> si besoin, puis relancez l'app.</p>
                        </div>
                        """)

            # Aide
            with gr.Tab("❓ Aide"):
                gr.Markdown("""
                ### Exemples
                - "Analyse cette vidéo : https://www.youtube.com/watch?v=..."
                - "Résume-moi les points clés"
                - "Envoie l'analyse à contact@exemple.com avec le sujet 'Analyse du jour'"
                - "Crée un post LinkedIn de 900 caractères"

                **Astuce :** pour envoyer par email, l'agent appelle `send_gmail_email(recipient_email, subject, content, is_html=False)`.
                """)

        # Events
        config_btn.click(fn=setup_agent, inputs=[api_key_input], outputs=[config_status, status_display])

        send_btn.click(fn=chat_with_agent, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
        msg_input.submit(fn=chat_with_agent, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])

        clear_btn.click(fn=clear_conversation, outputs=[chatbot])
        stats_btn.click(fn=get_session_stats, outputs=[stats_display])

        gr.Examples(
            examples=[
                ["Salut ! Peux-tu analyser cette vidéo pour moi ?"],
                ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                ["Résume-moi les points clés de cette vidéo"],
                ["Envoie cette analyse par email à contact@exemple.com (sujet: Analyse YouTube)"],
                ["Qu'est-ce qui est dit vers la 3ème minute ?"]
            ],
            inputs=[msg_input],
            label="💡 Exemples d'interactions"
        )

    return app

# -----------------------------------
# Main
# -----------------------------------
if __name__ == "__main__":
    app = create_interface()
    app.queue(default_concurrency_limit=5)
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True,
        show_error=True,
        show_api=False,
        favicon_path=None,
        ssl_verify=False
    )
    print("🚀 Application lancée !")
    print("🌐 http://localhost:7860")
    print("📧 Gmail:", "OK" if app_state.gmail_configured else "manquant (vérifie .env : GMAIL_EMAIL / GMAIL_APP_PASSWORD)")
