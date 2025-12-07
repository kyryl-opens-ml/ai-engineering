from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.models.user import User
from api.config import get_settings

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    settings = get_settings()
    if not settings.supabase_jwt_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_JWT_SECRET not configured",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}"
        )

    supabase_id = payload.get("sub")
    email = payload.get("email")
    if not supabase_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = db.query(User).filter(User.supabase_id == supabase_id).first()
    if not user:
        user = User(supabase_id=supabase_id, email=email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
