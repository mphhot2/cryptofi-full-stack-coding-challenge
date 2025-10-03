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

@app.get("/users/{user_id}/balances", response_model=List[CoinOut])
def get_user_balances(user_id: str):
    """
    Returns ordered prices+balances for the given user.

    Ordering requirement:
      The balances should be ordered by the most amount of holdings a user has,
      for all the coins that the user holds, then alphabetically.
    """
    return list_balances_for_user(user_id)
