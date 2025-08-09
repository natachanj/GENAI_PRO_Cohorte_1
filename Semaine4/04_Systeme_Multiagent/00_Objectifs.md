
## Sujet 4 : **Créer un système multi-agents simple**

### Objectif

Montrer comment faire collaborer plusieurs agents, chacun avec un rôle **clair et limité**, pour accomplir une tâche plus complète : **résumer un contenu** puis **l’envoyer par email**.



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


### Flux de données (sans code)

1. **Entrée** : l’utilisateur colle un texte long ou une URL YouTube.
2. **(Optionnel)** : si URL, récupérer un transcript.
3. **Analyse** : Agent 1 produit un livrable structuré (points clés, résumé, CTA draft).
4. **Communication** : Agent 2 reformate en email (objet + corps), contrôle la longueur et la lisibilité.
5. **Envoi** : Agent 2 appelle l’outil d’email (SMTP Gmail) et renvoie un **statut + aperçu**.
6. **Affichage** : l’interface montre un récap (destinataire, objet, snippet du contenu, statut).


