from sqlalchemy import ForeignKey, String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine('sqlite+aiosqlite:///db.sqlite3', echo=True)

async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(25), nullable=True)
    number: Mapped[str] = mapped_column(String(13), nullable=True)
    insta_name: Mapped[str] = mapped_column(String(30), nullable=True)


class Record(Base):
    __tablename__ = 'record'

    id: Mapped[int] = mapped_column(primary_key=True)
    user = mapped_column(ForeignKey('users.id'))
    date_time = mapped_column(DateTime)
    id_event = mapped_column(String(1024))


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
