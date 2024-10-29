import os

from sqlalchemy import JSON, Integer, String
from sqlalchemy.ext.asyncio import (AsyncAttrs, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secretpass")
POSTGRES_USER = os.getenv("POSTGRES_USER", "swapi")
POSTGRES_DB = os.getenv("POSTGRES_DB", "swapi")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRS_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRS_PORT}/{POSTGRES_DB}"
)


engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass


class SwapiPeople(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    height: Mapped[str] = mapped_column(String)
    mass: Mapped[str] = mapped_column(String)
    hair_color: Mapped[str] = mapped_column(String)
    skin_color: Mapped[str] = mapped_column(String)
    eye_color: Mapped[str] = mapped_column(String)
    birth_year: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String)
    homeworld: Mapped[str] = mapped_column(String)
    films: Mapped[str] = mapped_column(String)  # Список фильмов как строка
    species: Mapped[str] = mapped_column(String)  # Список видов как строка
    starships: Mapped[str] = mapped_column(String)  # Список кораблей как строка
    vehicles: Mapped[str] = mapped_column(String)  # Список транспорта как строка


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
