import streamlit as st
import re
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound, TranscriptsDisabled,
    VideoUnavailable, CouldNotRetrieveTranscript
)
from agents import Agent, function_tool, Runner
from openai.types.responses import ResponseTextDeltaEvent
import asyncio

# Chargement de la clé API depuis le fichier .env
load_dotenv()

# Configuration de l'interface Streamlit
st.set_page_config(page_title="YouTube Transcript Agent", page_icon="📽", layout="centered")
st.title("📽 YouTube Transcript Agent")
st.markdown("Posez une question sur une vidéo YouTube ou analysez son contenu à partir de son URL.")

# Fonction outil
@function_tool
def fetch_youtube_transcript(url: str) -> str:
    video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(video_id_pattern, url)

    if not match:
        return "URL YouTube invalide."

    video_id = match.group(1)

    try:
        transcript = YouTubeTranscriptApi().fetch(video_id)
        formatted_entries = []
        for entry in transcript:
            minutes = int(entry.start // 60)
            seconds = int(entry.start % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            text = entry.text
            formatted_entries.append(f"{timestamp} {text}")
        return "\n".join(formatted_entries)

    except TranscriptsDisabled:
        return "Les transcriptions sont désactivées pour cette vidéo."
    except NoTranscriptFound:
        return "Aucune transcription disponible pour cette vidéo."
    except VideoUnavailable:
        return "Vidéo non disponible ou privée."
    except CouldNotRetrieveTranscript:
        return "Impossible de récupérer la transcription pour le moment."
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"

# Création de l'agent
agent = Agent(
    name="YouTube Transcript Agent",
    instructions=(
        "Tu es un assistant qui aide à analyser le contenu de vidéos YouTube. "
        "Quand une URL est fournie, commence par récupérer la transcription à l'aide de l'outil."
    ),
    tools=[fetch_youtube_transcript],
    model="gpt-4o"
)

# Zone de saisie utilisateur
url_input = st.text_input("URL YouTube")
question_input = st.text_area("Votre question", height=100)

if st.button("Analyser"):
    if not url_input.strip():
        st.warning("Merci de fournir une URL YouTube.")
    elif not question_input.strip():
        st.warning("Merci de poser une question.")
    else:
        input_items = [
            {"content": url_input.strip(), "role": "user"},
            {"content": question_input.strip(), "role": "user"},
        ]

        with st.spinner("Analyse en cours..."):
            try:
                result = Runner.run_streamed(agent, input=input_items)
                response = ""
                # Exécution des événements asynchrones dans Streamlit (hack asyncio compatible)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                async def collect():
                    nonlocal response
                    async for event in result.stream_events():
                        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                            response += event.data.delta
                        elif event.type == "run_item_stream_event":
                            if event.item.type == "tool_call_item":
                                st.info("Récupération de la transcription...")
                            elif event.item.type == "tool_call_output_item":
                                if "transcription" in event.item.output.lower():
                                    st.success("Transcription récupérée.")
                loop.run_until_complete(collect())
                st.markdown("**Réponse de l'agent :**")
                st.write(response)
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
