# 📄 IALab – PDF Analyzer

Application web full-stack permettant d’analyser automatiquement un document PDF via une API backend développée avec FastAPI et utilisant l’API OpenAI pour le traitement intelligent du contenu.

Projet réalisé dans le cadre d’un test technique.

---

# 🧠 Description du projet

L’application permet :

- 📤 Upload d’un fichier PDF depuis l’interface Angular
- ⚙ Envoi du document vers un backend FastAPI
- 🤖 Analyse du contenu via l’API OpenAI
- 📊 Affichage structuré des résultats dans l’interface utilisateur
- ⏳ Indicateur de chargement pendant le traitement
- ❗ Gestion des erreurs

Structure du projet :

- `frontend/` → Application Angular
- `backend/` → API FastAPI (Python)

---

# 🛠 Stack technique

## Frontend
- Angular
- TypeScript
- HTML / CSS

## Backend
- FastAPI
- Uvicorn
- Python
- OpenAI API
- python-dotenv

---

# 🚀 Installation & Lancement

⚠️ Le projet nécessite de lancer **le backend ET le frontend**.

---

# 1️⃣ Configuration de la clé API OpenAI

Le backend nécessite une clé OpenAI valide.

Définir la variable d’environnement avant de lancer le backend.

### Windows (PowerShell)

```bash
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### Mac / Linux

```bash
export OPENAI_API_KEY="your_openai_api_key_here"
```

⚠️ La variable doit être définie dans le même terminal que celui utilisé pour lancer le backend.

---

# 2️⃣ Lancer le Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Backend disponible sur :
http://127.0.0.1:8000

Documentation interactive :
http://127.0.0.1:8000/docs

---

# 3️⃣ Lancer le Frontend

Ouvrir un second terminal :

```bash
cd frontend
npm install
npx ng serve
```

Application disponible sur :
http://localhost:4200

---

# 📌 Important

- Le backend doit être lancé avant le frontend.
- Vérifier que l’URL backend dans le service Angular pointe vers :
  http://127.0.0.1:8000
- En cas d’erreur CORS, vérifier la configuration CORSMiddleware dans FastAPI.

---

# 👤 Auteur

Zakaria Ben Slimene  
Master 2 – Machine Learning & AI  
Université Lyon 2
