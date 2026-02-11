# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth.verify_email import (
    EmailVerificationRequest,
    EmailVerificationResponse,
)
from app.services.auth.email_verification_service import EmailVerificationService

from app.schemas.auth.resend_verification import (
    ResendVerificationRequest,
    ResendVerificationResponse
)
from app.services.auth.resend_verification_service import ResendVerificationService

from app.schemas.auth.password_reset import (
    PasswordResetRequest,
    PasswordResetRequestResponse,
    PasswordResetConfirmRequest,
    PasswordResetConfirmResponse,
)
from app.services.auth.password_reset_service import PasswordResetService


from fastapi import status
from app.database.sessions import get_db
from app.schemas.auth.login import LoginRequest, LoginResponse
from app.services.auth.login_service import LoginService
from app.schemas.auth.register import RegisterRequest, RegisterResponse
from app.services.auth.registration_service import RegistrationService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    summary="Register a new user",
    status_code=status.HTTP_201_CREATED,
)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    service = RegistrationService(db)
    return service.register(data)



@router.post(
    "/verify-email",
    response_model=EmailVerificationResponse,
    summary="Confirm email address",
)

def verify_email(
    data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    service = EmailVerificationService(db)

    try:
        service.verify_email(data.token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return EmailVerificationResponse(
        message="Email successfully verified"
    )


@router.post(
    "/resend-verification",
    response_model=ResendVerificationResponse,
    summary="Resend email verification link",
)
def resend_verification(
    data: ResendVerificationRequest,
    db: Session = Depends(get_db),
):
    service = ResendVerificationService(db)

    try:
        service.resend(str(data.email))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ResendVerificationResponse(
        message="Verification email has been sent."
    )

# login
@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login and receive JWT token",
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    service = LoginService(db)
    try:
        return service.login(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


#password reset
@router.post(
    "/request-password-reset",
    response_model=PasswordResetRequestResponse,
    summary="Request password reset email",
)
def request_password_reset(
    data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    service = PasswordResetService(db)

    service.generate_reset_token(str(data.email))

    return PasswordResetRequestResponse(
        message="If this email exists — password reset instructions were sent."
    )

@router.post(
    "/reset-password",
    response_model=PasswordResetConfirmResponse,
    summary="Reset password using reset token",
)
def reset_password(
    data: PasswordResetConfirmRequest,
    db: Session = Depends(get_db),
):
    service = PasswordResetService(db)

    try:
        updated_at = service.reset_password(
            token=data.token,
            new_password=data.new_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return PasswordResetConfirmResponse(
        message="Password has been successfully updated. All sessions invalidated.",
        updated_at=updated_at,
    )
