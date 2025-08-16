## Semaine 5 — Ollama, LangChain et OpenRouter

Ce dossier contient des notebooks pour:
- **Ollama en Python** (`00_ollama_python_.ipynb`)
- **LangChain + Ollama (quickstart)** (`01_ollama_langchain_quickstart.ipynb`)
- **OpenRouter via SDK OpenAI** (`02_openrouter_python.ipynb`)

### Prérequis
- Python 3.10+
- macOS ou Linux (Windows WSL recommandé pour Ollama)

### Installation rapide
1) Créer et activer un environnement virtuel
```bash
python3 -m venv .venv && source .venv/bin/activate
```

2) Installer les dépendances
```bash
pip install -r requirements.txt
```

3) Configurer l'environnement
- Installer Ollama et télécharger un modèle (ex: `llama3`).
- Créer et exporter la variable `OPENROUTER_API_KEY` pour OpenRouter.

Consultez le guide détaillé: `GUIDE_INSTALLATION_OLLAMA_OPENROUTER.md`.

### Lancer les notebooks
```bash
jupyter notebook
```
Ouvrez ensuite les fichiers `.ipynb` dans votre navigateur.

### Notes
- Pour Ollama, assurez-vous qu'un modèle est disponible localement (ex: `ollama pull llama3`).
- Pour OpenRouter, une clé API valide doit être présente dans `OPENROUTER_API_KEY`.

