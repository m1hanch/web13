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
    new_user = await users_repo.get_user_by_email(email=body.email, db=db)
    if new_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Account already exists')
    body.password = auth_service.get_password_hash(body.password)
    new_user = await users_repo.create_user(body=body, db=db)
    bt.add_task(email.send_email, new_user.email, new_user.username, str(request.base_url))
    return new_user


@router.post('/login', response_model=TokenSchema)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
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
    user = await users_repo.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(email.send_email, user.email, user.username, str(request.base_url))
    return {"message": "Check your email for confirmation."}

@router.post('/password-recovery')
async def password_recovery(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                            db: AsyncSession = Depends(get_db)):
    user = await users_repo.get_user_by_email(body.email, db)
    if not user:
        return {"message": "email not registered"}
    #new_password = auth_service.generate_password()
    background_tasks.add_task(email.send_reset_password_email, user.email, str(request.base_url))
    await users_repo.update_password(user, auth_service.get_password_hash(new_password), db)
    return {"message": ""}