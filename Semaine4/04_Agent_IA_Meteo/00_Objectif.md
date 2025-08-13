Pour un cours simple aujourd'hui sur les agents IA, tu pourrais leur apprendre :

## Sujet : **Créer un Agent IA capable de réaliser une tâche unique et utile**

### Objectif

Montrer comment construire un agent qui combine **une API externe** et **un modèle de langage**, et qui exécute automatiquement une action à partir d'une instruction simple.

### Idée simple d'exercice

Créer un **agent météo** :

* L'utilisateur donne une ville et un jour
* L'agent utilise une API météo pour récupérer la prévision
* L'agent formate la réponse de manière naturelle

💡 **Note sur l’API** :

* Pour un usage simple et gratuit, on peut utiliser **OpenWeatherMap** qui propose un **plan gratuit** avec un nombre limité de requêtes par minute.
* Il faut simplement créer un compte sur [https://openweathermap.org/api](https://openweathermap.org/api) et récupérer une clé API.
* Pendant le cours, tu peux aussi simuler les réponses (sans appel réel) pour éviter les limites ou problèmes de connexion.

### Points à enseigner

1. **Structure d’un agent IA**

   * **Entrées** (prompt + paramètres)
   * **Outils** (fonctions Python ou API externes)
   * **Raisonnement et exécution**
   * **Sortie** (réponse à l’utilisateur)

2. **Utilisation de `function_tool`** pour exposer une fonction météo

```python
@function_tool
def get_weather(city: str, date: str) -> str:
    # Simulation pour l'exemple
    return f"La météo à {city} le {date} sera ensoleillée, 24°C."
```

3. **Création de l’agent** avec `Agent()` et ajout de l’outil

4. **Scénarios d'utilisation**

   * Poser une question météo simple
   * Demander une prévision dans un format particulier (tableau, résumé, style humoristique)

5. **Extensions possibles**

   * Ajouter un deuxième outil (ex. : conversion de température °C ↔ °F)
   * Lier à une API réelle comme OpenWeatherMap (gratuite mais nécessite une clé API)

### Résultat attendu

À la fin, les apprenants sauront :

* Créer un agent avec un outil dédié
* Comprendre le flux **question → exécution de l’outil → réponse IA**
* Modifier l’agent pour d'autres tâches simples
