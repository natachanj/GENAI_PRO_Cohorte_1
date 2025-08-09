# 📽 YouTube Transcript Agent

Un assistant intelligent qui analyse le contenu des vidéos YouTube en utilisant leurs transcriptions. Cette application est disponible en plusieurs versions, offrant différentes interfaces et approches pour répondre à vos besoins d'analyse de contenu vidéo.

## 🌟 Fonctionnalités

- Extraction automatique des transcriptions de vidéos YouTube
- Multiples interfaces au choix (Gradio, Streamlit, Jupyter)
- Analyse intelligente du contenu grâce à GPT-4
- Support des horodatages dans les réponses
- Gestion des erreurs robuste
- Configuration flexible de la clé API via l'interface

## 🛠 Technologies Utilisées

- **Python** - Langage de programmation principal
- **Gradio & Streamlit** - Frameworks pour l'interface utilisateur
- **OpenAI GPT-4** - Modèle de langage pour l'analyse
- **YouTube Transcript API** - Pour l'extraction des transcriptions
- **TensorFlow** - Pour le traitement des données
- **Conda** - Pour la gestion de l'environnement virtuel

## 📋 Prérequis

- Python 3.10 ou supérieur
- Une clé API OpenAI
- Connexion Internet stable
- Anaconda ou Miniconda

## ⚙️ Installation

### Configuration de l'environnement avec Conda

1. Créez un nouvel environnement Conda avec Python 3.10 :
```bash
conda create -n tf2-env python=3.10
```

2. Activez l'environnement :
```bash
conda activate tf2-env
```

3. Installez les dépendances :
```bash
pip install tensorflow==2.13.0 tensorflow-probability==0.21.0
pip install gradio openai youtube-transcript-api streamlit jupyter ipykernel
python -m ipykernel install --user --name tf2-env --display-name "Python (tf2-env)"
```

## 🚀 Interfaces Disponibles

### 1. Interface Gradio

#### Description
[Gradio](https://www.gradio.app/docs) est un framework moderne qui permet de créer rapidement des interfaces web pour des modèles d'IA. Il offre :
- Une interface élégante et responsive
- Un chat interactif avec historique
- Un déploiement facile avec URL publique
- Une excellente gestion des flux de données en temps réel

#### Utilisation
```bash
conda activate tf2-env
python youtube_agent_gradio.py
```

Accédez à l'interface via :
- URL locale : http://127.0.0.1:7860
- URL publique (générée automatiquement)

### 2. Python (Script Direct)

#### Description
[Python](https://docs.python.org/3.10/) est le langage de base du projet, offrant :
- Une exécution directe et rapide
- Un contrôle total sur le flux d'exécution
- Une facilité de débogage
- Une intégration native avec les API

#### Utilisation
Le script peut être exécuté directement :
```bash
python AgentIATranscription.py
```

### 3. Interface Streamlit

#### Description
[Streamlit](https://docs.streamlit.io/) est un framework Python qui permet de créer des applications web data-driven. Avantages :
- Interface simple et intuitive
- Mise à jour en temps réel
- Widgets interactifs préconçus
- Déploiement facile

#### Utilisation
```bash
conda activate tf2-env
streamlit run AgentIATranscription.py
```

L'interface sera accessible à :
- URL locale : http://localhost:8501

### 4. Jupyter Notebook

#### Description
[Jupyter](https://jupyter-notebook.readthedocs.io/) est un environnement de développement interactif idéal pour :
- L'exploration pas à pas du code
- La visualisation des résultats
- L'expérimentation et l'apprentissage
- La documentation interactive

#### Utilisation
```bash
jupyter notebook
```

Ouvrez `Créer_Un_Agent_IA_Youtube.ipynb` et sélectionnez le kernel "Python (tf2-env)".

## 🔍 Fonctionnement

L'application fonctionne en plusieurs étapes :

1. Extraction de l'ID de la vidéo YouTube depuis l'URL
2. Récupération de la transcription via l'API YouTube
3. Analyse du contenu par GPT-4
4. Génération de réponses pertinentes

## ⚠️ Gestion des Erreurs

L'application gère plusieurs cas d'erreur :
- URLs YouTube invalides
- Transcriptions désactivées
- Vidéos non disponibles
- Problèmes de connexion
- Validation de la clé API

## 🔄 Maintenance

```bash
# Mettre à jour les dépendances
conda activate tf2-env
pip install -r requirements.txt --upgrade

# Exporter l'environnement
pip freeze > requirements.txt

# Supprimer l'environnement
conda deactivate
conda remove -n tf2-env --all
```

## 📚 Documentation Complémentaire

- [OpenAI API](https://platform.openai.com/docs/api-reference)
- [YouTube Transcript API](https://github.com/jdepoix/youtube-transcript-api)
- [TensorFlow](https://www.tensorflow.org/api_docs)
- [Conda](https://docs.conda.io/en/latest/)

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👥 Auteurs

- LDA ACADEMY - Développement initial

---
Créé avec ❤️ pour faciliter l'analyse de contenu YouTube