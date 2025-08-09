import streamlit as st
import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, CouldNotRetrieveTranscript
from openai import OpenAI

st.set_page_config(page_title="YouTube Content Agent", page_icon="🎬", layout="centered")
st.title("🎬 YouTube Content Agent")
st.markdown("Générez du contenu ou posez des questions à partir d'une vidéo YouTube.")

AGENT_INSTRUCTIONS = (
    "Tu es un assistant expert en analyse de vidéos YouTube et en création de contenu. "
    "Lorsque l'utilisateur te donne une URL, commence par récupérer automatiquement la transcription de la vidéo. "
    "Analyse ensuite le contenu en identifiant les messages clés, le ton employé, les intentions de l’auteur, les cibles et les points marquants.\n\n"
    "Tu peux ensuite répondre à deux types de demandes :\n"
    "1. Poser des questions sur la vidéo : l'utilisateur peut te poser des questions précises pour mieux comprendre ou explorer le contenu.\n"
    "2. Générer des contenus pour les réseaux sociaux :\n"
    "   - Un post LinkedIn (800 à 1200 caractères), structuré, professionnel, avec une bonne accroche et un appel à l’action\n"
    "   - Un post Instagram (300 à 600 caractères), plus direct, percutant et adapté au ton de la plateforme.\n\n"
    "Adapte toujours le style et le ton à la plateforme cible. Si un message central fort ou un angle original se dégage, utilise-le comme fil conducteur."
)

def fetch_youtube_transcript(url: str) -> str:
    video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(video_id_pattern, url)
    if not match:
        return "URL YouTube invalide."

    video_id = match.group(1)
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = None

        try:
            transcript_data = ytt_api.fetch(video_id, languages=['fr'])
        except NoTranscriptFound:
            try:
                transcript_data = ytt_api.fetch(video_id, languages=['en'])
            except NoTranscriptFound:
                try:
                    transcript_data = ytt_api.fetch(video_id)
                except:
                    transcript_list = ytt_api.list_transcripts(video_id)
                    try:
                        transcript = transcript_list.find_transcript(['fr', 'en'])
                        transcript_data = transcript.fetch()
                    except NoTranscriptFound:
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript_data = available_transcripts[0].fetch()
                        else:
                            return "❌ Aucune transcription disponible."

        if not transcript_data:
            return "❌ Aucune donnée de transcription récupérée"

        formatted = []
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
                formatted.append(f"{timestamp} {text}")
            except Exception as e:
                st.warning(f"Erreur de parsing d'un snippet: {str(e)}")
                continue

        return "\n".join(formatted)

    except TranscriptsDisabled:
        return "❌ Les transcriptions sont désactivées pour cette vidéo."
    except VideoUnavailable:
        return "❌ Vidéo non disponible."
    except CouldNotRetrieveTranscript:
        return "❌ Impossible de récupérer la transcription."
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def analyze_with_openai(transcript: str, question: str, api_key: str) -> str:
    try:
        client = OpenAI(api_key=api_key)
        prompt = f"""
        Voici la transcription d'une vidéo YouTube :

        {transcript}

        Demande de l'utilisateur : {question}

        {AGENT_INSTRUCTIONS}
        """
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erreur d'analyse : {str(e)}"

st.markdown("---")

st.markdown("### 🔑 Configuration de l'API OpenAI")
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.text_input("Votre clé API OpenAI", type="password", value=st.session_state.api_key)
if api_key_input:
    st.session_state.api_key = api_key_input
    st.success("Clé API enregistrée")
else:
    st.warning("Veuillez fournir une clé API pour continuer")
    st.stop()

st.markdown("---")

st.markdown("### 📺 Analyse de vidéo YouTube")
url = st.text_input("URL de la vidéo YouTube")
question = st.text_area("Votre question ou demande (ex : 'Génère un post LinkedIn', 'Quels sont les points clés ?', etc.)")

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Lancer l'analyse"):
        if not url:
            st.error("Merci de fournir une URL valide.")
        elif not question:
            st.error("Merci de formuler une question ou une demande.")
        else:
            with st.spinner("Récupération de la transcription..."):
                transcript = fetch_youtube_transcript(url)

            if transcript.startswith("❌"):
                st.error(transcript)
            else:
                st.success("Transcription récupérée avec succès.")
                with st.expander("📄 Aperçu de la transcription"):
                    st.text(transcript[:1000] + "..." if len(transcript) > 1000 else transcript)

                with st.spinner("Analyse en cours..."):
                    result = analyze_with_openai(transcript, question, st.session_state.api_key)
                    st.markdown("### 🤖 Résultat")
                    st.markdown(result)

with col2:
    if st.button("🔄 Recommencer", type="secondary"):
        st.rerun()

st.markdown("---")

st.info("""
💡 Cette application vous permet d'analyser le contenu d'une vidéo YouTube via sa transcription :
- Posez des questions spécifiques sur le contenu
- Générez du contenu prêt à l'emploi (LinkedIn, Instagram)

Votre clé API OpenAI est utilisée uniquement localement, elle n'est pas stockée sur un serveur.
""")