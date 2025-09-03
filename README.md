# GENAI_PRO_Cohorte_1

Ressources officielles de la 1ʳᵉ cohorte du **bootcamp GENAI PRO** : notebooks, scripts, datasets et supports pour apprendre et mettre en pratique l’IA générative, le Prompt Engineering, le RAG multimodal et les agents IA, avec un projet final prêt pour la production.

## Contenu du dépôt

- **`/notebooks`** : Notebooks Jupyter pour les exercices et démonstrations.
- **`/scripts`** : Scripts Python réutilisables.
- **`/datasets`** : Jeux de données pour l'entraînement et les tests.
- **`/supports`** : Présentations, fiches pratiques et ressources pédagogiques.

### Semaine 7 : Fine-tuning des SLMs

**`/Semaine7/FineTuning_SLM.ipynb`** : Notebook complet sur le fine-tuning d'un Small Language Model (SLM) pour la classification de sites de phishing.

**Contenu du notebook :**
- **Théorie des SLMs** : Avantages par rapport aux LLMs (ressources réduites, meilleure interprétabilité, spécialisation)
- **Modèles populaires** : DistilBERT, TinyBERT, ALBERT, MiniLM, etc.
- **Cas pratique** : Classification de sites de phishing avec DistilBERT
- **Techniques avancées** : Freezing des couches de base, optimisation des hyperparamètres
- **Évaluation** : Métriques de performance (Accuracy, AUC, F1-score)
- **Déploiement** : Sauvegarde et utilisation du modèle fine-tuné

**Technologies utilisées :**
- Transformers (Hugging Face)
- Datasets
- PyTorch
- Scikit-learn
- DistilBERT

## Objectifs pédagogiques

- Comprendre les fondamentaux des **LLMs** (Large Language Models).
- Maîtriser le **Prompt Engineering** (de base et avancé).
- Construire des **systèmes RAG multimodaux**.
- Développer et déployer des **agents IA** pour des cas concrets.
- Maîtriser le **fine-tuning des SLMs** (Small Language Models) pour des tâches spécialisées.
- Réaliser un projet final prêt à être utilisé en production.

## Technologies utilisées

- **LangChain**
- **OpenAI API**
- **Hugging Face** (Transformers, Datasets)
- **Ollama**
- **ChromaDB**
- **Streamlit**
- **Gradio**
- **FastAPI**
- **Docker**
- **PyTorch**
- **Scikit-learn**
- **DistilBERT** et autres SLMs

## Organisation du bootcamp

1. **Semaines 1-2** : Fondamentaux LLM et Prompt Engineering.
2. **Semaines 3-4** : RAG textuel et multimodal.
3. **Semaines 5-6** : Agents IA et intégrations avancées.
4. **Semaine 7** : Fine-tuning des SLMs (Small Language Models).
5. **Semaines 6-8** : Projet final (RAG + Agent IA).

## Cloner ce dépôt

- Assurez-vous d'avoir Git installé (`git --version`).
- Clonez le dépôt et entrez dans le dossier:

```bash
git clone https://github.com/natachanj/GENAI_PRO_Cohorte_1.git
cd GENAI_PRO_Cohorte_1
```

## Contribution

Les ressources sont réservées aux participants inscrits.  
Pour toute question, contactez l’équipe GENAI PRO.

## Licence

Ce projet est protégé. Usage privé uniquement.
