from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import json
import re
from pydantic import BaseModel
from openai import AsyncOpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable,
    CouldNotRetrieveTranscript
)

# Instructions de l'agent
AGENT_INSTRUCTIONS = (
    "Tu es un assistant expert en analyse de vidéos YouTube et en création de contenu. "
    "Lorsque l'utilisateur te donne une URL, commence par récupérer automatiquement la transcription de la vidéo. "
    "Analyse ensuite le contenu en identifiant les messages clés, le ton employé, les intentions de l’auteur, les cibles et les points marquants.\n\n"
    "Tu peux ensuite répondre à deux types de demandes :\n"
    "1. **Poser des questions sur la vidéo** : l'utilisateur peut te poser des questions précises pour mieux comprendre ou explorer le contenu de la vidéo.\n"
    "2. **Générer des contenus pour les réseaux sociaux** :\n"
    "   - Un **post LinkedIn** (800 à 1200 caractères), structuré, professionnel, avec une bonne accroche, un développement clair et une ouverture à l’interaction (question, call-to-action…)\n"
    "   - Un **post Instagram** (300 à 600 caractères), plus direct, percutant, avec un ton léger, inspirant ou engageant, centré sur une idée clé de la vidéo.\n\n"
    "Adapte toujours le style et le ton au format demandé. "
    "Si la vidéo contient un message central fort ou un storytelling marquant, fais-en le fil conducteur."
)

app = FastAPI(title="🎬 YouTube Content Generator Pro")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# État global
api_key = None
conversations = {}

class ConfigRequest(BaseModel):
    api_key: str

@app.post("/api/configure")
async def configure(request: ConfigRequest):
    global api_key
    try:
        print(f"Configuration avec la clé : {request.api_key[:10]}...")
        
        # Validation de la clé API
        client = AsyncOpenAI(api_key=request.api_key)
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        
        api_key = request.api_key
        print("✅ Configuration réussie")
        return {"status": "success", "message": "API configurée avec succès"}
        
    except Exception as e:
        print(f"❌ Erreur de configuration : {str(e)}")
        raise HTTPException(status_code=400, detail=f"Clé API invalide: {str(e)}")

@app.get("/api/status")
async def get_status():
    return {"configured": api_key is not None}

async def fetch_youtube_transcript(url: str) -> str:
    """Récupère la transcription YouTube avec la vraie API."""
    try:
        # Extraction de l'ID de la vidéo
        video_id_pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
        match = re.search(video_id_pattern, url)
        
        if not match:
            return "⚠️ URL YouTube invalide. Vérifiez le format de l'URL."
            
        video_id = match.group(1)
        print(f"🎥 Récupération de la transcription pour: {video_id}")
        
        # Créer une instance de l'API
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
        
        # Vérifier que nous avons des données
        if not transcript_data:
            return "❌ Aucune donnée de transcription récupérée"
        
        # Formatage de la transcription
        if hasattr(transcript_data, 'snippets'):
            # C'est un objet FetchedTranscript avec des snippets
            formatted_transcript = []
            for snippet in transcript_data.snippets:
                try:
                    start_time = float(snippet.start)
                    minutes = int(start_time // 60)
                    seconds = int(start_time % 60)
                    timestamp = f"[{minutes:02d}:{seconds:02d}]"
                    text = snippet.text.strip()
                    if text:
                        formatted_transcript.append(f"{timestamp} {text}")
                except Exception as snippet_error:
                    print(f"⚠️ Erreur formatage snippet: {snippet_error}")
                    continue
            
            if formatted_transcript:
                result = "\n".join(formatted_transcript)
                print(f"✅ Transcription formatée: {len(formatted_transcript)} snippets")
                return result
            else:
                return "❌ Aucun snippet valide trouvé"
                
        elif isinstance(transcript_data, list):
            # Format liste de dictionnaires (ancien format)
            formatted_transcript = []
            for entry in transcript_data:
                try:
                    if isinstance(entry, dict) and 'text' in entry:
                        start_time = float(entry.get('start', 0))
                        minutes = int(start_time // 60)
                        seconds = int(start_time % 60)
                        timestamp = f"[{minutes:02d}:{seconds:02d}]"
                        text = entry['text'].strip()
                        if text:
                            formatted_transcript.append(f"{timestamp} {text}")
                except Exception as entry_error:
                    print(f"⚠️ Erreur formatage entrée: {entry_error}")
                    continue
            
            if formatted_transcript:
                result = "\n".join(formatted_transcript)
                print(f"✅ Transcription formatée: {len(formatted_transcript)} entrées")
                return result
            else:
                return "❌ Aucune entrée valide trouvée"
        else:
            return f"❌ Format de transcription non reconnu: {type(transcript_data)}"

    except TranscriptsDisabled:
        return "❌ Les transcriptions sont désactivées pour cette vidéo"
    except VideoUnavailable:
        return "❌ Cette vidéo n'est pas disponible"
    except CouldNotRetrieveTranscript:
        return "❌ Impossible de récupérer la transcription pour cette vidéo"
    except Exception as e:
        print(f"❌ Erreur inattendue: {str(e)}")
        return f"❌ Erreur inattendue: {str(e)}"

async def analyze_with_openai(transcript: str, question: str) -> str:
    """Analyse le contenu avec OpenAI"""
    try:
        if not api_key:
            return "⚠️ Clé API non configurée"
            
        client = AsyncOpenAI(api_key=api_key)
        
        prompt = f"""Transcription de la vidéo :
{transcript}

Question/Demande : {question}

Analyse cette transcription selon les instructions suivantes:
{AGENT_INSTRUCTIONS}"""
        
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ Erreur d'analyse OpenAI: {str(e)}")
        return f"❌ Erreur d'analyse : {str(e)}"

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"✅ Client connecté : {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"❌ Client déconnecté : {client_id}")

    async def send_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(
                    json.dumps({"type": "message", "content": message})
                )
            except Exception as e:
                print(f"❌ Erreur envoi message: {e}")
                self.disconnect(client_id)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "").strip()
            
            if not message:
                continue
                
            if not api_key:
                await manager.send_message(
                    "⚠️ Veuillez d'abord configurer votre clé API OpenAI dans la sidebar",
                    client_id
                )
                continue
            
            # Détection d'URL YouTube
            if "youtube.com" in message.lower() or "youtu.be" in message.lower():
                await manager.send_message(
                    "🔄 Récupération de la transcription YouTube...",
                    client_id
                )
                
                transcript = await fetch_youtube_transcript(message)
                
                if transcript.startswith("❌") or transcript.startswith("⚠️"):
                    await manager.send_message(transcript, client_id)
                    continue
                
                await manager.send_message(
                    "✨ Génération du contenu en cours... (cela peut prendre quelques secondes)",
                    client_id
                )
                
                analysis = await analyze_with_openai(
                    transcript,
                    "Génère un article de blog, un post LinkedIn et un post Instagram basés sur cette vidéo"
                )
                
                await manager.send_message(analysis, client_id)
                
                # Sauvegarde pour les questions futures
                conversations[client_id] = {
                    "transcript": transcript,
                    "last_analysis": analysis
                }
                
                await manager.send_message(
                    "\n💡 Vous pouvez maintenant poser des questions spécifiques sur cette vidéo !",
                    client_id
                )
                
            else:
                # Question sur une vidéo précédente
                if client_id not in conversations:
                    await manager.send_message(
                        "💡 Commencez par partager une URL YouTube pour que je puisse analyser le contenu !",
                        client_id
                    )
                    continue
                
                await manager.send_message(
                    "🤔 Analyse de votre question...",
                    client_id
                )
                
                response = await analyze_with_openai(
                    conversations[client_id]["transcript"],
                    message
                )
                
                await manager.send_message(response, client_id)
                
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"❌ Erreur WebSocket : {str(e)}")
        try:
            await manager.send_message(
                f"❌ Une erreur est survenue : {str(e)}",
                client_id
            )
        except:
            pass
        manager.disconnect(client_id)

@app.get("/", response_class=HTMLResponse)
def get_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🎬 YouTube Content Generator Pro</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
                display: grid;
                grid-template-columns: 1fr 320px;
                gap: 20px;
                min-height: calc(100vh - 40px);
            }
            .chat-container {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            }
            .sidebar {
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                height: fit-content;
            }
            .header {
                text-align: center;
                margin-bottom: 25px;
                padding-bottom: 20px;
                border-bottom: 2px solid #f0f0f0;
            }
            .header h1 {
                margin: 0;
                color: #333;
                font-size: 28px;
            }
            .header p {
                color: #666;
                margin: 10px 0 0 0;
                font-size: 16px;
            }
            .messages {
                flex: 1;
                height: 500px;
                overflow-y: auto;
                margin-bottom: 20px;
                padding: 15px;
                border: 2px solid #f0f0f0;
                border-radius: 10px;
                background: #fafafa;
            }
            .message {
                margin-bottom: 15px;
                padding: 12px 16px;
                border-radius: 12px;
                white-space: pre-wrap;
                word-wrap: break-word;
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .user-message {
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                margin-left: 15%;
                border-bottom-right-radius: 4px;
            }
            .bot-message {
                background: white;
                margin-right: 15%;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 4px;
                color: #333;
            }
            .input-area {
                display: flex;
                gap: 12px;
                align-items: flex-end;
            }
            textarea {
                flex-grow: 1;
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 12px;
                resize: vertical;
                font-family: inherit;
                font-size: 14px;
                line-height: 1.4;
                transition: border-color 0.3s ease;
            }
            textarea:focus {
                outline: none;
                border-color: #007bff;
            }
            button {
                padding: 12px 24px;
                background: linear-gradient(135deg, #007bff, #0056b3);
                color: white;
                border: none;
                border-radius: 12px;
                cursor: pointer;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.3s ease;
                position: relative;
                overflow: hidden;
            }
            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                opacity: 0.7;
            }
            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,123,255,0.3);
            }
            button:active:not(:disabled) {
                transform: translateY(0);
            }
            .sidebar h2 {
                color: #333;
                margin: 0 0 20px 0;
                font-size: 20px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .config-form {
                margin-bottom: 20px;
            }
            .config-form input {
                width: 100%;
                padding: 12px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-bottom: 12px;
                font-size: 14px;
                transition: border-color 0.3s ease;
            }
            .config-form input:focus {
                outline: none;
                border-color: #007bff;
            }
            .status {
                margin-top: 15px;
                padding: 12px;
                border-radius: 8px;
                text-align: center;
                font-weight: 600;
                font-size: 14px;
            }
            .status.success {
                background: #d4edda;
                color: #155724;
                border: 1px solid #c3e6cb;
            }
            .status.error {
                background: #f8d7da;
                color: #721c24;
                border: 1px solid #f5c6cb;
            }
            .status.info {
                background: #d1ecf1;
                color: #0c5460;
                border: 1px solid #bee5eb;
            }
            .loading {
                position: relative;
                pointer-events: none;
            }
            .loading::after {
                content: '';
                position: absolute;
                width: 20px;
                height: 20px;
                top: 50%;
                left: 50%;
                margin: -10px 0 0 -10px;
                border: 2px solid transparent;
                border-top-color: white;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .examples {
                background: #f8f9ff;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                border: 1px solid #e0e0ff;
            }
            .examples h3 {
                margin: 0 0 10px 0;
                color: #4a4a8a;
                font-size: 16px;
            }
            .examples ul {
                margin: 0;
                padding-left: 18px;
                color: #666;
            }
            .examples li {
                margin-bottom: 5px;
                font-size: 13px;
            }
            @media (max-width: 768px) {
                .container {
                    grid-template-columns: 1fr;
                    gap: 15px;
                }
                body { padding: 10px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="chat-container">
                <div class="header">
                    <h1>🎬 YouTube Content Generator Pro</h1>
                    <p>Transformez vos vidéos YouTube en contenu multi-plateforme</p>
                </div>
                
                <div id="messages" class="messages">
                    <div class="message bot-message">
                        🤖 Bonjour ! Je suis votre assistant de génération de contenu YouTube.
                        
Voici ce que je peux faire pour vous :
• 📝 Créer un article de blog complet (500-800 mots)
• 💼 Rédiger un post LinkedIn professionnel (800-1200 caractères)
• 📸 Générer un post Instagram engageant (300-600 caractères)

Pour commencer :
1. Configurez votre clé API OpenAI dans la sidebar →
2. Collez l'URL d'une vidéo YouTube
3. Je me charge du reste !

Vous pourrez ensuite me poser des questions spécifiques sur le contenu de la vidéo.
                    </div>
                </div>
                
                <div class="input-area">
                    <textarea
                        id="messageInput"
                        placeholder="Collez une URL YouTube (ex: https://www.youtube.com/watch?v=...) ou posez une question sur la vidéo analysée..."
                        rows="3"
                    ></textarea>
                    <button id="sendButton" disabled>
                        📤 Envoyer
                    </button>
                </div>
            </div>
            
            <div class="sidebar">
                <h2>⚙️ Configuration</h2>
                <div class="config-form">
                    <input
                        type="password"
                        id="apiKeyInput"
                        placeholder="Votre clé API OpenAI (sk-...)"
                    >
                    <button id="configureButton" style="width: 100%;">
                        🔐 Configurer l'API
                    </button>
                </div>
                <div id="status" class="status info">
                    🔴 API non configurée
                </div>
                
                <div class="examples">
                    <h3>💡 Exemples d'URLs</h3>
                    <ul>
                        <li>https://www.youtube.com/watch?v=ABC123</li>
                        <li>https://youtu.be/ABC123</li>
                        <li>Toute URL YouTube valide</li>
                    </ul>
                </div>
                
                <div class="examples">
                    <h3>❓ Questions possibles</h3>
                    <ul>
                        <li>"Refais juste le post LinkedIn"</li>
                        <li>"Rends l'article plus technique"</li>
                        <li>"Quels sont les points clés ?"</li>
                        <li>"Adapte pour un public débutant"</li>
                    </ul>
                </div>
            </div>
        </div>

        <script>
            let ws = null;
            let isConfigured = false;
            const clientId = 'client_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);

            function connect() {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    return;
                }
                
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${clientId}`;
                
                console.log('Connexion WebSocket:', wsUrl);
                ws = new WebSocket(wsUrl);
                
                ws.onopen = () => {
                    console.log('✅ WebSocket connecté');
                    document.getElementById('sendButton').disabled = !isConfigured;
                };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    addMessage(data.content, 'bot');
                    document.getElementById('sendButton').disabled = false;
                };
                
                ws.onclose = () => {
                    console.log('❌ WebSocket déconnecté');
                    if (isConfigured) {
                        setTimeout(connect, 2000);
                    }
                };
                
                ws.onerror = (error) => {
                    console.error('❌ Erreur WebSocket:', error);
                };
            }

            function addMessage(content, type) {
                const messages = document.getElementById('messages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.textContent = content;
                messages.appendChild(messageDiv);
                messages.scrollTop = messages.scrollHeight;
            }

            // Configuration de l'API
            document.getElementById('configureButton').addEventListener('click', async () => {
                const apiKey = document.getElementById('apiKeyInput').value.trim();
                const button = document.getElementById('configureButton');
                const status = document.getElementById('status');
                
                if (!apiKey) {
                    status.textContent = '❌ Clé API requise';
                    status.className = 'status error';
                    return;
                }
                
                if (!apiKey.startsWith('sk-')) {
                    status.textContent = '❌ Format de clé invalide (doit commencer par sk-)';
                    status.className = 'status error';
                    return;
                }
                
                button.disabled = true;
                button.classList.add('loading');
                status.textContent = '🔄 Validation en cours...';
                status.className = 'status info';
                
                try {
                    const response = await fetch('/api/configure', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ api_key: apiKey })
                    });
                    
                    const result = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(result.detail || 'Erreur de configuration');
                    }
                    
                    status.textContent = '🟢 API configurée avec succès !';
                    status.className = 'status success';
                    isConfigured = true;
                    document.getElementById('sendButton').disabled = false;
                    connect();
                    
                    // Masquer le champ de saisie après configuration
                    document.getElementById('apiKeyInput').type = 'text';
                    document.getElementById('apiKeyInput').value = apiKey.substring(0, 7) + '***' + apiKey.substring(apiKey.length - 4);
                    document.getElementById('apiKeyInput').disabled = true;
                    button.textContent = '🔄 Changer la clé';
                    
                } catch (error) {
                    console.error('Erreur configuration:', error);
                    status.textContent = `❌ ${error.message}`;
                    status.className = 'status error';
                    isConfigured = false;
                    document.getElementById('sendButton').disabled = true;
                } finally {
                    button.disabled = false;
                    button.classList.remove('loading');
                }
            });

            // Envoi de message
            document.getElementById('sendButton').addEventListener('click', () => {
                sendMessage();
            });
            
            document.getElementById('messageInput').addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            function sendMessage() {
                const input = document.getElementById('messageInput');
                const message = input.value.trim();
                
                if (!message || !isConfigured) return;
                
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({ message }));
                    addMessage(message, 'user');
                    input.value = '';
                    document.getElementById('sendButton').disabled = true;
                } else {
                    addMessage('❌ Connexion perdue, reconnexion...', 'bot');
                    connect();
                }
            }

            // Vérifier le statut initial au chargement
            window.addEventListener('load', async () => {
                try {
                    const response = await fetch('/api/status');
                    const data = await response.json();
                    
                    if (data.configured) {
                        isConfigured = true;
                        document.getElementById('status').textContent = '🟢 API déjà configurée';
                        document.getElementById('status').className = 'status success';
                        document.getElementById('sendButton').disabled = false;
                        connect();
                    }
                } catch (error) {
                    console.log('Pas de configuration existante');
                }
            });
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage du serveur YouTube Content Generator Pro...")
    print("🌐 Interface accessible sur: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)