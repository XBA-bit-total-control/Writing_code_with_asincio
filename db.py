from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String

from dotenv import load_dotenv

import os


load_dotenv()

DNS = (f"{os.getenv("DB_DRIVER")}://{os.getenv("DB_LOGIN")}:"
       f"{os.getenv("DB_PASSWORD")}@{os.getenv("DB_HOST")}:"
       f"{os.getenv("DB_PORT")}/{os.getenv("DB_DATABASE")}")

engine = create_async_engine(DNS)
Session = async_sessionmaker(bind=engine)

Base = declarative_base()


class Characters(Base):
    __tablename__ = "персонажи"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    birth_year: Mapped[str] = mapped_column(String(10))
    eye_color: Mapped[str] = mapped_column(String(50))
    gender: Mapped[str] = mapped_column(String(15))
    hair_color: Mapped[str] = mapped_column(String(50))
    homeworld: Mapped[str] = mapped_column(String(90))
    mass: Mapped[str] = mapped_column(String(15))
    name: Mapped[str] = mapped_column(String(105))
    skin_color: Mapped[str] = mapped_column(String(50))


async def open_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_orm():
    await engine.dispose()
