import logging
import os
import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

logging.basicConfig(level=logging.DEBUG)


db_user = os.getenv("MYSQL_USER", "dev_user")
db_pwd = os.getenv("MYSQL_PASS", "12345")
db_name = os.getenv("MYSQL_DB", "test")

db_uri = f"mysql+asyncmy://{db_user}:{db_pwd}@127.0.0.1:3306/{db_name}?charset=utf8mb4"

engine = create_async_engine(
    str(db_uri),
    pool_recycle=600,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=30,
    echo=False,
)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession]:
    """Return session for request lifecycle."""
    logging.info("get_db")
    async with SessionLocal() as session, session.begin():
        yield session


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    """Application startup and shutdown logic."""
    logging.info("lifespan start")
    yield
    logging.info("lifespan end")
    try:
        await engine.dispose()
    except Exception as exc:
        logging.info(str(exc))

app = FastAPI(lifespan=lifespan, debug=False)

async def get_result(db):
    await asyncio.sleep(1)
    for i in range(100):
        result = await db.execute(text("SELECT * from user"))
    await asyncio.sleep(1)
    return result

@app.get("/")
async def index(db: Annotated[AsyncSession, Depends(get_db)]):
    logging.info("index")
    result = await get_result(db)
    return {
        "result": str(result.scalar()),
    }
