# api/src/deps.py
import os
import json
from pathlib import Path
from typing import Dict, Tuple, List
from decimal import Decimal

import boto3
from botocore.exceptions import ClientError

from .models import CoinOut

# DynamoDB Local (docker maps to 8003)
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8003")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Dummy creds for local dynamodb/localstack
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_DEFAULT_REGION", REGION)

dynamodb = boto3.resource("dynamodb", endpoint_url=DDB_ENDPOINT, region_name=REGION)

# JSON lives in api/data/
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json_safely(filename: str, root_key: str) -> list:
    """Read {DATA_DIR/filename}[root_key]; return [] if missing/bad."""
    try:
        with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get(root_key, [])
    except FileNotFoundError:
        print(f"[seed] {filename} not found; skip seeding.")
    except Exception as e:
        print(f"[seed] Failed reading {filename}: {e}")
    return []


def ensure_tables_and_seed():
    """Create tables if missing and seed from JSON files once."""

    # prices
    try:
        table = dynamodb.create_table(
            TableName="prices",
            KeySchema=[{"AttributeName": "symbol", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "symbol", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        print("Created table: prices")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceInUseException":
            raise

    prices = dynamodb.Table("prices")
    if prices.scan().get("Count", 0) == 0:
        for row in _load_json_safely("prices.json", "prices"):
            prices.put_item(
                Item={
                    "symbol": row["coin"],
                    "name": row["name"],
                    "price": Decimal(str(row["price"])),
                }
            )
        print("Seeded prices from JSON")

    # balances
    try:
        table = dynamodb.create_table(
            TableName="balances",
            KeySchema=[{"AttributeName": "pk", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "pk", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        print("Created table: balances")
    except ClientError as e:
        if e.response["Error"]["Code"] != "ResourceInUseException":
            raise

    balances = dynamodb.Table("balances")
    if balances.scan().get("Count", 0) == 0:
        for ub in _load_json_safely("balances.json", "user_balances"):
            uid = ub["user_id"]
            for sym, amt in ub["balances"].items():
                balances.put_item(
                    Item={
                        "pk": f"user{uid}-{sym}",
                        "user_id": uid,
                        "symbol": sym,
                        "amount": Decimal(str(amt)),
                    }
                )
        print("Seeded balances from JSON")


def _table(name: str):
    return dynamodb.Table(name)


def load_prices() -> Dict[str, Tuple[str, float]]:
    """{SYM: (name, price)} from DynamoDB."""
    t = _table("prices")
    items: List[dict] = []
    resp = t.scan()
    items += resp.get("Items", [])
    while "LastEvaluatedKey" in resp:
        resp = t.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items += resp.get("Items", [])

    out: Dict[str, Tuple[str, float]] = {}
    for it in items:
        sym = str(it["symbol"]).upper()
        out[sym] = (it.get("name", sym), float(it.get("price", 0)))
    return out


def load_user_balances(user_id: str) -> Dict[str, float]:
    t = _table("balances")
    items: List[dict] = []
    resp = t.scan()
    items += resp.get("Items", [])
    while "LastEvaluatedKey" in resp:
        resp = t.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items += resp.get("Items", [])

    out: Dict[str, float] = {}
    for it in items:
        if str(it.get("user_id")) == str(user_id):
            out[str(it["symbol"]).upper()] = float(it.get("amount", 0))
    return out


def list_balances_for_user(user_id: str) -> List[CoinOut]:
    prices = load_prices()              # {SYM: (name, price)}
    amounts = load_user_balances(user_id)  # {SYM: amount}

    coins: List[CoinOut] = []
    for sym, (name, price) in prices.items():
        amt = float(amounts.get(sym, 0.0))
        coins.append(CoinOut(
            symbol=sym,
            name=name,
            price=price,
            amount=amt,
            value=amt * price,
        ))

    # - balances with >0 amount first, sorted by amount DESC
    # - if amounts tie, sort alphabetically by symbol
    # - balances with 0 amount last, alphabetically
    coins.sort(
        key=lambda c: (
            0 if c.amount > 0 else 1,
            -c.amount if c.amount > 0 else 0,
            c.symbol.upper()
        )
    )

    return coins
