import calendar
from datetime import date, timedelta, datetime

from sqlalchemy import select, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.contact import ContactSchema
from src.entity.models import Contact, User


async def get_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactSchema, db: AsyncSession, user: User):
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
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_contacts_by_first_name(first_name: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(first_name=first_name, user=user)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contacts_by_last_name(last_name: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(last_name=last_name, user=user)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact_by_email(email: str, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(email=email, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def get_contacts_by_upcoming_birthday(limit: int, offset: int, db: AsyncSession):
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
