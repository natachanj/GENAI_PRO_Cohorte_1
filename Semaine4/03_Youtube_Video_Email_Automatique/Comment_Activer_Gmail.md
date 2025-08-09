# README — Configuration du mot de passe d’application Gmail pour SMTP dans l’application

Ce guide explique comment obtenir et utiliser les variables `GMAIL_EMAIL` et `GMAIL_APP_PASSWORD` dans ton `.env` afin de permettre à l’application d’envoyer des emails via Gmail.

---

## 1️⃣ Activer la validation en deux étapes (2FA)

1. Va sur [https://myaccount.google.com/security](https://myaccount.google.com/security)
2. Dans **"Connexion à Google"**, clique sur **"Validation en deux étapes"**
3. Active la 2FA en suivant les instructions (SMS, Google Authenticator, etc.)

---

## 2️⃣ Accéder directement à la page des mots de passe d’application

Une fois la 2FA activée, va sur : [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

> 💡 Cette page n’apparaît que si tu as un compte Google personnel ou si ton administrateur Workspace l’a autorisée.

---

## 3️⃣ Générer un mot de passe d’application

1. Dans **Sélectionner l’application**, choisis **"Autre (nom personnalisé)"**
2. Donne un nom (ex : `YouTube Transcript App`) et clique sur **Générer**
3. Google affiche un mot de passe à 16 caractères (ex : `abcd efgh ijkl mnop`)
4. **Copie-le** et **colle-le sans espaces** : tu dois obtenir une suite de 16 caractères collés, par exemple `abcdefghijkmnop`. Ce sera ta valeur `GMAIL_APP_PASSWORD`.

---

## 4️⃣ Ajouter au fichier `.env`

```env
OPENAI_API_KEY=sk-...
GMAIL_EMAIL=ton_adresse@gmail.com
GMAIL_APP_PASSWORD=motdepasseapplication16caracteres
```

⚠️ Utilise uniquement le mot de passe d’application généré, **jamais** ton mot de passe Gmail principal.

---

## 5️⃣ Utilisation dans l’application

Dans l’application, ces variables sont lues automatiquement :

```python
GMAIL_CONFIG = {
    "email": os.getenv("GMAIL_EMAIL", "").strip(),
    "password": os.getenv("GMAIL_APP_PASSWORD", "").strip(),
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
}
```

Si elles sont présentes et correctes, le bouton **"Envoyer le résultat par email"** dans l’interface :

* Enverra le dernier transcript ou la dernière réponse IA par Gmail
* Affichera un **aperçu de l’email envoyé** (destinataire, sujet, contenu)

---

## 6️⃣ Exemple d’aperçu après envoi

```
✅ Email envoyé
--- Aperçu ---
De: ton_adresse@gmail.com
À: destinataire@example.com
Sujet: Résultat YouTube
Contenu:
[Transcription ou analyse générée]
```
