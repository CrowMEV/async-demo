from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from sqlalchemy import JSON, Column
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


load_dotenv()


DB_URI = (
    f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@localhost/{os.getenv('DB_NAME')}"
)
engine = create_async_engine(DB_URI, echo=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class SwapiPeople(Base):
    __tablename__ = "swapi_people"
    id: Mapped[int] = mapped_column(primary_key=True)
    json = Column(JSON)


async def past_to_db(peoples_data: list[dict[str, Any]]):
    async with async_session() as session:
        session.add_all([SwapiPeople(json=item) for item in peoples_data])
        await session.commit()
