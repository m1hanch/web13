from fastapi import APIRouter, HTTPException, Depends, status, Path, Query

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User

from src.repository import contacts as repositories_contacts
from src.schemas.contact import ContactSchema, ContactResponse
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactSchema])
async def get_contacts(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/by-id/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-name/{first_name}', response_model=list[ContactResponse])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db),
                                     user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contacts_by_first_name(first_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-surname/{last_name}', response_model=list[ContactResponse])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db),
                                    user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contacts_by_last_name(last_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-email/{email}', response_model=ContactResponse)
async def get_contact_by_email(email: str, db: AsyncSession = Depends(get_db),
                               user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.get_contact_by_email(email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/birthdays', response_model=list[ContactResponse])
async def get_contacts_by_upcoming_birthday(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                            db: AsyncSession = Depends(get_db)):
    contacts = await repositories_contacts.get_contacts_by_upcoming_birthday(limit, offset, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contact_id}')
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact
