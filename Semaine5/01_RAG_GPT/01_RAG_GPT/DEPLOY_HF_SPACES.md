## Déployer le projet RAG sur Hugging Face Spaces (Gradio)

Ce guide explique comment déployer votre app Gradio (`app.py`) sur Hugging Face Spaces et éviter le message « Aucun passage pertinent trouvé. » en s’assurant que l’index vectoriel Chroma est disponible au démarrage.

---

### Prérequis

- **Compte Hugging Face** (accès à Spaces)
- **Clé API OpenAI** (`OPENAI_API_KEY`)
- **Repo** contenant au minimum: `app.py`, `fonctions/`, `requirements.txt`, `data/` (PDF)
- Optionnel: `constraints.txt`, `runtime.txt` (ex: `python-3.11`), `packages.txt` si vous voulez des paquets système

---

### 1) Préparer le dépôt

- Assurez-vous que les fichiers suivants existent à la racine:
  - `app.py`
  - `fonctions/` (avec `config.py`, `rag_pipeline.py`, `ingestion.py`, `retrieval.py`, `embeddings.py`, `utils.py`)
  - `requirements.txt`
  - `data/` avec au moins `TSLA-Q1-2023-Update.pdf`
  - `constraints.txt` (optionnel, pour pinner des versions)
  - `runtime.txt` (optionnel, contenu recommandé: `python-3.11`)

- Vérifiez `requirements.txt` (exemples clés):
  - `gradio>=5.0`
  - `langchain`, `langchain-openai`, `langchain-community`, `langchain-chroma`
  - `openai`, `tiktoken`, `chromadb`, `pypdf`, `pandas`, `python-dotenv`
  - Camelot est optionnel; si non installé, l’ingestion se fait en mode dégradé sans extraire les tableaux (pas bloquant).

---

### 2) Créer ou pré-générer l’index Chroma (`.chroma/`)

L’app lit un vecteur store Chroma existant au démarrage. Sans base, vous risquez d’obtenir « Aucun passage pertinent trouvé. »

Choisissez UNE des options:

- **Option A — Pré-calculer localement puis pousser `.chroma/`:**
  1. Installer les dépendances localement:
     ```bash
     pip install -r requirements.txt -c constraints.txt
     ```
  2. Générer la base:
     ```bash
     python - <<'PY'
from fonctions.ingestion import ingest_all_pdfs
ingest_all_pdfs()
print("Chroma prête dans .chroma/")
PY
     ```
  3. Committer le dossier `.chroma/` (si volumineux, utiliser Git LFS), puis pousser.

- **Option B — Construire l’index au démarrage du Space:**
  Ajoutez ce snippet dans `app.py` (juste après les imports) pour lancer l’ingestion si `.chroma/` est vide:
  ```python
  from pathlib import Path
  from fonctions.config import PERSIST_DIR, DATA_DIR
  from fonctions.ingestion import ingest_all_pdfs

  if (not PERSIST_DIR.exists()) or (not any(PERSIST_DIR.iterdir())):
      if any(DATA_DIR.glob("*.pdf")):
          ingest_all_pdfs()
  ```
  - Avantage: vous ne poussez pas `.chroma/`.
  - Inconvénient: premier démarrage plus long.

Remarques:
- L’ingestion fonctionne même si Camelot/Poppler/Tesseract sont absents; seuls les tableaux seront ignorés.
- Assurez-vous que `data/` contient au moins un PDF.

---

### 3) Créer le Space

1. Sur `huggingface.co` → Spaces → **Create new Space**
2. Renseigner:
   - **Name**: ex. `rag-tesla-q1-2023`
   - **SDK**: Gradio
   - **Visibility**: Public ou Private
3. Créez le Space.
4. Uploadez vos fichiers via l’UI du Space (onglet Files) ou connectez le Space à votre repo Git.

---

### 4) Configurer le runtime et les secrets

- Dans l’onglet **Settings** du Space → **Variables and secrets**:
  - Secrets:
    - `OPENAI_API_KEY`: votre clé OpenAI
  - Variables (optionnel):
    - `TOP_K=8`
    - `CHUNK_SIZE=1000`
    - `CHUNK_OVERLAP=200`
    - `LLM_BACKEND=openai` (défaut)
    - `EMBEDDING_BACKEND=openai` (défaut)

- Version de Python (optionnel): créez `runtime.txt` avec:
  ```
  python-3.11
  ```

- Paquets système (optionnel, uniquement si vous voulez l’extraction de tableaux via Camelot):
  - Ajoutez un fichier `packages.txt` contenant par exemple:
    ```
    poppler-utils
    tesseract-ocr
    ghostscript
    ```
  - Et ajoutez `camelot-py` à `requirements.txt`.

---

### 5) Déclencher le build

- Poussez / uploadez les fichiers. Le Space installe les dépendances et lance `app.py` automatiquement (SDK Gradio).
- L’URL du Space est visible en haut à droite du Space.

---

### 6) Tester l’application

- Ouvrez l’URL du Space
- Posez des questions comme:
  - « Quel est le chiffre d’affaires ? »
  - « Quel est le total des revenus ? »
- Vous devriez voir une réponse chiffrée et, à droite, les sources récupérées.

---

### 7) Dépannage: « Aucun passage pertinent trouvé. »

- **Index Chroma absent:**
  - Option A: avez-vous bien commité et poussé `.chroma/` ?
  - Option B: le snippet d’ingestion a-t-il été ajouté et exécuté ? `data/` contient-il un PDF ?
- **Clé OpenAI manquante:**
  - `OPENAI_API_KEY` est-il bien défini en Secret ?
- **Logs du Space:**
  - Onglet **Logs** → vérifier erreurs d’initialisation (LLM, accès disque, etc.)
- **Requêtes trop vagues:**
  - Essayez des formulations guidées (ex: « Quel est le total des revenus au T1 2023 (en $) ? »)
- **Données manquantes:**
  - Vérifiez la présence de `data/TSLA-Q1-2023-Update.pdf` dans l’onglet Files

---

### 8) Bonnes pratiques

- Pour un démarrage rapide: pré-générez `.chroma/` en local et poussez-la.
- Pour alléger le repo: ingestion au démarrage (snippet ci-dessus).
- Conservez les valeurs par défaut `OPENAI_MODEL` et `OPENAI_EMBEDDING_MODEL` sauf besoin spécifique.
- Ajustez `TOP_K` et l’affichage des sources dans l’UI pour une meilleure lisibilité.

---

### 9) Structure finale (exemple)

```
.
├── app.py
├── fonctions/
│   ├── __init__.py
│   ├── config.py
│   ├── embeddings.py
│   ├── ingestion.py
│   ├── rag_pipeline.py
│   ├── retrieval.py
│   └── utils.py
├── data/
│   └── TSLA-Q1-2023-Update.pdf
├── requirements.txt
├── constraints.txt
├── runtime.txt               # optionnel
├── packages.txt              # optionnel (si Camelot/Poppler/Tesseract)
└── .chroma/                  # présent si Option A
```

---

### TL;DR

- Déposez `app.py`, `fonctions/`, `requirements.txt`, `data/` dans un Space Gradio
- Ajoutez `OPENAI_API_KEY` comme Secret
- Assurez la présence de `.chroma/` (pré-générée) ou déclenchez l’ingestion au démarrage (snippet)
- Testez vos questions et vérifiez les **Logs** en cas de souci
