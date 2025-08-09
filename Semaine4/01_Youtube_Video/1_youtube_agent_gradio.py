import gradio as gr
import asyncio
import re
import os
from datetime import datetime
from agents import Agent, function_tool, Runner
from openai.types.responses import ResponseTextDeltaEvent
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, TranscriptsDisabled,
    VideoUnavailable, CouldNotRetrieveTranscript
)

# Instructions de l'agent
AGENT_INSTRUCTIONS = (
    "Tu es un assistant expert en analyse de vidéos YouTube et en création de contenu. "
    "Lorsque l'utilisateur te donne une URL, commence par récupérer automatiquement la transcription de la vidéo. "
    "Analyse ensuite le contenu en identifiant les messages clés, le ton employé, les intentions de l'auteur, les cibles et les points marquants.\n\n"
    "Tu peux ensuite répondre à deux types de demandes :\n"
    "1. Poser des questions sur la vidéo : l'utilisateur peut te poser des questions précises pour mieux comprendre ou explorer le contenu.\n"
    "2. Générer des contenus pour les réseaux sociaux :\n"
    "   - Un post LinkedIn (800 à 1200 caractères), structuré, professionnel, avec une bonne accroche et un appel à l'action\n"
    "   - Un post Instagram (300 à 600 caractères), plus direct, percutant et adapté au ton de la plateforme.\n\n"
    "Adapte toujours le style et le ton à la plateforme cible. Si un message central fort ou un angle original se dégage, utilise-le comme fil conducteur."
)

# Outil pour récupérer les transcriptions YouTube
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

        # Méthode 1: Utiliser fetch() avec des langues prioritaires
        try:
            transcript_data = ytt_api.fetch(video_id, languages=['fr'])
            print("✅ Transcription française récupérée")
        except NoTranscriptFound:
            try:
                transcript_data = ytt_api.fetch(video_id, languages=['en'])
                print("✅ Transcription anglaise récupérée")
            except NoTranscriptFound:
                try:
                    # Sans spécifier de langue (défaut: anglais)
                    transcript_data = ytt_api.fetch(video_id)
                    print("✅ Transcription par défaut récupérée")
                except Exception as fetch_error:
                    print(f"🔄 fetch() a échoué: {str(fetch_error)}")
                    
                    # Méthode 2: Utiliser list() puis fetch() sur l'objet transcript
                    try:
                        print("🔄 Essai avec list() puis fetch()...")
                        transcript_list = ytt_api.list(video_id)
                        
                        # Essayer de trouver une transcription française ou anglaise
                        try:
                            transcript_obj = transcript_list.find_transcript(['fr', 'en'])
                            transcript_data = transcript_obj.fetch()
                            print(f"✅ Transcription {transcript_obj.language} trouvée via list()")
                        except NoTranscriptFound:
                            # Prendre la première transcription disponible
                            try:
                                available_transcripts = list(transcript_list)
                                if available_transcripts:
                                    first_transcript = available_transcripts[0]
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

        # Formatage de la transcription
        formatted_entries = []
        for entry in transcript_data:
            try:
                # Gestion des objets FetchedTranscriptSnippet
                if hasattr(entry, 'start') and hasattr(entry, 'text'):
                    # C'est un objet FetchedTranscriptSnippet
                    start = float(entry.start)
                    text = entry.text
                elif isinstance(entry, dict) and 'start' in entry and 'text' in entry:
                    # C'est un dictionnaire (ancien format)
                    start = float(entry['start'])
                    text = entry['text']
                else:
                    # Format inconnu, on essaie d'accéder aux attributs
                    start = getattr(entry, 'start', 0)
                    text = getattr(entry, 'text', str(entry))
                
                minutes = int(start // 60)
                seconds = int(start % 60)
                timestamp = f"[{minutes:02d}:{seconds:02d}]"
                formatted_entries.append(f"{timestamp} {text}")
            except Exception as e:
                print(f"⚠️ Erreur de parsing d'un snippet: {str(e)}")
                continue

        result = "\n".join(formatted_entries)
        print(f"✅ Transcription formatée: {len(formatted_entries)} snippets")
        return result

    except TranscriptsDisabled:
        return "❌ Les transcriptions sont désactivées pour cette vidéo."
    except VideoUnavailable:
        return "❌ Vidéo non disponible."
    except CouldNotRetrieveTranscript:
        return "❌ Impossible de récupérer la transcription pour cette vidéo."
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def create_agent():
    """Crée l'agent avec les instructions"""
    return Agent(
        name="YouTube Content Generator",
        instructions=AGENT_INSTRUCTIONS,
        tools=[fetch_youtube_transcript],
        model="gpt-4o"
    )

# Variables globales pour l'état de l'application
class AppState:
    def __init__(self):
        self.agent = None
        self.api_key = None
        self.current_video = None
        self.conversation_history = []
        self.session_start = datetime.now()

app_state = AppState()

def setup_agent(api_key):
    """Configure l'agent avec la clé API"""
    if not api_key or not api_key.strip():
        return "❌ Veuillez entrer une clé API", "🔴 Non configuré"
    
    if not api_key.startswith('sk-'):
        return "❌ Format invalide. La clé doit commencer par 'sk-'", "🔴 Erreur"
    
    try:
        os.environ['OPENAI_API_KEY'] = api_key.strip()
        app_state.api_key = api_key.strip()
        app_state.agent = create_agent()
        app_state.session_start = datetime.now()
        return f"✅ Agent configuré avec la clé sk-...{api_key[-8:]}", "🟢 Configuré"
    except Exception as e:
        return f"❌ Erreur lors de la configuration : {str(e)}", "🔴 Erreur"

def detect_youtube_url(text):
    """Détecte si le texte contient une URL YouTube"""
    youtube_pattern = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+'
    return bool(re.search(youtube_pattern, text))

def format_user_prompt(user_input):
    """Formate le prompt utilisateur avec des instructions contextuelles"""
    if detect_youtube_url(user_input):
        app_state.current_video = user_input
        return f"""Nouvelle vidéo YouTube à analyser : {user_input}

Instructions spéciales :
1. Récupère d'abord la transcription avec l'outil
2. Fais une analyse initiale rapide
3. Pose-moi 2-3 questions pertinentes pour approfondir
4. Sois proactif et engage la conversation !"""
    else:
        return user_input

async def chat_with_agent(message, history):
    """Fonction principale pour chatter avec l'agent"""
    if not app_state.agent:
        error_msg = "❌ Veuillez d'abord configurer votre clé API dans l'onglet Configuration."
        history.append([message, error_msg])
        yield history, ""
        return
    
    if not message.strip():
        yield history, ""
        return
    
    # Ajouter le message utilisateur à l'historique
    history.append([message, ""])
    
    # Préparer l'historique pour l'agent
    input_items = []
    for user_msg, ai_msg in history[:-1]:  # Exclure le dernier message (pas encore de réponse)
        if user_msg and ai_msg:
            input_items.append({"content": user_msg, "role": "user"})
            input_items.append({"content": ai_msg, "role": "assistant"})
    
    # Ajouter le message actuel
    formatted_input = format_user_prompt(message)
    input_items.append({"content": formatted_input, "role": "user"})
    
    # Limiter l'historique
    input_items = input_items[-12:]
    
    # Générer la réponse en streaming
    response = ""
    try:
        result = Runner.run_streamed(app_state.agent, input=input_items)
        
        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                response += event.data.delta
                # Mettre à jour l'historique avec la réponse partielle
                history[-1][1] = response
                yield history, ""
            
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    status_msg = "🔄 Récupération de la transcription YouTube..."
                    history[-1][1] = status_msg
                    yield history, ""
                
                elif event.item.type == "tool_call_output_item":
                    if any(emoji in event.item.output for emoji in ["⚠️", "❌"]):
                        error_msg = f"⚠️ Problème : {event.item.output}"
                        history[-1][1] = error_msg
                        yield history, ""
                    else:
                        success_msg = "✅ Transcription récupérée ! Analyse en cours...\n\n"
                        history[-1][1] = success_msg
                        yield history, ""
    
    except Exception as e:
        error_response = f"❌ Erreur lors de l'exécution : {str(e)}"
        history[-1][1] = error_response
        yield history, ""

def clear_conversation():
    """Efface l'historique de conversation"""
    app_state.conversation_history = []
    return []

def get_session_stats():
    """Retourne les statistiques de session"""
    if not app_state.session_start:
        return "📊 Aucune session active"
    
    duration = datetime.now() - app_state.session_start
    video_count = 1 if app_state.current_video else 0
    
    stats = f"""📊 **Statistiques de Session**
⏱️ Durée : {duration}
🎥 Vidéos analysées : {video_count}
🤖 Agent : {'✅ Actif' if app_state.agent else '❌ Non configuré'}
🔑 API : {'✅ Configurée' if app_state.api_key else '❌ Non configurée'}
"""
    
    if app_state.current_video:
        stats += f"📹 Vidéo actuelle : {app_state.current_video[:50]}..."
    
    return stats

# Interface Gradio
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
        
        # En-tête
        gr.HTML("""
        <div class="header-text">
            <h1 style="color: #2c3e50; font-size: 2.5em;">🎬 YouTube Transcript Agent</h1>
            <p style="color: #7f8c8d; font-size: 1.2em;">Analysez et discutez du contenu de vidéos YouTube avec une IA conversationnelle</p>
        </div>
        """)
        
        with gr.Tabs():
            # Onglet principal - Chat
            with gr.Tab("💬 Chat avec l'IA"):
                with gr.Row():
                    with gr.Column(scale=3):
                        chatbot = gr.Chatbot(
                            label="🤖 Conversation avec l'Agent YouTube",
                            height=500,
                            show_copy_button=True,
                            bubble_full_width=False,
                            avatar_images=("🧑", "🤖")
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="💭 Votre message",
                                placeholder="Collez une URL YouTube ou posez une question...",
                                scale=4,
                                lines=2
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
            
            # Onglet configuration
            with gr.Tab("🔧 Configuration"):
                with gr.Row():
                    with gr.Column():
                        gr.HTML("""
                        <div class="config-box">
                            <h3>🔑 Configuration de la Clé API OpenAI</h3>
                            <p>Obtenez votre clé API sur <a href="https://platform.openai.com/api-keys" target="_blank">platform.openai.com</a></p>
                        </div>
                        """)
                        
                        api_key_input = gr.Textbox(
                            label="🔐 Clé API OpenAI",
                            placeholder="sk-...",
                            type="password",
                            lines=1
                        )
                        
                        config_btn = gr.Button("✅ Configurer Agent", variant="primary", size="lg")
                        config_status = gr.Textbox(
                            label="📋 Statut de Configuration",
                            interactive=False,
                            lines=2
                        )
            
            # Onglet aide
            with gr.Tab("❓ Aide"):
                gr.Markdown("""
                # 🎯 Guide d'Utilisation
                
                ## 📋 Étapes pour commencer :
                1. **🔧 Configuration** : Allez dans l'onglet Configuration et entrez votre clé API OpenAI
                2. **💬 Chat** : Retournez à l'onglet Chat pour commencer à discuter
                3. **🎥 Analyse** : Collez une URL YouTube ou posez des questions
                
                ## 🚀 Fonctionnalités :
                - **🎬 Analyse de vidéos** : Collez n'importe quelle URL YouTube
                - **💭 Chat interactif** : Posez des questions sur le contenu
                - **⚡ Réponses en temps réel** : Streaming des réponses de l'IA
                - **🧠 Mémoire conversationnelle** : L'IA se souvient de vos échanges
                - **📊 Statistiques** : Suivez votre session d'analyse
                
                ## 💡 Exemples d'interactions :
                - "Analyse cette vidéo : https://youtube.com/watch?v=..."
                - "Résume-moi les points clés"
                - "Qu'est-ce qui est dit vers la 5ème minute ?"
                - "L'auteur mentionne-t-il [sujet] ?"
                - "Quelles sont les conclusions principales ?"
                
                ## 🔒 Sécurité :
                - Votre clé API n'est jamais sauvegardée
                - Elle reste privée pendant votre session
                - Aucune donnée n'est stockée de manière permanente
                """)
        
        # Événements
        config_btn.click(
            fn=setup_agent,
            inputs=[api_key_input],
            outputs=[config_status, status_display]
        )
        
        send_btn.click(
            fn=chat_with_agent,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        msg_input.submit(
            fn=chat_with_agent,
            inputs=[msg_input, chatbot],
            outputs=[chatbot, msg_input]
        )
        
        clear_btn.click(
            fn=clear_conversation,
            outputs=[chatbot]
        )
        
        stats_btn.click(
            fn=get_session_stats,
            outputs=[stats_display]
        )
        
        # Exemples
        gr.Examples(
            examples=[
                ["Salut ! Peux-tu analyser cette vidéo pour moi ?"],
                ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                ["Résume-moi les points clés de cette vidéo"],
                ["Qu'est-ce qui est dit vers la 3ème minute ?"],
                ["L'auteur mentionne-t-il des exemples concrets ?"]
            ],
            inputs=[msg_input],
            label="💡 Exemples d'interactions"
        )
    
    return app

if __name__ == "__main__":
    # Créer et lancer l'application
    app = create_interface()
    
    # Configuration de lancement
    app.queue(default_concurrency_limit=5)  # Support multi-utilisateurs
    app.launch(
        server_name="0.0.0.0",    # Accessible depuis le réseau
        server_port=7860,         # Port standard
        share=True,               # Lien public temporaire
        show_error=True,          # Afficher les erreurs
        show_api=False,           # Cacher l'API documentation
        favicon_path=None,        # Pas d'icône personnalisée
        ssl_verify=False          # Pour éviter les problèmes SSL
    )
    
    print("🚀 Application lancée !")
    print("🌐 Interface accessible sur http://localhost:7860")
    print("🔗 Lien public généré automatiquement pour le partage")