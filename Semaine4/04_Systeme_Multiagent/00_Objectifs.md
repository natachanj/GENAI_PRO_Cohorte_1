
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


### Orchestration (checklist pratico-pratique)

1. **Valider l’entrée** : texte non vide, ou URL YouTube valide.
2. **Limiter la taille** : si texte très long, **segmenter** et faire des mini-résumés avant la synthèse.
3. **Appeler Agent 1** : demander explicitement le format de sortie attendu (voir Contrats).
4. **Vérifier la sortie** : présence des 4 blocs (points clés, ton, angles, résumé).
5. **Appeler Agent 2** : fournir la sortie d’Agent 1 + destinataire + instructions (style, longueur max…).
6. **Envoyer** : passer par l’outil email ; récupérer **statut** et **aperçu**.
7. **Afficher** : destinataire, objet, extrait du corps + message de succès/erreur.



### Interface (UI) à prévoir

* Champs :

  * **Zone d’entrée** (texte ou URL YouTube)
  * **Destinataire** (email)
  * **Bouton** « Lancer pipeline multi‑agents »
* Affichages :

  * **Aperçu analyse** (extrait du livrable d’Agent 1)
  * **Aperçu email** (destinataire, objet, extrait du corps)
  * **Statut** (succès/erreur + message clair)



### Bonnes pratiques & erreurs fréquentes

* **Clarté des rôles** : un agent = une mission ; éviter les prompts flous ou surchargés.
* **Contrainte de longueur** : imposer des bornes (ex. objet ≤ 60 caractères, corps < 600 mots).
* **Validation email** : vérifier le format de l’adresse avant d’envoyer.
* **Idempotence** : éviter les doubles envois (désactiver le bouton après clic, afficher un identifiant d’envoi).
* **Fallback** : si l’envoi échoue, afficher le message prêt à copier‑coller.
* **Journalisation** : tracer « qui/quoi/quand » pour pouvoir débugger en cours.



### Scénario d’utilisation (pas à pas)

1. L’utilisateur colle un texte long ou l’URL d’une vidéo YouTube.
2. L’interface récupère le transcript si besoin.
3. **Agent 1** produit un résumé structuré + angles + CTA.
4. **Agent 2** génère l’email final et déclenche l’envoi.
5. L’interface affiche un **aperçu** (destinataire, objet, extrait) et le **statut**.



