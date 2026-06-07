from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token_payload
from app.domain.models import User

# Extrage tokenul din Cookie
def get_token_from_cookie(request: Request) -> str:
    authorization = request.cookies.get("access_token")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return authorization.split(" ")[1]

def get_current_user(
    token: str = Depends(get_token_from_cookie),
    db: Session = Depends(get_db)
) -> User:
    
    user_id_str = verify_token_payload(token)
    user = db.query(User).filter(User.id == int(user_id_str)).first()
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
        
    return user