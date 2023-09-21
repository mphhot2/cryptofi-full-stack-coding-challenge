from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="CryptoFi Full-Stack Coding Challenge",
)


@app.get("/")
def hello_world():
    """
    NOTE: This is route is used as an example for the test suite
    No action needed here
    """
    return {"hello": "world"}


@app.get("/prices_and_balances")
def get_prices_and_balances():
    """
    TODO
    Requirements:
    The GET route return the current prices for BTC, ETH and BCH and the user's balances for BTC, ETH and BCH.
    The prices should be ordered by the highest user balance to the lowest user balance, then alphabetically for all coins with no balance.
    """

    return {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
