## Guide d'installation — Ollama et OpenRouter

### 1) Installer Ollama

macOS (Homebrew):
```bash
brew install --cask ollama
```

Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Windows: utilisez WSL2 (Ubuntu) puis suivez les étapes Linux.

Démarrer le service (si nécessaire):
```bash
ollama serve
```

Télécharger un modèle (ex: Llama 3):
```bash
ollama pull llama3
```

Test rapide:
```bash
ollama run llama3 "Bonjour, peux-tu te présenter en 2 phrases ?"
```

### 2) Clé API OpenRouter

1. Créez un compte sur `https://openrouter.ai`
2. Générez une clé API
3. Exportez la clé dans votre shell (ajoutez à votre `~/.zshrc` si souhaité):
```bash
export OPENROUTER_API_KEY="votre_cle_api"
```

Option .env (facultatif, si vous utilisez `python-dotenv`):
```
OPENROUTER_API_KEY=votre_cle_api
```

### 3) Exemples d'utilisation

Python (SDK OpenAI avec OpenRouter):
```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

resp = client.chat.completions.create(
    model="openrouter/anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Dis bonjour en français."}],
)
print(resp.choices[0].message.content)
```

LangChain + Ollama (local):
```python
from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3")
result = llm.invoke("Explique brièvement ce qu'est Ollama.")
print(result.content)
```

### 4) Dépannage rapide
- Si `ollama` n'est pas trouvé: vérifiez votre PATH ou relancez le terminal après installation.
- Si aucun modèle n'est disponible: exécutez `ollama pull <modele>`.
- Si l'API OpenRouter renvoie 401: vérifiez `OPENROUTER_API_KEY`.

