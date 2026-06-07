from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import jwt

from app.core.database import get_db
from app.core.config import settings
from app.domain.models.user import User
from app.domain.schemas.user_schema import Token, UserResponse
from app.domain.constants import RoleEnum
from app.api.dependencies import get_current_user
from app.core.security import get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(hours=24))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/login")
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token = create_access_token(data={"sub": str(user.id)})
    
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,  
        secure=True,    
        samesite="lax",  
        max_age=24 * 60 * 60
    )
    return {"message": "Successfully logged in"}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logout successful"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):

    return current_user

@router.post("/seed-users")
def seed_users_endpoint(db: Session = Depends(get_db)):
    """Endpoint temporar pentru popularea bazei de date cu utilizatori."""
    if db.query(User).count() == 0:
        
        hashed_pw = get_password_hash("password")
        
        test_users = [
            User(email="angajat@test.com", hashed_password=hashed_pw, role=RoleEnum.REQUESTER),
            User(email="manager@test.com", hashed_password=hashed_pw, role=RoleEnum.MANAGER),
            User(email="it@test.com", hashed_password=hashed_pw, role=RoleEnum.IT_REP),
            User(email="finance@test.com", hashed_password=hashed_pw, role=RoleEnum.FINANCE),
        ]
        db.add_all(test_users)
        db.commit()
        return {"message": "Useri de test adaugati cu succes (cu parole hash-uite)!"}
        
    return {"message": "Baza de date contine deja useri."}
