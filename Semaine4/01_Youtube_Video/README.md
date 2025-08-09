# 🎬 YouTube Content Generator Pro

Un assistant intelligent multi-plateforme qui analyse le contenu des vidéos YouTube et génère automatiquement du contenu pour les réseaux sociaux. Disponible en 5 versions différentes pour répondre à tous vos besoins.

## 🌟 Fonctionnalités Principales

- **Extraction automatique** des transcriptions YouTube avec gestion robuste des langues
- **Génération de contenu** : articles de blog, posts LinkedIn, posts Instagram
- **Analyse intelligente** du contenu avec GPT-4o
- **5 interfaces différentes** : Gradio, Python CLI, Streamlit, Jupyter, FastAPI
- **Gestion d'erreurs avancée** pour les transcriptions YouTube
- **Configuration flexible** de la clé API OpenAI

## 📁 Structure du Projet

```
01_Youtube_Video/
├── 1_youtube_agent_gradio.py      # Interface Gradio avec chat interactif
├── 2_main.py                      # Script Python CLI classique
├── 3_AgentIATranscription.py      # Application Streamlit
├── 4_Créer_Un_Agent_IA_Youtube.ipynb  # Notebook Jupyter
├── 5_youtube_agent_fastapi.py     # API FastAPI avec interface web
├── requirements.txt                # Dépendances Python
└── README.md                      # Documentation
```

## 🛠 Technologies Utilisées

- **Python 3.10** - Langage principal
- **OpenAI GPT-4o** - Modèle de langage pour l'analyse
- **YouTube Transcript API** - Extraction des transcriptions
- **Gradio** - Interface web moderne avec chat
- **Streamlit** - Application web data-driven
- **FastAPI** - API REST avec WebSocket
- **Jupyter Notebook** - Environnement interactif
- **Conda** - Gestion de l'environnement virtuel

## ⚙️ Installation

### 1. Configuration de l'environnement Conda

```bash
# Création de l'environnement
conda create -n tf2-env python=3.10

# Activation
conda activate tf2-env

# Installation des dépendances
pip install tensorflow==2.13.0 tensorflow-probability==0.21.0
pip install ipykernel jupyter
python -m ipykernel install --user --name tf2-env --display-name "Python (tf2-env)"
```

### 2. Installation des packages requis

```bash
# Packages principaux
pip install gradio openai youtube-transcript-api streamlit fastapi uvicorn

# Packages additionnels
pip install python-dotenv requests
```

## 🚀 Utilisation

### 1. Interface Gradio (Recommandée) 🌟

**Description** : Interface web moderne avec chat interactif, historique des conversations et déploiement automatique.

**Avantages** :
- Interface élégante et responsive
- Chat en temps réel avec historique
- URL publique automatique pour le partage
- Gestion avancée des transcriptions YouTube
- Instructions d'agent optimisées

**Lancement** :
```bash
conda activate tf2-env
python 1_youtube_agent_gradio.py
```

**Accès** :
- Local : http://localhost:7860
- Public : URL générée automatiquement

### 2. Script Python CLI 🖥️

**Description** : Script Python classique en ligne de commande avec interface interactive.

**Avantages** :
- Exécution directe et rapide
- Configuration de l'API en première étape
- Interface en ligne de commande intuitive
- Gestion robuste des erreurs

**Lancement** :
```bash
conda activate tf2-env
python 2_main.py
```

**Fonctionnalités** :
- Configuration de la clé API en premier
- Test automatique de la clé API
- Analyse de vidéos en boucle
- Aperçu des transcriptions

### 3. Application Streamlit 📊

**Description** : Interface web data-driven avec widgets interactifs et bouton de recommencer.

**Avantages** :
- Interface simple et intuitive
- Widgets interactifs préconçus
- Bouton "Recommencer" pour relancer l'analyse
- Mise à jour en temps réel

**Lancement** :
```bash
conda activate tf2-env
streamlit run 3_AgentIATranscription.py
```

**Accès** : http://localhost:8501

### 4. Jupyter Notebook 📓

**Description** : Environnement interactif pour l'exploration et l'apprentissage.

**Avantages** :
- Exploration pas à pas du code
- Visualisation des résultats
- Expérimentation et apprentissage
- Documentation interactive

**Lancement** :
```bash
conda activate tf2-env
jupyter notebook
```

**Utilisation** : Ouvrir `4_Créer_Un_Agent_IA_Youtube.ipynb`

### 5. API FastAPI avec Interface Web 🌐

**Description** : API REST moderne avec interface web personnalisée et WebSocket.

**Avantages** :
- API REST complète
- Interface web personnalisée
- Communication WebSocket en temps réel
- Gestion avancée des transcriptions
- Configuration robuste de l'API

**Lancement** :
```bash
conda activate tf2-env
python 5_youtube_agent_fastapi.py
```

**Accès** : http://localhost:8000

## 🔧 Configuration de l'API OpenAI

### Méthode 1 : Variable d'environnement
```bash
export OPENAI_API_KEY="sk-votre-clé-api-ici"
```

### Méthode 2 : Interface utilisateur
- **Gradio/Streamlit** : Champ de saisie dans l'interface
- **Python CLI** : Saisie interactive au démarrage
- **FastAPI** : Configuration via l'interface web

## 🎯 Instructions de l'Agent

L'agent est configuré pour :

1. **Analyser le contenu** : Identifier les messages clés, le ton, les cibles
2. **Générer du contenu** :
   - **Article de blog** (500-800 mots) : Introduction, développement, conclusion
   - **Post LinkedIn** (800-1200 caractères) : Professionnel avec call-to-action
   - **Post Instagram** (300-600 caractères) : Direct et engageant

## 🔍 Gestion des Transcriptions YouTube

### Méthodes de récupération :
1. **Français auto-généré** (priorité)
2. **Anglais auto-généré** (fallback)
3. **Transcription par défaut**
4. **Liste des transcriptions disponibles**

### Gestion des erreurs :
- URLs invalides
- Transcriptions désactivées
- Vidéos non disponibles
- Erreurs de formatage

## ⚠️ Résolution des Problèmes

### Erreur "bad interpreter"
```bash
# Réinstaller les packages dans l'environnement Conda
conda activate tf2-env
pip install --force-reinstall streamlit gradio uvicorn
```

### Erreur de transcription YouTube
- Vérifiez que la vidéo a des sous-titres activés
- Essayez une autre vidéo pour tester
- Vérifiez votre connexion Internet

### Erreur de clé API
- Vérifiez le format : `sk-...`
- Testez la clé sur [OpenAI Platform](https://platform.openai.com/account/api-keys)
- Vérifiez vos crédits OpenAI

## 📚 Documentation des Technologies

- **[Gradio](https://www.gradio.app/docs)** - Interface web moderne
- **[Streamlit](https://docs.streamlit.io/)** - Applications data-driven
- **[FastAPI](https://fastapi.tiangolo.com/)** - API REST moderne
- **[OpenAI API](https://platform.openai.com/docs)** - Modèles de langage
- **[YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)** - Transcriptions YouTube
- **[Jupyter](https://jupyter-notebook.readthedocs.io/)** - Environnement interactif

## 🔄 Maintenance

```bash
# Mise à jour des dépendances
conda activate tf2-env
pip install -r requirements.txt --upgrade

# Export de l'environnement
pip freeze > requirements.txt

# Nettoyage
conda deactivate
conda remove -n tf2-env --all
```

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- **LDA ACADEMY** - Développement initial et maintenance

---

🎬 **YouTube Content Generator Pro** - Transformez vos vidéos YouTube en contenu multi-plateforme avec l'IA !

*Créé avec ❤️ pour faciliter l'analyse et la génération de contenu YouTube*