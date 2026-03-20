import logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware 
from app.routers import search, movies, frontend_logs, auth, query, history, interactions
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import search, movies, frontend_logs, auth, query, history
from app.core.logging import setup_logging
from app.services.db_warmup import warmup_db
from app.services.embedding import generate_embedding
from prometheus_fastapi_instrumentator import Instrumentator
from app.routers.profile import router as profile_router

setup_logging()
logger = logging.getLogger("http")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Warming up embedding model...")
    generate_embedding("теплий старт системи")
    warmup_db()
    logger.info("Embedding model warmed up")
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def log_requests(request: Request, call_next):
    logger.info(f"REQUEST  {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"RESPONSE {response.status_code} {request.method} {request.url}")
    return response


app.middleware("http")(log_requests)

app.include_router(search.router)
app.include_router(movies.router)
app.include_router(auth.router)
app.include_router(frontend_logs.router)
app.include_router(query.router)
app.include_router(history.router)
app.include_router(interactions.router)
app.include_router(profile_router)

Instrumentator().instrument(app).expose(app)
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
