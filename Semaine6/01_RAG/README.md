# Jour 4 — Résumé Automatique de Documents Financiers

## 🎯 Objectif

Transformer rapidement un **rapport financier** (annuel, trimestriel, comptes, bilan, annexes) en un **résumé clair et chiffré** grâce à l'IA générative.

## ✨ Fonctionnalités Implémentées

### 📊 Analyse Automatique de PDF
- **Lecture intelligente** : Extraction du texte page par page avec repères clairs
- **Nettoyage automatique** : Suppression des espaces inutiles et formatage
- **Gestion de la longueur** : Limitation automatique pour éviter les dépassements d'API

###  IA Générative Spécialisée
- **Modèle OpenAI** : Utilisation de GPT-4o-mini pour l'analyse
- **Prompting spécialisé** : Instructions d'analyste financier avec format de sortie structuré
- **Résumé structuré** : Format Markdown avec sections prédéfinies

###  Résumé Financier Structuré
Le système génère automatiquement :
- **Informations générales** : Société, période, devise
- **Résumé exécutif** : 5-8 lignes d'analyse
- **Chiffres clés** : Tableau avec indicateurs, valeurs, évolutions et références de pages
- **Analyse détaillée** : Performance, structure financière, risques, outlook
- **Références internes** : Pages et sections à relire

###  Questions Interactives
- **Interface de questions** : Possibilité de poser des questions spécifiques sur le PDF
- **Réponses sourcées** : Références aux pages d'origine
- **Précision garantie** : Pas d'invention de données

### 🌐 Interface Web Streamlit
- **Application web moderne** : Interface intuitive et responsive
- **Upload de fichiers** : Glisser-déposer de PDF directement dans le navigateur
- **Analyse en temps réel** : Résumé et questions sans quitter l'interface
- **Téléchargement** : Export des résumés en format Markdown
- **Questions suggérées** : Interface cliquable pour les questions courantes

## Comment Utiliser

### Prérequis
- Python 3.10+
- Clé API OpenAI valide
- Document PDF financier à analyser

### Installation

1. **Cloner le repository**
```bash
git clone https://github.com/natachanj/GENAIExpress.git
cd GENAIExpress/Jour4
```

2. **Créer un environnement conda**
```bash
conda create -n genai-jour4 python=3.11
conda activate genai-jour4
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Installer ipykernel pour Jupyter**
```bash
python -m ipykernel install --user --name genai-jour4 --display-name "GENAI Jour4"
```

### Lancement de l'Application Streamlit

```bash
conda activate genai-jour4
streamlit run app.py
```

L'application s'ouvrira dans votre navigateur à l'adresse : `http://localhost:8501`

4. **Configuration des variables d'environnement**
Créer un fichier `.env` à la racine du projet :
```bash
# Copier le fichier d'exemple
cp env_example.txt .env

# Éditer le fichier .env et ajouter votre clé API
OPENAI_API_KEY=votre_cle_api_openai
```

**Note :** Obtenez votre clé API sur [platform.openai.com](https://platform.openai.com/api-keys)

### Utilisation

1. **Lancer Jupyter Lab**
```bash
jupyter lab
```

2. **Ouvrir le notebook**
Ouvrir `resume_documents_financiers.ipynb`

3. **Sélectionner le kernel conda**
Dans Jupyter, en haut à droite, sélectionner le kernel "GENAI Jour4" (conda)

3. **Placer votre PDF**
Mettre votre document financier dans le dossier `data/`

4. **Exécuter les cellules**
Suivre l'ordre des cellules pour :
- Charger les dépendances
- Configurer l'API
- Analyser le PDF
- Générer le résumé
- Poser des questions spécifiques

## 📁 Structure du Projet

```
Jour4/
├── data/
│   └── teslafinancialreport.pdf    # Exemple de document
├── resume_documents_financiers.ipynb  # Notebook principal
├── app.py                          # Application Streamlit
├── requirements.txt                 # Dépendances Python
└── README.md                       # Ce fichier
```

## 🔧 Technologies Utilisées

- **OpenAI API** : Modèles GPT-4o pour l'analyse de texte
- **PyMuPDF** : Lecture et extraction de contenu PDF
- **Python-dotenv** : Gestion des variables d'environnement
- **IPython** : Affichage Markdown dans Jupyter
- **Jupyter** : Environnement de développement interactif

## 📋 Format de Sortie

Le résumé généré suit cette structure :

```markdown
# Synthèse financière de [Société] - [Période]

- **Société / Période / Devise** : [Informations]

- **Résumé exécutif** : [5-8 lignes d'analyse]

- **Chiffres clés** :
| Indicateur | Valeur | Évolution/Contexte | Période | Page |
|------------|--------|-------------------|---------|------|
| [Données extraites] |

- **Analyse** : [Performance, Structure, Risques, Outlook]

- **Références internes** : [Pages à relire]
```

## ⚠️ Bonnes Pratiques

- **Vérification** : Toujours vérifier les chiffres affichés et leurs pages d'origine
- **Précision** : En cas d'ambiguïté, utiliser "non précisé" plutôt que d'inventer
- **Sécurité** : Limiter la taille des documents pour éviter les dépassements d'API
- **Confidentialité** : Ne pas partager de documents sensibles via l'API

## 🎯 Cas d'Usage

- **Analystes financiers** : Résumé rapide de rapports trimestriels
- **Investisseurs** : Analyse comparative de documents financiers
- **Étudiants** : Compréhension de rapports financiers complexes
- **Consultants** : Préparation de présentations client

## 🔮 Évolutions Futures

- [ ] Support multi-format (Word, Excel)
- [ ] Analyse comparative entre documents
- [ ] Génération de graphiques automatiques
- [ ] Export en différents formats (PDF, PowerPoint)
- [ ] Interface web simplifiée

## 📚 Ressources

- [Documentation OpenAI](https://platform.openai.com/docs)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [Challenge GENAIExpress](https://github.com/natachanj/GENAIExpress)

---

**Note** : Ce projet fait partie du challenge GENAIExpress - Démarrer avec l'IA Générative en 5 jours.


