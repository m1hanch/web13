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
    """
    The get_contacts function returns a list of contacts.

    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value for a parameter
    :param le: Limit the maximum number of contacts that can be returned
    :param offset: int: Set the offset of the query
    :param ge: Specify a minimum value for the limit parameter
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user
    :return: A list of contacts
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts(limit, offset, db, user)
    return contacts


@router.get('/by-id/{contact_id}', response_model=ContactResponse)
async def get_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact function is used to retrieve a single contact from the database.
    The function takes in an integer value for the contact_id, which is then passed into
    the get_contact function of the contacts repository. The user object that was retrieved
    from auth_service's get_current_user dependency is also passed into this function as well.

    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-name/{first_name}', response_model=list[ContactResponse])
async def get_contacts_by_first_name(first_name: str, db: AsyncSession = Depends(get_db),
                                     user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_first_name function is used to retrieve a contact by their first name.
        The function takes in the first_name parameter, which is a string that represents the
        contact's first name. It also takes in an optional db parameter, which is an AsyncSession object
        that represents the database connection and defaults to Depends(get_db). Finally, it takes in an optional user parameter,
        which is a User object representing the current user and defaults to Depends(auth_service.get_current_user).

    :param first_name: str: Get the first name of a contact
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user
    :return: A list of contacts with the given first name
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contacts_by_first_name(first_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-surname/{last_name}', response_model=list[ContactResponse])
async def get_contacts_by_last_name(last_name: str, db: AsyncSession = Depends(get_db),
                                    user: User = Depends(auth_service.get_current_user)):
    """
    The get_contacts_by_last_name function returns a list of contacts with the given last name.
        If no contact is found, it will return an empty list.

    :param last_name: str: Specify the last name of the contact to be retrieved
    :param db: AsyncSession: Pass the database connection to the function
    :param user: User: Get the current user from the auth_service
    :return: A list of contact objects
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contacts_by_last_name(last_name, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/by-email/{email}', response_model=ContactResponse)
async def get_contact_by_email(email: str, db: AsyncSession = Depends(get_db),
                               user: User = Depends(auth_service.get_current_user)):
    """
    The get_contact_by_email function is used to retrieve a contact by email.
        The function takes in an email and returns the contact with that email.

    :param email: str: Get the email from the request
    :param db: AsyncSession: Get the database session
    :param user: User: Check if the user is logged in
    :return: A contact object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.get_contact_by_email(email, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.get('/birthdays', response_model=list[ContactResponse])
async def get_contacts_by_upcoming_birthday(limit: int = Query(10, ge=10, le=500), offset: int = Query(0, ge=0),
                                            db: AsyncSession = Depends(get_db)):
    """
    The get_contacts_by_upcoming_birthday function returns a list of contacts with upcoming birthdays.
    The function takes in an optional limit and offset parameter, which are used to paginate the results.
    The default value for limit is 10, and the default value for offset is 0.

    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value of the limit parameter
    :param le: Limit the number of contacts returned to a maximum of 500
    :param offset: int: Specify the starting point of the query
    :param ge: Specify the minimum value of the parameter
    :param db: AsyncSession: Get the database session
    :return: A list of contacts with an upcoming birthday
    :doc-author: Trelent
    """
    contacts = await repositories_contacts.get_contacts_by_upcoming_birthday(limit, offset, db)
    if contacts is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contacts


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=2, seconds=5))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the repository
    :param user: User: Get the current user
    :return: A contactschema object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.create_contact(body, db, user)
    return contact


@router.put('/{contact_id}')
async def update_contact(body: ContactSchema, contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The update_contact function updates a contact in the database.
        It takes an id, body and db as parameters. The id is used to find the contact in the database,
        while body contains all of the information that will be updated for that specific contact.
        The db parameter is used to connect with our PostgreSQL database.

    :param body: ContactSchema: Validate the body of the request
    :param contact_id: int: Get the contact id from the url
    :param db: AsyncSession: Get the database session
    :param user: User: Get the current user from the auth_service
    :return: A contactschema object
    :doc-author: Trelent
    """
    contact = await repositories_contacts.update_contact(contact_id, body, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact


@router.delete('/{contact_id}')
async def delete_contact(contact_id: int = Path(ge=1), db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
    The delete_contact function deletes a contact from the database.
        The function takes in an integer representing the id of the contact to be deleted,
        and returns a dictionary containing information about that contact.

    :param contact_id: int: Specify the contact to be updated
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Get the current user from the auth_service
    :return: The deleted contact
    :doc-author: Trelent
    """
    contact = await repositories_contacts.delete_contact(contact_id, db, user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return contact
