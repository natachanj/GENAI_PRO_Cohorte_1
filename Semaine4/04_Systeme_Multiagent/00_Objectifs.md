Pour un cours simple aujourd'hui sur les agents IA, tu pourrais leur apprendre :

## Sujet 1 : **Créer un Agent IA capable de réaliser une tâche unique et utile**

### Objectif

Montrer comment construire un agent qui combine **une API externe** et **un modèle de langage**, et qui exécute automatiquement une action à partir d'une instruction simple.

### Idée simple d'exercice

Créer un **agent météo** :

* L'utilisateur donne une ville et un jour
* L'agent utilise une API météo pour récupérer la prévision
* L'agent formate la réponse de manière naturelle

💡 **Note sur l’API** :

* Utiliser **OpenWeatherMap** (plan gratuit disponible)
* Créer un compte sur [https://openweathermap.org/api](https://openweathermap.org/api) et récupérer une clé API
* Possibilité de simuler les réponses pour éviter les limites ou problèmes de connexion

### Points à enseigner

1. **Structure d’un agent IA**

   * **Entrées** (prompt + paramètres)
   * **Outils** (fonctions Python ou API externes)
   * **Raisonnement et exécution**
   * **Sortie** (réponse à l’utilisateur)

2. **Utilisation de `function_tool`** pour exposer une fonction météo

3. **Création de l’agent** avec `Agent()` et ajout de l’outil

4. **Scénarios d'utilisation**

5. **Extensions possibles**

---

## Sujet 2 : **Créer un Agent IA qui interagit avec un fichier local**

### Objectif

Apprendre à connecter un agent à un fichier texte ou CSV pour effectuer une analyse ou extraire des informations.

### Idée simple d'exercice

Créer un **agent lecteur de fichiers** :

* L’utilisateur téléverse un fichier texte ou CSV
* L’agent lit le contenu et répond aux questions sur ce fichier

### Points à enseigner

* Utiliser `function_tool` pour lire un fichier et retourner le contenu
* Passer ce contenu dans le contexte de l’agent
* Limiter la taille du contenu (chunking)

---

## Sujet 3 : **Créer un Agent IA qui envoie un email**

### Objectif

Apprendre à connecter l’agent à un service SMTP (ex : Gmail avec mot de passe d’application) pour envoyer un résultat.

### Idée simple d'exercice

* L’utilisateur donne une adresse email et un message
* L’agent utilise un outil `send_email` pour envoyer le message et confirmer l’envoi

### Points à enseigner

* Utilisation d’une configuration `.env`
* Envoi d’emails texte et HTML
* Confirmation et aperçu dans l’interface

---

## Sujet 4 : **Créer un système multi-agents simple**

### Objectif

Montrer comment faire collaborer plusieurs agents, chacun avec un rôle **clair et limité**, pour accomplir une tâche plus complète : **résumer un contenu** puis **l’envoyer par email**.

---

### Rôles (responsabilités nettes)

* **Agent 1 — Analyse**

  * Synthétise un texte/transcript.
  * Extrait 5–8 points clés, le ton et les intentions de l’auteur.
  * Propose un résumé exécutif court et un angle/CTA potentiel.
* **Agent 2 — Communication**

  * Transforme le livrable d’Agent 1 en message prêt à l’envoi (objet + corps d’email structuré).
  * Vérifie la clarté, ajoute une conclusion/CTA, puis déclenche l’envoi.
* **Orchestrateur**

  * Reçoit l’entrée utilisateur (texte brut ou URL YouTube).
  * Déclenche Agent 1, récupère sa sortie, la passe à Agent 2.
  * Gère les erreurs et affiche un **aperçu** de l’email envoyé.

---

### Flux de données (sans code)

1. **Entrée** : l’utilisateur colle un texte long ou une URL YouTube.
2. **(Optionnel)** : si URL, récupérer un transcript.
3. **Analyse** : Agent 1 produit un livrable structuré (points clés, résumé, CTA draft).
4. **Communication** : Agent 2 reformate en email (objet + corps), contrôle la longueur et la lisibilité.
5. **Envoi** : Agent 2 appelle l’outil d’email (SMTP Gmail) et renvoie un **statut + aperçu**.
6. **Affichage** : l’interface montre un récap (destinataire, objet, snippet du contenu, statut).

---

### Contrats d’E/S entre les agents

* **Entrée Agent 1** : un texte clair (ou transcript) avec contexte minimal (thème, audience, objectif).
* **Sortie Agent 1** :

  * Points clés (liste numérotée)
  * Ton & intentions (2–3 phrases)
  * 2–3 angles d’email possibles
  * Résumé exécutif (120–180 mots)
* **Entrée Agent 2** : la sortie d’Agent 1 + le destinataire + instructions de style (professionnel, concis…).
* **Sortie Agent 2** :

  * Objet concis (≤ 60 caractères)
  * Corps d’email structuré (titres, listes, paragraphe de conclusion + CTA)
  * Préheader court (optionnel)
  * Statut d’envoi + aperçu (destinataire, objet, extrait du message)

---

### Orchestration (checklist pratico-pratique)

1. **Valider l’entrée** : texte non vide, ou URL YouTube valide.
2. **Limiter la taille** : si texte très long, **segmenter** et faire des mini-résumés avant la synthèse.
3. **Appeler Agent 1** : demander explicitement le format de sortie attendu (voir Contrats).
4. **Vérifier la sortie** : présence des 4 blocs (points clés, ton, angles, résumé).
5. **Appeler Agent 2** : fournir la sortie d’Agent 1 + destinataire + instructions (style, longueur max…).
6. **Envoyer** : passer par l’outil email ; récupérer **statut** et **aperçu**.
7. **Afficher** : destinataire, objet, extrait du corps + message de succès/erreur.

---

### Interface (UI) à prévoir

* Champs :

  * **Zone d’entrée** (texte ou URL YouTube)
  * **Destinataire** (email)
  * **Bouton** « Lancer pipeline multi‑agents »
* Affichages :

  * **Aperçu analyse** (extrait du livrable d’Agent 1)
  * **Aperçu email** (destinataire, objet, extrait du corps)
  * **Statut** (succès/erreur + message clair)

---

### Bonnes pratiques & erreurs fréquentes

* **Clarté des rôles** : un agent = une mission ; éviter les prompts flous ou surchargés.
* **Contrainte de longueur** : imposer des bornes (ex. objet ≤ 60 caractères, corps < 600 mots).
* **Validation email** : vérifier le format de l’adresse avant d’envoyer.
* **Idempotence** : éviter les doubles envois (désactiver le bouton après clic, afficher un identifiant d’envoi).
* **Fallback** : si l’envoi échoue, afficher le message prêt à copier‑coller.
* **Journalisation** : tracer « qui/quoi/quand » pour pouvoir débugger en cours.

---

### Scénario d’utilisation (pas à pas)

1. L’utilisateur colle un texte long ou l’URL d’une vidéo YouTube.
2. L’interface récupère le transcript si besoin.
3. **Agent 1** produit un résumé structuré + angles + CTA.
4. **Agent 2** génère l’email final et déclenche l’envoi.
5. L’interface affiche un **aperçu** (destinataire, objet, extrait) et le **statut**.

---

### Évaluation rapide (pour la classe)

* **Fidélité** : le résumé reflète‑t‑il bien le contenu source ?
* **Lisibilité** : l’email est‑il clair, aéré, actionnable ?
* **Concision** : respect des limites de longueur.
* **Robustesse** : gestion des entrées vides, URL invalides, échec SMTP.

---

### Variantes si tu as 10–15 minutes de plus

* Ajouter un **Agent 3 – Réseaux sociaux** pour générer un post LinkedIn/Instagram à partir du résumé d’Agent 1.
* **Branche décisionnelle** : si le contenu contient un appel à l’inscription/vente, adapter automatiquement le CTA.
* **Mesure** : compter les mots, estimer le temps de lecture, afficher un score de clarté.
