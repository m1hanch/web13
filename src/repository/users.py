from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    The get_user_by_email function takes an email address and returns the user associated with that email.
    If no such user exists, it returns None.

    :param email: str: Define the email address that will be passed in as a parameter to the function
    :param db: AsyncSession: Pass in the database session
    :return: A single user, if it exists
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_user(body: UserSchema, db: AsyncSession):
    """
    The create_user function creates a new user in the database.

    :param body: UserSchema: Validate the data that is passed into the function
    :param db: AsyncSession: Pass the database session to the function
    :return: The newly created user object
    :doc-author: Trelent
    """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
    The update_token function updates the refresh token for a user.

    :param user: User: Specify the user that is being updated
    :param token: str | None: Update the refresh_token field in the database
    :param db: AsyncSession: Pass in the database session
    :return: The user object
    :doc-author: Trelent
    """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession) -> None:
    """
    The confirmed_email function takes in an email and a database session,
    and sets the confirmed field of the user with that email to True.


    :param email: str: Get the user's email address
    :param db: AsyncSession: Pass in a database session
    :return: None
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, avatar_url: str | None, db: AsyncSession) -> User:
    """
    The update_avatar_url function updates the avatar_url of a user.

    :param email: str: Find the user in the database
    :param avatar_url: str | None: Specify that the avatar_url parameter can either be a string or none
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.avatar = avatar_url
    await db.commit()
    await db.refresh(user)
    return user


async def update_password(email: str, password: str, db: AsyncSession) -> User:
    """
    The update_password function takes in an email and a password,
        then updates the user's password with the new one.

    :param email: str: Specify the email of the user to update
    :param password: str: Update the password of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object, which is a good practice
    :doc-author: Trelent
    """
    user = await get_user_by_email(email, db)
    user.password = password
    await db.commit()
    await db.refresh(user)
    return user
