from fastapi import APIRouter

from .signup import router as signup_router
from .login import router as login_router
from .forgot_password import router as forgot_password_router
from .reset_password import router as reset_password_router
from .token import router as token_router

router = APIRouter()

router.include_router(signup_router, tags=["Auth"])
router.include_router(login_router, tags=["Auth"])
router.include_router(forgot_password_router, tags=["Auth"])
router.include_router(reset_password_router, tags=["Auth"])
router.include_router(token_router, tags=["Auth"])