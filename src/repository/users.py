from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    stmt = select(User).filter_by(email=email)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession):
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, avatar_url: str | None, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(email: str, password: str, db: AsyncSession) -> User:
    user = await get_user_by_email(email, db)
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user
