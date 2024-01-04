import calendar
from datetime import date, timedelta, datetime

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contact import ContactSchema
from src.entity.models import Contact, User


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Determine the starting point of the query
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Filter the contact by id
    :param db: AsyncSession: Pass the database session into the function
    :param user: User: Filter the contacts by user
    :return: A single contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Access the database
    :param user: User: Get the user from the request
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify which contact to update
    :param body: ContactSchema: Get the data from the body of the request
    :param db: AsyncSession: Pass in a database session
    :param user: User: Ensure that the user is only able to update their own contacts
    :return: A contact object or none
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        for field in body.model_fields_set:
            setattr(contact, field, getattr(body, field))
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the contact to delete
    :param db: AsyncSession: Pass in the database connection
    :param user: User: Get the user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_contacts_by_first_name(first_name: str, db: AsyncSession, user: User):
    """
    The get_contacts_by_first_name function returns a list of contacts with the given first name.

    :param first_name: str: Specify the first name of the contact you want to get
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contacts with the given first name
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(first_name=first_name, user=user)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_by_last_name(last_name: str, db: AsyncSession, user: User):
    """
    The get_contacts_by_last_name function returns a list of contacts with the given last name.

    :param last_name: str: Filter the contacts by last name
    :param db: AsyncSession: Pass in the database session to the function
    :param user: User: Filter the contacts by user
    :return: A list of contact objects
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(last_name=last_name, user=user)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_email(email: str, db: AsyncSession, user: User):
    """
    The get_contact_by_email function takes in an email and a database session,
    and returns the contact with that email. If no such contact exists, it returns None.

    :param email: str: Get the email of a contact
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the user is only able to get contacts that they have created
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(email=email, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def get_contacts_by_upcoming_birthday(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts_by_upcoming_birthday function returns a list of contacts with birthdays in the next 7 days.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first n records
    :param db: AsyncSession: Pass the database session into the function
    :return: A list of contact objects
    :doc-author: Trelent
    """
    today = datetime.now()
    in_week = (today + timedelta(days=7)).timetuple()[1:3]
    today = (today.month, today.day)
    if today > in_week:
        stmt = select(Contact).offset(offset).limit(limit).filter(or_(
            and_(
                func.extract('month', Contact.birthday) == today[0],
                func.extract('day', Contact.birthday) >= today[1],
            ),
            and_(
                func.extract('month', Contact.birthday) == in_week[0],
                func.extract('day', Contact.birthday) <= in_week[1],
            )
        ))
    else:
        stmt = (
            select(Contact)
            .offset(offset)
            .limit(limit)
            .filter(
                and_(
                    func.extract('month', Contact.birthday) >= today[0],
                    func.extract('day', Contact.birthday) >= today[1],
                    func.extract('month', Contact.birthday) <= in_week[0],
                    func.extract('day', Contact.birthday) <= in_week[1],
                )
            )
        )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()
