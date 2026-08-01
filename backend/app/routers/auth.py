from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, UserRole, TempleStaff
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserOut
from app.security import create_access_token, get_password_hash, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def role_value(role):
    if hasattr(role, "value"):
        return role.value
    return str(role)


def assigned_temples_for_user(user: User, db: Session) -> list[int]:
    if role_value(user.role) == UserRole.pilgrim.value:
        return []

    rows = db.query(TempleStaff).filter(TempleStaff.user_id == user.id).all()
    return [row.temple_id for row in rows]


def serialize_user(user: User, db: Session) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": role_value(user.role),
        "is_active": user.is_active,
        "assigned_temples": assigned_temples_for_user(user, db),
    }


def make_token_response(user: User, db: Session) -> dict:
    assigned_temples = assigned_temples_for_user(user, db)
    actual_role = role_value(user.role)

    token = create_access_token(
        user.id,
        {
            "role": actual_role,
            "assigned_temples": assigned_temples,
        },
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": serialize_user(user, db),
    }


def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        secret_key = getattr(settings, "SECRET_KEY", "digidarshan-dev-secret-key")
        algorithm = getattr(settings, "ALGORITHM", "HS256")

        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user


@router.post("/register", response_model=TokenResponse)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email.lower()).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    role = payload.role or UserRole.pilgrim

    user = User(
        name=payload.name,
        email=payload.email.lower(),
        phone=payload.phone,
        password_hash=get_password_hash(payload.password),
        role=role,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return make_token_response(user, db)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    email = payload.email.strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return make_token_response(user, db)


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user_from_token),
    db: Session = Depends(get_db),
):
    return serialize_user(current_user, db)