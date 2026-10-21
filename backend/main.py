from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(Path(__file__).parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware

from chat.router import router as chat_router
from common.auth_router import router as auth_router
from common.config import CORS_ORIGINS
from common.dummyjson import dummyjson
from common.handlers import log_requests, register_exception_handlers
from common.logging_config import setup_logging
from products.router import router as products_router
from users.router import router as users_router
from warehouses.router import router as warehouses_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await dummyjson.start()
    yield
    await dummyjson.close()


app = FastAPI(title="Stockly API", lifespan=lifespan)

register_exception_handlers(app)

# Order matters: the last one added is the outermost. CORS must wrap log_requests,
# so that error responses also carry the CORS headers.
app.middleware("http")(log_requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(products_router)
app.include_router(users_router)
app.include_router(warehouses_router)
