from fastapi import APIRouter, Depends, File, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import Token, UserCreate, UserResponse
from models import User
from utils import verify
from oauth2 import create_access_token

router = APIRouter(
    prefix = "/users",
    tags=['Users'],
)

@router.post('/login', response_model=Token)
async def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)): 
   
    user = db.query(User).filter(User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")

    if not verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")

    access_token = create_access_token(data = {"user_id": user.id})

    return {"access_token": access_token, 
            "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def createUser(user: UserCreate, db: AsyncSession = Depends(get_db)):

    hashed_password = hash(user.password)
    user.password = hashed_password

    new_user = User(**user.dict())

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=UserResponse)
def getUser(id: int, db: AsyncSession = Depends(get_db)):

    user = db.query(User).filter(User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with {id} is not found")

    return user