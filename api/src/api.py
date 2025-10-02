from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import CoinOut
from .deps import list_balances_for_user, ensure_tables_and_seed

app = FastAPI(title="CryptoFi Full-Stack Coding Challenge")

# Allow CRA on :3000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Create/seed DynamoDB tables on boot (idempotent)."""
    ensure_tables_and_seed()

@app.get("/")
def hello_world():
    return {"hello": "world"}

@app.get("/users/{user_id}/balances", response_model=List[CoinOut])
def get_user_balances(user_id: str):
    """
    Returns ordered prices+balances for the given user.

    Ordering requirement:
      1) All coins the user HOLDS (> 0) ordered by amount DESC
      2) Then all coins with ZERO balance ordered alphabetically by symbol
    """
    return list_balances_for_user(user_id)
