from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel as PydanticBaseModel

from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.schemas.user import UserUpdate
from app.services.auth_service import (
    create_user,
    authenticate_user,
    create_access_token,
    get_user_by_email,
    get_user_by_id,
    decode_token
)
from app.config import get_settings
from app.models import User

router = APIRouter()
security = HTTPBearer()
settings = get_settings()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user = create_user(db, user_data)
    
    # Generate verification token and send email
    from app.services.email_verification import generate_verification_token, send_verification_email
    token = generate_verification_token()
    user.verification_token = token
    user.email_verified = False
    db.commit()
    
    email_sent = send_verification_email(user.email, user.full_name, token)
    
    if not email_sent:
        # If SMTP not configured, auto-verify (dev/fallback mode)
        user.email_verified = True
        user.verification_token = None
        db.commit()
    
    if not user.email_verified:
        # Don't log them in — require verification first
        return {
            "message": "Please check your email to verify your account.",
            "email": user.email,
            "requires_verification": True,
        }
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/verify")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify a user's email address via token."""
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired verification link")
    
    user.email_verified = True
    user.verification_token = None
    db.commit()
    
    return {"message": "Email verified successfully", "email": user.email}


@router.post("/resend-verification")
async def resend_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resend verification email (for logged-in users)."""
    if current_user.email_verified:
        return {"message": "Email already verified"}
    
    from app.services.email_verification import generate_verification_token, send_verification_email
    token = generate_verification_token()
    current_user.verification_token = token
    db.commit()
    
    sent = send_verification_email(current_user.email, current_user.full_name, token)
    if not sent:
        raise HTTPException(status_code=500, detail="Failed to send verification email. Please try again later.")
    
    return {"message": "Verification email sent"}


class ResendRequest(PydanticBaseModel):
    email: str

@router.post("/resend-verification-public")
async def resend_verification_public(
    request: ResendRequest,
    db: Session = Depends(get_db)
):
    """Resend verification email by email address (no auth required)."""
    user = get_user_by_email(db, request.email)
    if not user or getattr(user, 'email_verified', True):
        # Don't reveal whether the email exists
        return {"message": "If that email is registered, a verification link has been sent."}
    
    from app.services.email_verification import generate_verification_token, send_verification_email
    token = generate_verification_token()
    user.verification_token = token
    db.commit()
    
    send_verification_email(user.email, user.full_name, token)
    return {"message": "If that email is registered, a verification link has been sent."}


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not getattr(user, 'email_verified', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "email_not_verified",
                "message": "Please verify your email before logging in. Check your inbox for a verification link.",
                "email": user.email,
            }
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    for field, value in update_data.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


@router.get("/me/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current plan usage and limits."""
    from app.services.plan_limits import get_usage_summary
    return get_usage_summary(current_user, db)
