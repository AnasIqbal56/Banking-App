from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from auth import get_current_user
from routes import auth, accounts, transactions, bills


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await init_db()
    yield


app = FastAPI(
    title="Banking App API",
    description="A minimalistic banking application API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","https://banking-app-plum.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(bills.router)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Banking App API is running", "status": "healthy"}


@app.get("/api/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current logged in user info"""
    return current_user


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
