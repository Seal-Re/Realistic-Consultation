# Realistic-Consultation

Flask backend and a small Vue 3 frontend for a Chinese-medicine "realistic consultation": the user describes symptoms in text, an LLM answers in the role of a virtual doctor, and the answer is spoken by a Live2D avatar.

## Context

Course project (TCM simulated consultation). Backend in `application/`, frontend in `frontend/`. The prompt, conversation and consultation text are Chinese.

## How it works

- `POST /api/AI` (`application/ai.py`): loads the conversation for the session from MongoDB, inserts a fixed Chinese system prompt that casts the model as a virtual doctor, trims the history to 10 messages, and calls DeepSeek (`deepseek-reasoner`) through the `openai` SDK. The reply is appended to the history and saved back.
- `POST /api/AI_new`: creates a new session by incrementing the highest `session_id`.
- `GET /api/content`: returns the stored history without the system prompt, as `{role, content}` objects; accepts an optional `session_id`, otherwise uses the latest.
- `GET /dealAudio` (`application/audio.py` → `utils.createAudio`): synthesizes an MP3 with the edge-tts CLI into `tts/<file_name>` and returns its URL.
- `GET /api/table_list`: looks up documents in the `TablePool` collection by `number`.

The frontend calls `/api/AI` and `/dealAudio` as two separate requests (`frontend/src/App.vue`) and then plays the returned audio through the Live2D model.

## Tech stack

- Backend: Flask 3 + Flask-CORS, pymongo (MongoDB at `mongodb://127.0.0.1:27017/`, database `Realistic-Consultation`, collections `ai_history` and `TablePool`), `openai` SDK against DeepSeek, edge-tts (14 voices mapped in `utils.voiceMap`).
- Frontend: Vue 3 + Vite + axios, Live2D Cubism 4 / PixiJS runtime; several models are bundled under `frontend/src/assets/` (Doro, haru, Hiyori, kei_vowels_pro, March 7th, shizuku) but only the Doro model is loaded.

## Getting started

```bash
# Backend — no requirements file is committed; install Flask, flask-cors, pymongo, openai, edge-tts
python run.py      # http://127.0.0.1:2020

cd frontend
npm install
npm run dev
```

`edge-tts` must be on PATH. Set the DeepSeek key in `application/AIBase.py` (`api_key` is currently empty; `base_url` is `https://api.deepseek.com`). MongoDB must be running locally with the database and collections above.

## Status and limitations

- The repository contains a committed `error.log` (325 lines, April 2025) with Flask dev-server output. It includes the dev debugger PIN, local Windows paths, and full consultation text embedded in request query strings. It should be removed from the repository.
- `test.py` is a seven-line file-existence check. `frontend/README.md` is the unmodified Vite template.

## Contributors / License

MIT — see `LICENSE`. Only Seal-Re has commits.
