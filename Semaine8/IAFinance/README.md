# IAFINANCE - Conseiller d'Investissement Assisté par IA

## Description

IAFINANCE est une application d'analyse financière qui combine l'analyse traditionnelle des marchés financiers avec l'intelligence artificielle pour fournir des recommandations d'investissement personnalisées. L'application analyse automatiquement les données boursières, calcule des métriques techniques, génère des signaux de trading et produit des conseils d'investissement via l'API OpenAI.

## Fonctionnalités

- **Analyse automatisée** des données boursières (cours, métriques techniques)
- **Recommandations personnalisées** basées sur votre profil de risque (prudent/équilibre/dynamique)
- **Plan d'allocation de budget** avec répartition automatique des poids
- **Signaux de trading** avec règles de gestion du risque
- **Projections indicatives** de performance (non garanties)
- **Interface web intuitive** via Gradio
- **Backtesting** de stratégies simples (moyennes mobiles)
- **Rapports détaillés** en markdown

## Structure du Projet

```
IAFINANCE/
├── README.md                          # Documentation du projet
├── requirements.txt                   # Dépendances Python
├── main.py                           # Script principal pour l'analyse
├── app.py                            # Interface web Gradio
├── 01_ia_finance_prompt_app.ipynb    # Notebook d'exemple et démonstration
├── fonctions/                        # Modules utilitaires
│   ├── __init__.py                  # Exports des fonctions
│   ├── data_utils.py                # Chargement et traitement des données
│   ├── metrics_utils.py             # Calcul des métriques techniques
│   ├── rules_engine.py              # Moteur de règles et signaux
│   ├── reporting.py                 # Génération des rapports
│   ├── ia_utils.py                  # Utilitaires pour l'IA
│   ├── backtest.py                  # Fonctions de backtesting
│   └── symbols.py                   # Détection et validation des symboles
```

### Modules Principaux

- **`data_utils.py`** : Chargement des données boursières via yfinance
- **`metrics_utils.py`** : Calcul des métriques (RSI, moyennes mobiles, volatilité, drawdown)
- **`rules_engine.py`** : Génération de signaux de trading et règles de gestion du risque
- **`reporting.py`** : Création de rapports détaillés en markdown
- **`ia_utils.py`** : Interface avec l'API OpenAI pour les conseils personnalisés
- **`backtest.py`** : Backtesting de stratégies d'investissement
- **`symbols.py`** : Détection automatique des tickers et résolution des noms d'entreprises

## Installation

### Prérequis

- Python 3.8 ou supérieur
- Conda (recommandé pour la gestion des environnements)

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd IAFINANCE
```

### 2. Créer l'environnement virtuel avec Conda

```bash
# Créer un nouvel environnement conda
conda create -n iafinance python=3.11

# Activer l'environnement
conda activate iafinance
```

### 3. Installer les dépendances

```bash
# Installer les packages depuis requirements.txt
pip install -r requirements.txt
```

### 4. Configuration pour Jupyter (ipykernel)

Pour utiliser le projet dans Jupyter Notebook/Lab, ajoutez l'environnement conda au kernel :

```bash
# Ajouter l'environnement conda à ipykernel
conda install ipykernel

# Enregistrer l'environnement comme kernel Jupyter
python -m ipykernel install --user --name iafinance --display-name "IAFINANCE (Python 3.11)"
```

**Note** : Après cette étape, vous pourrez sélectionner le kernel "IAFINANCE (Python 3.11)" dans vos notebooks Jupyter.

### 5. Configuration de l'API OpenAI (optionnel)

Créez un fichier `.env` à la racine du projet :

```bash
# Créer le fichier .env
touch .env
```

Ajoutez votre clé API OpenAI dans le fichier `.env` :

```
OPENAI_API_KEY=sk-votre-cle-api-ici
```

**Note** : L'application fonctionne sans clé API, mais certaines fonctionnalités IA seront limitées.

## Utilisation

### Interface Web (Recommandé)

Lancez l'interface web Gradio :

```bash
python app.py
```

L'application sera accessible à l'adresse : `http://localhost:7860`

### Script Principal

Pour une analyse directe :

```bash
python main.py
```

### Notebook Jupyter

Ouvrez le notebook d'exemple :

```bash
jupyter notebook 01_ia_finance_prompt_app.ipynb
```

Assurez-vous de sélectionner le kernel "IAFINANCE (Python 3.11)" dans Jupyter.

## Configuration

### Profils de Risque

L'application propose trois profils de risque :

- **Prudent** : Favorise la stabilité et la volatilité réduite
- **Équilibre** : Mix entre rendement et risque modéré
- **Dynamique** : Favorise le momentum et les tendances fortes

### Paramètres d'Analyse

- **Horizon** : Période d'analyse (3-60 mois)
- **Budget** : Montant total à investir
- **Achats étalés** : Nombre de mois pour étaler les investissements

## Exemples d'Utilisation

### Analyse de titres populaires

```python
# Dans main.py, modifiez les paramètres :
TICKERS = ["AAPL", "MSFT", "GOOGL", "TSLA"]
PROFIL = "equilibre"
HORIZON = 12
```

### Interface Web

1. Saisissez les titres (noms ou symboles)
2. Définissez votre budget et profil de risque
3. Cliquez sur "Générer"
4. Consultez les onglets de résultats

## Dépendances

Les principales dépendances sont listées dans `requirements.txt` :

- **yfinance** : Téléchargement des données boursières
- **pandas** : Manipulation des données
- **numpy** : Calculs numériques
- **matplotlib** : Visualisation des graphiques
- **openai** : API pour les conseils IA
- **gradio** : Interface web
- **python-dotenv** : Gestion des variables d'environnement

## Limitations et Avertissements

⚠️ **IMPORTANT** : Cette application est à des fins éducatives uniquement et ne constitue pas un conseil en investissement personnalisé.

- Les projections sont indicatives et non garanties
- Les performances passées ne préjugent pas des résultats futurs
- Effectuez toujours vos propres vérifications (DYOR)
- Consultez un conseiller financier pour des décisions importantes

## Support et Contribution

Pour signaler des bugs ou proposer des améliorations, veuillez créer une issue sur le repository.

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

---

**Développé avec ❤️ pour l'analyse financière assistée par IA**
