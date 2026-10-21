# Stockly

Product and warehouse management dashboard with an AI chat assistant.

## Stack

- **Backend** — Python / FastAPI, data from [DummyJSON](https://dummyjson.com), AI via Groq
- **Frontend** — Vue 3, Vuetify, Vite

## Getting started

```bash
npm run setup   # install all dependencies (frontend + backend venv)
npm run dev     # start backend (port 8000) and frontend (port 5173) concurrently
```

Copy `.env.example` to `.env` and fill in your API keys before running.

## Environment variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key (powers the chat assistant) |
| `JWT_SECRET` | Secret used to sign JWTs — change in production |
| `LOW_STOCK_THRESHOLD` | Units at or below which a product is "low stock" (default: 10) |

## Project structure

```
backend/
  chat/         AI chat assistant
  common/       Auth, config, error handling
  products/     Product catalogue and analytics
  users/        User management
  warehouses/   Warehouse stock and reorder reports
frontend/
  src/
    components/ Reusable UI components
    composables/ Shared Vue logic
    views/      Page-level views
    layouts/    App shell (nav + header)
```

## Running tests

```bash
cd backend
.venv/Scripts/python -m pytest   # Windows
.venv/bin/python -m pytest       # macOS / Linux
```
