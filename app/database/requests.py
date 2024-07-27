from app.database.models import async_session
from app.database.models import User, Record
from sqlalchemy import select, update, delete
from datetime import datetime


async def add_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()
            return False
        elif user.name:
            return True
        return False


async def get_audit(date_time_str):
    async with async_session() as session:
        date_time = datetime.fromisoformat(date_time_str)
        user = await session.scalar(select(Record).where(Record.date_time == date_time))

        if user:
            return False
        else:
            return True


async def get_user_rec(user_id):
    async with async_session() as session:
        user = await session.scalar(select(Record).where(Record.user == user_id))

        if not user:
            return False
        return user


async def delete_user_rec(user_id):
    async with async_session() as session:
        await session.execute(delete(Record).where(Record.user == user_id))
        await session.commit()


async def clear_rec():
    async with async_session() as session:
        now = datetime.now()
        await session.execute(delete(Record).where(Record.date_time < now))
        await session.commit()


async def edit_user(tg_id, name, number, insta_name=None):
    async with async_session() as session:
        user = await session.execute(update(User).where(User.tg_id == tg_id).values(name=name, number=number, insta_name=insta_name))
        await session.commit()


async def get_user(u_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == u_id))
        return user


async def add_rec_to_new_table(tg_id, date_time_str, id_event):
    async with async_session() as session:
        date_time = datetime.fromisoformat(date_time_str)
        session.add(Record(user=tg_id, date_time=date_time, id_event=id_event))
        await session.commit()
