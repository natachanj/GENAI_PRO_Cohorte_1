# 🚗 Tesla Q1 2023 - Système RAG Intelligent

Un système de **Retrieval-Augmented Generation (RAG)** sophistiqué pour analyser le rapport trimestriel Q1 2023 de Tesla. Ce projet combine l'extraction intelligente de documents PDF, la recherche vectorielle et l'IA générative pour fournir des réponses précises aux questions financières.

## 📋 Table des matières

- [🚀 Fonctionnalités](#-fonctionnalités)
- [🏗️ Architecture](#️-architecture)
- [📁 Structure du projet](#-structure-du-projet)
- [⚙️ Prérequis](#️-prérequis)
- [🔧 Installation](#-installation)
- [🚀 Utilisation](#-utilisation)
- [📊 Configuration](#-configuration)
- [🔍 API et Endpoints](#-api-et-endpoints)
- [📚 Documentation technique](#-documentation-technique)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

## 🚀 Fonctionnalités

- **📄 Extraction intelligente de PDF** : Texte, tableaux et OCR
- **🔍 Recherche vectorielle avancée** : ChromaDB avec embeddings OpenAI
- **🤖 Assistant IA financier** : Réponses contextuelles en français
- **💻 Interface web moderne** : Gradio avec design responsive
- **📱 Interface notebook** : Tests et développement interactifs
- **⚡ Pipeline optimisé** : Recherche "table-first" pour données financières
- **🔧 Configuration flexible** : Variables d'environnement et paramètres ajustables

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Interface     │    │   Pipeline      │    │   Base de       │
│   Utilisateur   │◄──►│   RAG           │◄──►│   Données       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                        │                        │
│ • Gradio Web App      │ • Ingestion PDF        │ • Documents PDF
│ • Jupyter Notebook    │ • Embeddings           │ • Vector Store
│ • Chat Interface      │ • Retrieval            │ • ChromaDB
└───────────────────────┴────────────────────────┴─────────────────┘
```

### Composants principaux

- **`app.py`** : Interface web Gradio avec chat interactif
- **`fonctions/rag_pipeline.py`** : Pipeline RAG principal avec LLM OpenAI
- **`fonctions/ingestion.py`** : Extraction et traitement des documents PDF
- **`fonctions/retrieval.py`** : Recherche vectorielle et ranking
- **`fonctions/embeddings.py`** : Gestion des embeddings OpenAI
- **`fonctions/config.py`** : Configuration centralisée

## 📁 Structure du projet

```
Test/
├── 📄 app.py                          # Interface web Gradio
├── 📊 RAG_PDF_notebook.ipynb         # Notebook de test et développement
├── 📋 requirements.txt                # Dépendances Python
├── 🔒 constraints.txt                 # Contraintes de versions
├── 📁 data/                          # Documents PDF à analyser
│   └── TSLA-Q1-2023-Update.pdf      # Rapport Tesla Q1 2023
├── 📁 fonctions/                     # Modules Python du système
│   ├── __init__.py
│   ├── config.py                     # Configuration et variables d'env
│   ├── embeddings.py                 # Gestion des embeddings
│   ├── ingestion.py                  # Extraction et traitement PDF
│   ├── rag_pipeline.py               # Pipeline RAG principal
│   ├── retrieval.py                  # Recherche vectorielle
│   └── utils.py                      # Utilitaires divers
├── 📁 .chroma/                       # Base vectorielle (généré)
└── 📄 .env                           # Variables d'environnement
```

## ⚙️ Prérequis

### Système
- **OS** : macOS, Linux ou Windows
- **Python** : 3.11+ (recommandé)
- **RAM** : 4GB minimum (8GB recommandé)
- **Stockage** : 2GB d'espace libre

### Binaires système (optionnels pour OCR)
- **Poppler** : Extraction de pages PDF
- **Tesseract** : Reconnaissance de texte (OCR)

### Compte API
- **OpenAI API Key** : Pour embeddings et LLM

## 🔧 Installation

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd Test
```

### 2. Créer l'environnement Conda
```bash
# Créer l'environnement Python 3.11
conda create -n rag-tsla python=3.11 -y

# Activer l'environnement
conda activate rag-tsla
```

### 3. Installer les dépendances
```bash
# Installer les packages Python
pip install -r requirements.txt -c constraints.txt

# Installer le kernel Jupyter
pip install ipykernel
python -m ipykernel install --user --name=rag-tsla --display-name "Python (rag-tsla)"
```

### 4. Installer les binaires système (optionnel)

> **Note** : Ces binaires sont nécessaires pour l'extraction avancée de PDF et l'OCR. Sans eux, seuls le texte brut et les tableaux seront extraits.

#### 🍎 macOS
```bash
# Installer Homebrew si pas déjà fait
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Installer Poppler et Tesseract
brew install poppler tesseract

# Vérifier l'installation
pdftoppm -v
tesseract --version
```

#### 🐧 Ubuntu/Debian
```bash
# Mettre à jour les paquets
sudo apt-get update

# Installer Poppler (extraction PDF)
sudo apt-get install -y poppler-utils

# Installer Tesseract (OCR)
sudo apt-get install -y tesseract-ocr

# Installer les langues françaises pour Tesseract (optionnel)
sudo apt-get install -y tesseract-ocr-fra

# Vérifier l'installation
pdftoppm -v
tesseract --version
```

#### 🪟 Windows
```bash
# Option 1: Avec Chocolatey (recommandé)
choco install poppler tesseract

# Option 2: Installation manuelle
# 1. Poppler : https://github.com/oschwartz10612/poppler-windows/releases
#    - Télécharger la dernière version
#    - Extraire dans C:\poppler
#    - Ajouter C:\poppler\bin à votre PATH

# 2. Tesseract : https://github.com/UB-Mannheim/tesseract/wiki
#    - Télécharger l'installateur Windows
#    - Installer avec les langues françaises
#    - Ajouter C:\Program Files\Tesseract-OCR à votre PATH
```

#### 🔍 Vérification de l'installation
Après installation, vérifiez que les binaires sont accessibles :

```bash
# Vérifier Poppler
which pdftoppm  # macOS/Linux
where pdftoppm  # Windows

# Vérifier Tesseract
which tesseract  # macOS/Linux
where tesseract  # Windows

# Tester avec un PDF
pdftoppm -f 1 -l 1 -png test.pdf output
tesseract --version
```

#### 🚨 Résolution des problèmes

**Erreur "command not found"**
- Vérifiez que les binaires sont dans votre PATH
- Redémarrez votre terminal après installation
- Sur Windows, redémarrez l'ordinateur après modification du PATH

**Erreur de permissions (Linux/macOS)**
```bash
# Vérifier les permissions
ls -la $(which pdftoppm)
ls -la $(which tesseract)

# Corriger si nécessaire
sudo chmod +x $(which pdftoppm)
sudo chmod +x $(which tesseract)
```

### 5. Configuration des variables d'environnement
Créer un fichier `.env` à la racine du projet :

```bash
# OpenAI API
OPENAI_API_KEY=votre_clé_api_ici

# Modèles (optionnel, valeurs par défaut utilisées)
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_MODEL=gpt-4o-mini

# Paramètres RAG (optionnel)
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=8
```

## 🚀 Utilisation

### Interface Web (Recommandé)
```bash
# Activer l'environnement
conda activate rag-tsla

# Lancer l'application
python app.py
```

L'interface sera disponible sur : `http://localhost:7860`

### Notebook Jupyter
```bash
# Activer l'environnement
conda activate rag-tsla

# Lancer Jupyter
jupyter notebook RAG_PDF_notebook.ipynb
```

### Première utilisation
1. **Placer vos PDF** dans le dossier `data/`
2. **Lancer l'ingestion** via le notebook ou l'app
3. **Poser vos questions** sur les données financières

## 📊 Configuration

### Variables d'environnement principales

| Variable | Description | Défaut |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Clé API OpenAI (requise) | - |
| `OPENAI_EMBEDDING_MODEL` | Modèle d'embeddings | `text-embedding-3-large` |
| `OPENAI_MODEL` | Modèle LLM | `gpt-4o-mini` |
| `CHUNK_SIZE` | Taille des chunks de texte | `1000` |
| `CHUNK_OVERLAP` | Chevauchement des chunks | `200` |
| `TOP_K` | Nombre de documents récupérés | `8` |

### Paramètres de l'interface

- **k (documents)** : Nombre de sources à récupérer (1-12)
- **Affichage des sources** : Minimal, Compact, ou Détaillé
- **Nettoyer les extraits** : Amélioration de la lisibilité

## 🔍 API et Endpoints

### Pipeline RAG
```python
from fonctions.rag_pipeline import RAGPipeline

# Initialisation
pipeline = RAGPipeline(top_k=8)

# Question-réponse
result = pipeline.answer("Quel est le revenu total au Q1 2023?", [])
answer = result["answer"]
sources = result["hits"]
```

### Ingestion de documents
```python
from fonctions.ingestion import ingest_all_pdfs

# Traiter tous les PDF du dossier data/
vectorstore = ingest_all_pdfs()
```

## 📚 Documentation technique

### Pipeline de traitement

1. **Extraction PDF** : Texte brut + tableaux (Camelot) + OCR (Tesseract)
2. **Chunking** : Découpage intelligent avec RecursiveCharacterTextSplitter
3. **Embeddings** : Vectorisation avec OpenAI text-embedding-3-large
4. **Stockage** : Base vectorielle ChromaDB persistante
5. **Retrieval** : Recherche hybride (tableaux prioritaires + texte)
6. **Génération** : Réponse contextuelle avec GPT-4o-mini

### Stratégie de recherche

- **Priorité aux tableaux** : Recherche filtrée par type "table"
- **Complément texte** : Recherche MMR pour diversité
- **Déduplication** : Élimination des doublons par source/page
- **Normalisation** : Scores normalisés entre 0 et 1

### 🔍 Explication des concepts clés

#### **MMR (Maximal Marginal Relevance)**
**MMR** = **M**aximal **M**arginal **R**elevance

**MMR** est un algorithme de recherche avancé qui optimise la **diversité** des résultats tout en maintenant la **pertinence**.

**Comment ça fonctionne :**
1. **Premier résultat** : Le document le plus similaire à la requête
2. **Résultats suivants** : Documents qui sont à la fois :
   - Pertinents pour la requête
   - Différents des résultats déjà sélectionnés

**Avantages :**
- ✅ Évite la redondance (pas de documents trop similaires)
- ✅ Couvre différents aspects de la question
- ✅ Améliore la qualité globale des réponses

**Exemple concret :**
```
Question : "Quels sont les résultats financiers de Tesla au Q1 2023 ?"

Sans MMR : 5 documents parlant tous du revenu total
Avec MMR : 1 document sur le revenu + 1 sur les marges + 1 sur les livraisons + 1 sur les coûts + 1 sur les perspectives
```

#### **OCR (Optical Character Recognition)**
**OCR** = **O**ptical **C**haracter **R**ecognition

**OCR** est une technologie qui convertit le **texte en image** en **texte numérique** lisible par l'ordinateur.

**Pourquoi c'est important dans ce projet :**
- 📊 **Tableaux complexes** : Certains PDF ont des tableaux sous forme d'images
- 📈 **Graphiques avec texte** : Légendes et annotations sur les graphiques
- 🖼️ **Documents scannés** : PDF créés à partir de documents papier
- 🎨 **Mise en page complexe** : Documents avec des éléments visuels

**Technologie utilisée :**
- **Tesseract** : Moteur OCR open-source de Google
- **Poppler** : Extraction des pages PDF en images
- **Pré-traitement** : Amélioration de la qualité d'image avant OCR

**Pipeline OCR complet :**
```
PDF → Poppler (extraction pages) → Images → Tesseract (OCR) → Texte structuré → Embeddings → Recherche
```

**Exemple d'utilisation :**
```
Document original : Graphique avec "Revenue: $23.3B" en image
Après OCR : Texte "Revenue: $23.3B" → Peut être recherché et analysé
```

#### **Combinaison MMR + OCR**
Cette approche hybride permet de :
- 🎯 **Cibler précisément** les informations pertinentes (MMR)
- 📖 **Lire tout le contenu** même s'il est en image (OCR)
- 🔄 **Éviter la redondance** dans les sources (MMR)
- 📊 **Maximiser la couverture** des données financières

## 🤝 Contribution

### Développement local
```bash
# Cloner et installer en mode développement
git clone <repo>
cd Test
conda create -n rag-tsla-dev python=3.11 -y
conda activate rag-tsla-dev
pip install -r requirements.txt -c constraints.txt
pip install -e .
```

### Tests
```bash
# Lancer les tests (si implémentés)
python -m pytest tests/
```

### Structure des commits
- `feat:` : Nouvelles fonctionnalités
- `fix:` : Corrections de bugs
- `docs:` : Documentation
- `refactor:` : Refactoring du code
- `test:` : Ajout de tests

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 🆘 Support et dépannage

### Problèmes courants

**Erreur d'initialisation**
- Vérifier la présence de `OPENAI_API_KEY` dans `.env`
- S'assurer que l'environnement Conda est activé

**PDF non traités**
- Vérifier que les PDF sont dans le dossier `data/`
- Contrôler les permissions de lecture

**Erreurs de dépendances**
- Réinstaller l'environnement : `conda env remove -n rag-tsla`
- Vérifier la compatibilité Python 3.11+

### Logs et debugging
- Activer le mode debug dans `config.py`
- Vérifier les logs de l'application Gradio
- Utiliser le notebook pour tester les composants individuellement

---

**Développé avec ❤️ pour l'analyse financière intelligente**
