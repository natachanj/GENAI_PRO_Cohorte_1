#!/usr/bin/env python3
"""
Script Python classique pour analyser des vidéos YouTube
"""

import re
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, CouldNotRetrieveTranscript
from openai import OpenAI

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

def fetch_youtube_transcript(url: str) -> str:
    """Récupère la transcription d'une vidéo YouTube."""
    video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(video_id_pattern, url)
    if not match:
        return "URL YouTube invalide."

    video_id = match.group(1)
    print(f"🎥 Récupération de la transcription pour: {video_id}")
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_data = None

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
                except:
                    transcript_list = ytt_api.list_transcripts(video_id)
                    try:
                        transcript = transcript_list.find_transcript(['fr', 'en'])
                        transcript_data = transcript.fetch()
                        print(f"✅ Transcription {transcript.language} trouvée via list()")
                    except NoTranscriptFound:
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript_data = available_transcripts[0].fetch()
                            print(f"✅ Première transcription disponible: {available_transcripts[0].language}")
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
                print(f"⚠️ Erreur de parsing d'un snippet: {str(e)}")
                continue

        result = "\n".join(formatted)
        print(f"✅ Transcription formatée: {len(formatted)} snippets")
        return result

    except TranscriptsDisabled:
        return "❌ Les transcriptions sont désactivées pour cette vidéo."
    except VideoUnavailable:
        return "❌ Vidéo non disponible."
    except CouldNotRetrieveTranscript:
        return "❌ Impossible de récupérer la transcription."
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def analyze_with_openai(transcript: str, question: str, api_key: str) -> str:
    """Analyse le contenu avec OpenAI."""
    try:
        print("🤖 Analyse en cours avec OpenAI...")
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
        return f"❌ Erreur d'analyse : {str(e)}"

def main():
    """Fonction principale du script."""
    print("🎬 YouTube Content Agent - Script Python")
    print("=" * 50)
    
    # Configuration de l'API - Première question
    print("🔑 CONFIGURATION DE L'API OPENAI")
    print("=" * 30)
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("🔑 Entrez votre clé API OpenAI: ").strip()
        if not api_key:
            print("❌ Clé API requise pour continuer.")
            return
    else:
        print("✅ Clé API trouvée dans les variables d'environnement")
        use_env_key = input("🔑 Utiliser la clé API des variables d'environnement ? (o/n): ").strip().lower()
        if use_env_key not in ['o', 'oui', 'y', 'yes']:
            api_key = input("🔑 Entrez votre nouvelle clé API OpenAI: ").strip()
            if not api_key:
                print("❌ Clé API requise pour continuer.")
                return
    
    # Test de la clé API
    print("🔄 Test de la clé API...")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        print("✅ Clé API valide")
    except Exception as e:
        print(f"❌ Clé API invalide: {str(e)}")
        return
    
    print("✅ Configuration terminée")
    print()
    
    while True:
        print("\n" + "="*50)
        print("📺 Analyse de vidéo YouTube")
        print("="*50)
        
        # Saisie de l'URL
        url = input("🔗 URL de la vidéo YouTube (ou 'quit' pour quitter): ").strip()
        if url.lower() in ['quit', 'q', 'exit']:
            print("👋 Au revoir !")
            break
        
        if not url:
            print("❌ URL requise.")
            continue
        
        # Saisie de la question
        question = input("❓ Votre question ou demande (ex: 'Génère un post LinkedIn', 'Quels sont les points clés ?'): ").strip()
        if not question:
            print("❌ Question requise.")
            continue
        
        print("\n🔄 Traitement en cours...")
        
        # Récupération de la transcription
        transcript = fetch_youtube_transcript(url)
        
        if transcript.startswith("❌"):
            print(f"❌ Erreur: {transcript}")
            continue
        
        print("✅ Transcription récupérée avec succès")
        
        # Affichage d'un aperçu de la transcription
        preview = transcript[:500] + "..." if len(transcript) > 500 else transcript
        print(f"\n📄 Aperçu de la transcription:\n{preview}")
        
        # Analyse avec OpenAI
        result = analyze_with_openai(transcript, question, api_key)
        
        print("\n" + "="*50)
        print("🤖 RÉSULTAT")
        print("="*50)
        print(result)
        print("="*50)
        
        # Demander si l'utilisateur veut continuer
        continue_analysis = input("\n🔄 Voulez-vous analyser une autre vidéo ? (o/n): ").strip().lower()
        if continue_analysis not in ['o', 'oui', 'y', 'yes']:
            print("👋 Au revoir !")
            break

if __name__ == "__main__":
    main()