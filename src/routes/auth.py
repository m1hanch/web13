from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth import auth_service
from src.services import email
from src.database.db import get_db

from src.repository import users as users_repo
from src.schemas.user import UserSchema, TokenSchema, UserResponse, RequestEmail

router = APIRouter(prefix='/auth', tags=['auth'])
get_refresh_token = HTTPBearer()


@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserSchema, bt: BackgroundTasks, request: Request, db: AsyncSession = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It takes in a UserSchema object, which is validated by pydantic.
        If the email already exists, it returns an HTTP 409 Conflict error.
        Otherwise, it hashes the password and creates a new user with that information.

    :param body: UserSchema: Validate the request body
    :param bt: BackgroundTasks: Add a task to the background tasks
    :param request: Request: Get the base url of the request
    :param db: AsyncSession: Pass the database connection to the function
    :return: A new user object
    :doc-author: Trelent
    """
    new_user = await users_repo.get_user_by_email(email=body.email, db=db)
    if new_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await users_repo.create_user(body=body, db=db)
    bt.add_task(email.send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post('/login', response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    It takes the username and password from the request body,
    and returns an access token and refresh token if successful.

    :param body: OAuth2PasswordRequestForm: Get the username and password from the request body
    :param db: AsyncSession: Get the database session
    :return: A dict with the access token and refresh token
    :doc-author: Trelent
    """
    user = await users_repo.get_user_by_email(email=body.username, db=db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email')
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid password')
    access_token = await auth_service.create_access_token(data={'sub': user.email})
    refresh_token = await auth_service.create_refresh_token(data={'sub': user.email})
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@router.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access token.
    It takes in a refresh token and returns a new access_token, refresh_token, and token type.


    :param credentials: HTTPAuthorizationCredentials: Get the token from the authorization header
    :param db: AsyncSession: Get the database connection
    :return: A new access token and refresh token
    :doc-author: Trelent
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await users_repo.get_user_by_email(email, db)
    if user.refresh_token != token:
        await users_repo.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    await db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    The confirmed_email function is used to confirm a user's email address.
        It takes the token from the URL and uses it to get the user's email address.
        Then, it checks if that user exists in our database, and if they do not exist,
        we raise an HTTPException with a 400 status code (Bad Request) and detail message of &quot;Verification error&quot;.

    :param token: str: Get the token from the url
    :param db: AsyncSession: Get the database session
    :return: A message that the email has been confirmed
    :doc-author: Trelent
    """
    email = await auth_service.get_email_from_token(token)
    user = await users_repo.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await users_repo.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: AsyncSession = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link that will allow them
    to confirm their email address. The function takes in a RequestEmail object, which contains the
    email of the user who wants to confirm their account. It then checks if there is already a confirmed
    user with that email address, and if so returns an error message saying as much. If not, it sends
    an email containing a confirmation link.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the request
    :param db: AsyncSession: Pass the database session to the function
    :return: A message that tells the user to check their email for confirmation
    :doc-author: Trelent
    """
    user = await users_repo.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(email.send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post('/password-recovery')
async def password_recovery(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                            db: AsyncSession = Depends(get_db)):
    """
    The password_recovery function is used to send an email to the user with a link that will allow them
    to reset their password. The function takes in a RequestEmail object, which contains the email of the user
    who wishes to reset their password. It then checks if there is a registered account associated with that
    email address and returns an error message if not. If there is, it generates a new random password for
    the account and sends an email containing instructions on how to change it.

    :param body: RequestEmail: Get the email from the request body
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the request
    :param db: AsyncSession: Get the database session
    :return: A message that the email was sent
    :doc-author: Trelent
    """
    user = await users_repo.get_user_by_email(body.email, db)
    if not user:
        return {"message": "email not registered"}
    # new_password = auth_service.generate_password()
    background_tasks.add_task(email.send_reset_password_email, user.email, str(request.base_url))
    await users_repo.update_password(user, auth_service.get_password_hash(new_password), db)
    return {"message": ""}
