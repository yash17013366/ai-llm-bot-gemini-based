import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from database import ensure_indexes
from routes import auth_routes, chat_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ensure_indexes()
    except (ServerSelectionTimeoutError, ConnectionFailure) as exc:
        logger.warning(
            "Database index setup deferred — MongoDB unreachable at startup: %s. "
            "Indexes will be created on first successful connection. "
            "If this persists, check Atlas Network Access (IP whitelist) and SSL/TLS settings.",
            exc,
        )
    except Exception as exc:
        logger.warning("Database index setup deferred: %s", exc)
    yield


app = FastAPI(
    title="LLM Chatbot API",
    description="AI-powered chatbot backend with JWT authentication and Gemini integration",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(chat_routes.router)


@app.get("/")
def root():
    return {"message": "LLM Chatbot API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
    )
