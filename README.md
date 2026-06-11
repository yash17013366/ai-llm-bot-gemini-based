# AI-Powered LLM Chatbot

A full-stack AI chatbot web application built for an AI/ML internship portfolio. Users can register, log in, create multiple chat sessions, and have multi-turn conversations powered by Google Gemini 2.5 Flash. All conversations are persisted in MongoDB Atlas.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Axios, React Router DOM |
| Backend | FastAPI, PyMongo, JWT, bcrypt |
| Database | MongoDB Atlas |
| AI | Google Gemini API (`gemini-2.5-flash`) |
| Deployment | Vercel (frontend), Render (backend) |

## Features

- User registration and login with JWT authentication
- Create, view, and delete chat sessions
- Multi-turn conversations with last 10 messages as AI context
- Auto-generated chat titles from the first user message
- Responsive UI with collapsible sidebar on mobile
- Typing indicator while awaiting AI responses
- Graceful fallback when the Gemini API is unavailable

## Project Structure

```
llm-chatbot/
├── backend/          # FastAPI application
├── frontend/         # React + Vite application
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas cluster
- Google Gemini API key

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Create `backend/.env` from `backend/.env.example` and fill in your credentials:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

```env
SECRET_KEY=<generated_secret>
MONGODB_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?appName=Cluster0
DATABASE_NAME=llm_chatbot
GEMINI_API_KEY=<your_gemini_api_key>
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Start the API server:

```bash
uvicorn main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
```

Start the dev server:

```bash
npm run dev
```

App: http://localhost:5173

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | No | Register new user, return JWT |
| POST | `/auth/login` | No | Login, return JWT |
| POST | `/chat/new` | Yes | Create new empty chat session |
| POST | `/chat/message` | Yes | Send message, get AI response |
| GET | `/chat/history` | Yes | Get all chats for logged-in user |
| GET | `/chat/{chat_id}` | Yes | Get a single chat with messages |
| DELETE | `/chat/{chat_id}` | Yes | Delete a chat session |

## Deployment

### Backend (Render)

1. Connect your GitHub repository to Render
2. Create a new Web Service using `backend/render.yaml`
3. Set environment variables in the Render dashboard:
   - `SECRET_KEY`
   - `MONGODB_URI`
   - `DATABASE_NAME`
   - `GEMINI_API_KEY`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`

### Frontend (Vercel)

1. Import the repository into Vercel
2. Set the root directory to `frontend`
3. Framework preset: Vite
4. Set `VITE_API_URL` to your Render backend URL (e.g. `https://llm-chatbot-api.onrender.com`)

## Environment Variables

Never commit real `.env` files. Use `.env.example` as a template. Both `backend/.env` and `frontend/.env` are listed in `.gitignore`.

## Author

Yash Gaikwad
