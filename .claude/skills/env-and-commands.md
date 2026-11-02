# Skill: env-and-commands

## Purpose
Exact setup commands, run commands, and env variable contract for this repo.

## When to Use
- Onboarding / first run
- Debugging "connection refused" or import errors
- Adding new env vars (e.g., Azure OpenAI keys)
- Port conflicts

## Full .env for python/server/.env

```env
MONGODB_URI=mongodb://localhost:27017/
DB_NAME=exam_system
PORT=5000
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_API_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=<deployment-name>
AZURE_OPENAI_API_VERSION=2024-02-01
```

## Backend Setup (First Time)

```bash
cd python/server
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
pip install -r requirements.txt
# Create .env with vars above
```

## Backend Run

```bash
cd python/server
source venv/bin/activate
python app.py
# http://localhost:5000
```

## Frontend Setup (First Time)

```bash
cd python/client
npm install
```

## Frontend Run

```bash
cd python/client
npm run dev
# http://localhost:3000
```

## MongoDB

```bash
brew services start mongodb-community   # Mac
# sudo systemctl start mongodb          # Linux
mongosh                                  # verify running
```

## After Adding openai Package

```bash
cd python/server
source venv/bin/activate
pip install openai>=1.0.0
pip freeze > requirements.txt
```

Or manually add `openai>=1.0.0` to requirements.txt then `pip install -r requirements.txt`.

## Port Conflict Resolution

- Backend port: change `PORT` in `.env`, also update `API_BASE_URL` in `python/client/src/api/examApi.js`
- Frontend port: Vite auto-suggests next available port; or edit `python/client/vite.config.js`

## Common Issues

| Error | Fix |
|---|---|
| `ModuleNotFoundError: openai` | `pip install openai>=1.0.0` in venv |
| `Connection refused` on /questions | Start MongoDB + python app.py |
| CORS error | Both servers must be running |
| `pymongo.errors.ServerSelectionTimeoutError` | MongoDB not running |
| Azure 401 | Check AZURE_OPENAI_API_KEY in .env |
| Azure 404 on deployment | Check AZURE_OPENAI_DEPLOYMENT name |
