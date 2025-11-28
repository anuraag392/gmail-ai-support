from fastapi import FastAPI
from auth.login import router as login_router
from auth.callback import router as callback_router

app = FastAPI()

# Register /auth/login and /auth/callback endpoints
app.include_router(login_router, prefix="/auth")
app.include_router(callback_router, prefix="/auth")
