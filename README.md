# ✦ NoteAI — AI-Powered Note Taking SaaS

> Capture ideas, get instant AI summaries, and auto-organize with tags.

---

## 🚀 Features

- 🔐 **JWT Authentication** — Secure register, login, auto-refresh tokens
- 📝 **Notes CRUD** — Create, edit, delete notes with auto-save
- ✦ **AI Summarization** — One-click note summary powered by Groq LLaMA AI
- 🏷️ **AI Auto Tagging** — Automatic tag generation using AI
- 🔍 **Search & Filter** — Real-time search + tag-based filtering
- ✍️ **Markdown Editor** — Write in Markdown with live preview
- 📊 **Word Count** — Live word counter

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| Vue 3 (Composition API) | UI Framework |
| Pinia | Global State Management |
| Vue Router 4 | Client-side Routing |
| Axios | HTTP Client + JWT Interceptor |
| Marked.js | Markdown Rendering |
| Vite | Build Tool |

### Backend
| Technology | Purpose |
|------------|---------|
| FastAPI | REST API Framework |
| Motor (Async MongoDB) | Database Driver |
| Pydantic v2 | Data Validation |
| python-jose | JWT Token Management |
| bcrypt | Password Hashing |
| Groq (LLaMA 3) | AI Summarization & Tagging |

### Database & Services
| Service | Purpose |
|---------|---------|
| MongoDB Atlas | Cloud Database |
| Groq API | Free AI (LLaMA 3.3) |

---

## 📁 Project Structure

```
NoteAI/
├── noteai-frontend/          # Vue 3 Frontend
│   ├── src/
│   │   ├── views/
│   │   │   ├── auth/
│   │   │   │   ├── LoginView.vue
│   │   │   │   └── RegisterView.vue
│   │   │   └── dashboard/
│   │   │       └── DashboardView.vue
│   │   ├── stores/
│   │   │   ├── auth.js       # Pinia auth store
│   │   │   └── notes.js      # Pinia notes store
│   │   ├── services/
│   │   │   └── api.js        # Axios + JWT interceptor
│   │   └── router/
│   │       └── index.js      # Vue Router + guards
│   └── package.json
│
└── noteai-backend/           # FastAPI Backend
    ├── app/
    │   ├── routers/
    │   │   ├── auth.py       # Auth endpoints
    │   │   └── notes.py      # Notes + AI endpoints
    │   ├── core/
    │   │   ├── config.py     # Settings
    │   │   ├── database.py   # MongoDB connection
    │   │   ├── security.py   # JWT + bcrypt
    │   │   └── deps.py       # Dependencies
    │   ├── services/
    │   │   └── ai_service.py # Groq AI integration
    │   └── schemas/
    │       ├── user.py
    │       └── note.py
    └── requirements.txt
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB Atlas account (free)
- Groq API key (free)

### Frontend Setup
```bash
cd noteai-frontend
npm install
cp .env.example .env.local
# Add VITE_API_URL=http://localhost:8000/api
npm run dev
```

### Backend Setup
```bash
cd noteai-backend
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
cp .env.example .env
# Fill in .env values (see below)
uvicorn app.main:app --reload --port 8000
```

### Environment Variables (Backend `.env`)
```env
MONGODB_URL=mongodb+srv://<user>:<password>@cluster0.xxxxx.mongodb.net/noteai
JWT_SECRET_KEY=your-secret-key
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
GEMINI_API_KEY=gsk_your_groq_api_key
APP_NAME=NoteAI
DEBUG=True
FRONTEND_URL=http://localhost:5173
```

---

## 🔗 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/refresh` | Refresh token |
| GET | `/api/auth/me` | Current user |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notes/` | Get all notes |
| POST | `/api/notes/` | Create note |
| PUT | `/api/notes/{id}` | Update note |
| DELETE | `/api/notes/{id}` | Delete note |
| POST | `/api/notes/{id}/summarize` | AI summarize |
| POST | `/api/notes/{id}/auto-tag` | AI auto-tag |

---

## 👩‍💻 Developer

**Kajal Kumari**

---

*Built with ❤️ using Vue 3 + FastAPI + MongoDB + Groq AI*