# Notion MCP Agent - Documentation Complète

## Vue d'ensemble

Ce notebook Jupyter implémente un **agent IA spécialisé** qui interagit avec l'API Notion via le protocole MCP (Model Context Protocol). L'agent permet d'effectuer des opérations avancées sur les bases de données et pages Notion de manière conversationnelle.

## Structure du Notebook

### 1. Configuration Initiale



**Cellules 2-3 : Imports et Configuration**
```python
from agents.mcp.server import MCPServerStdio, MCPServer
from agents import Agent, Runner, gen_trace_id, trace, ModelSettings
from openai.types.responses import ResponseTextDeltaEvent
import os
import asyncio
from dotenv import load_dotenv
```

### 2. Guide de Configuration Notion

**Cellule 4 : Instructions Détaillées**
Guide complet en français pour :
- Créer une intégration Notion
- Récupérer la clé API
- Configurer les permissions
- Utiliser les variables d'environnement

**Points clés :**
- URL d'intégration : https://www.notion.com/my-integrations
- En-tête requis : `Notion-Version: 2022-06-28`
- Bonnes pratiques de sécurité

### 3. Gestion des Clés API

**Cellule 5 : Chargement des Variables d'Environnement**
```python
load_dotenv(dotenv_path=".env", override=True)
notion_key = os.getenv("NOTION_API_KEY")
api_key = os.getenv("OPENAI_API_KEY")
```

**Fonctionnalités :**
- Chargement sécurisé des clés depuis `.env`
- Affichage masqué des clés (premiers caractères uniquement)
- Validation de la présence des clés

### 4. Exploration des Outils MCP

**Cellules 6-9 : Découverte des Capacités**
- Connexion au serveur MCP Notion
- Liste des 19 outils disponibles :
  - `API-get-user` : Récupérer un utilisateur
  - `API-get-users` : Lister tous les utilisateurs
  - `API-post-database-query` : Interroger une base de données
  - `API-post-search` : Rechercher dans Notion
  - `API-get-block-children` : Récupérer les blocs enfants
  - `API-patch-block-children` : Modifier les blocs enfants
  - `API-retrieve-a-block` : Récupérer un bloc
  - `API-update-a-block` : Mettre à jour un bloc
  - `API-delete-a-block` : Supprimer un bloc
  - `API-retrieve-a-page` : Récupérer une page
  - `API-patch-page` : Modifier une page
  - `API-post-page` : Créer une page
  - `API-create-a-database` : Créer une base de données
  - `API-update-a-database` : Mettre à jour une base
  - `API-retrieve-a-database` : Récupérer une base
  - `API-retrieve-a-page-property` : Récupérer une propriété
  - `API-retrieve-a-comment` : Récupérer un commentaire
  - `API-create-a-comment` : Créer un commentaire

### 5. Configuration Asynchrone

**Cellule 10 : Installation nest_asyncio**
```python
!pip install nest_asyncio
```
Permet l'utilisation d'asyncio dans l'environnement Jupyter.

### 6. Fonction Principale

**Cellules 12-13 : Implémentation Main**
```python
async def main():
    async with MCPServerStdio(
        params={
            "command": "npx",
            "args": ["-y", "@notionhq/notion-mcp-server"],
            "env": {
                "OPENAPI_MCP_HEADERS": json.dumps(headers)
            }
        }
    ) as server:
        # Logique de connexion et test
```

### 7. Agent Conversationnel

**Cellules 14-17 : Interface Utilisateur**
- Chargement des instructions depuis `context/example-2/instructions.md`
- Fonction `run()` avec boucle conversationnelle
- Gestion des événements en streaming
- Interface utilisateur interactive

**Fonctionnalités de l'interface :**
- Prompt utilisateur : "Vous : "
- Réponse agent en temps réel
- Indicateurs d'appel d'outils
- Commandes de sortie : 'exit', 'quit', 'bye'

### 8. Implémentation Complète

**Cellule 18 : Agent Final**
Version optimisée avec :
- Gestion d'erreurs robuste
- Interface en français
- Indicateurs visuels pour les appels d'outils
- Configuration complète des headers Notion

## Cas d'Usage Démonstrés

### Exemple d'Interaction
```
Vous : donne moi ma liste de lecture

Agent : 
-- Appel outil : API-post-search
-- Appel outil : API-post-database-query
-- Outil terminé.

Voici ta "liste de lecture" Notion avec les 10 derniers contenus...
```

### Capacités Démontrées
1. **Recherche de contenu** : Interrogation de bases de données Notion
2. **Extraction d'informations** : Récupération de listes de lecture
3. **Gestion de propriétés** : Accès aux statuts et métadonnées
4. **Interface conversationnelle** : Interaction naturelle en français

## Configuration Requise

### Variables d'Environnement (.env)
```env
NOTION_API_KEY=your_notion_integration_token
OPENAI_API_KEY=your_openai_api_key
```

### Dépendances Python
- `agents` : Framework d'agents IA
- `openai` : Client OpenAI
- `python-dotenv` : Gestion des variables d'environnement
- `nest_asyncio` : Support asyncio dans Jupyter

### Prérequis Notion
- Intégration créée sur https://www.notion.com/my-integrations
- Permissions accordées aux bases/pages cibles
- Token d'intégration interne valide

## Architecture Technique

### Protocole MCP
- **Serveur** : `@notionhq/notion-mcp-server` via npx
- **Communication** : STDIO avec headers JSON
- **Authentification** : Bearer token Notion
- **Version API** : 2022-06-28

### Flux de Données
1. **Entrée utilisateur** → Interface conversationnelle
2. **Traitement IA** → Agent GPT-4 avec instructions
3. **Appel MCP** → Serveur Notion via outils
4. **Réponse** → Streaming en temps réel
5. **Affichage** → Interface utilisateur

## Points Forts

### Sécurité
- Clés API masquées dans les logs
- Variables d'environnement sécurisées
- Permissions granulaires Notion

### Robustesse
- Gestion d'erreurs complète
- Connexion asynchrone stable
- Interface utilisateur intuitive

### Extensibilité
- 19 outils MCP disponibles
- Architecture modulaire
- Instructions configurables

## Utilisation

### Démarrage
1. Configurer le fichier `.env` avec les clés API
2. Exécuter les cellules de configuration
3. Lancer l'agent avec `await run_notion_agent_notebook()`

### Commandes Disponibles
- **Recherche** : "donne moi ma liste de lecture"
- **Interrogation** : "trouve les posts sur l'IA"
- **Sortie** : "exit", "quit", "bye"

## Conclusion

Ce notebook représente une implémentation complète d'un agent IA conversationnel spécialisé dans l'interaction avec Notion. Il combine la puissance du protocole MCP avec une interface utilisateur intuitive, permettant des opérations avancées sur les bases de données Notion de manière naturelle et efficace. 