# api/src/deps.py
import os
from typing import Dict, Tuple, List
import boto3
from botocore.exceptions import ClientError
from .models import CoinOut
from decimal import Decimal

# Local DynamoDB endpoint; docker compose maps to 8003
DDB_ENDPOINT = os.getenv("DYNAMODB_ENDPOINT_URL", "http://localhost:8003")
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

# Localstack / DynamoDB local accepts any creds
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")
os.environ.setdefault("AWS_DEFAULT_REGION", REGION)

dynamodb = boto3.resource("dynamodb", endpoint_url=DDB_ENDPOINT, region_name=REGION)

def ensure_tables_and_seed():
    """Ensure prices and balances tables exist and seed them if empty."""

    # --- prices table ---
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
        prices.put_item(Item={"symbol": "BTC", "name": "Bitcoin", "price": Decimal("68000")})
        prices.put_item(Item={"symbol": "ETH", "name": "Ethereum", "price": Decimal("3400")})
        prices.put_item(Item={"symbol": "BCH", "name": "Bitcoin Cash", "price": Decimal("420")})
        prices.put_item(Item={"symbol": "LTC", "name": "Litecoin", "price": Decimal("85")})
        prices.put_item(Item={"symbol": "XLM", "name": "Stellar", "price": Decimal("0.12")})
        print("Seeded prices")

    # --- balances table ---
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
        balances.put_item(Item={"pk": "user1-BTC", "user_id": "1", "symbol": "BTC", "amount": Decimal("0.25")})
        balances.put_item(Item={"pk": "user1-ETH", "user_id": "1", "symbol": "ETH", "amount": Decimal("1.5")})
        balances.put_item(Item={"pk": "user2-BTC", "user_id": "2", "symbol": "BTC", "amount": Decimal("1")})
        balances.put_item(Item={"pk": "user2-ETH", "user_id": "2", "symbol": "ETH", "amount": Decimal("10")})
        print("Seeded balances")


def _table(name: str):
    return dynamodb.Table(name)  

def load_prices() -> Dict[str, Tuple[str, float]]:
    """
    Returns: { "BTC": ("Bitcoin", 68000.0), ... }
    Table: prices
    """
    t = _table("prices")
    items: List[dict] = []
    resp = t.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = t.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))

    out: Dict[str, Tuple[str, float]] = {}
    for it in items:
        sym = str(it["symbol"]).upper()
        out[sym] = (it.get("name", sym), float(it.get("price", 0)))
    return out

def load_user_balances(user_id: str) -> Dict[str, float]:
    """
    Returns: { "BTC": 0.25, "ETH": 1.5, ... }
    Table: balances
    """
    t = _table("balances")
    items: List[dict] = []
    resp = t.scan()
    items.extend(resp.get("Items", []))
    while "LastEvaluatedKey" in resp:
        resp = t.scan(ExclusiveStartKey=resp["LastEvaluatedKey"])
        items.extend(resp.get("Items", []))

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

    # ORDERING:
    #   - Group A: amount > 0 → sort by amount DESC, then symbol ASC
    #   - Group B: amount == 0 → sort by symbol ASC
    # We can do it in one pass with a tuple key:
    #   (is_zero, -amount_if_positive_else_0, symbol)
    coins.sort(key=lambda c: (c.amount <= 0, -(c.amount if c.amount > 0 else 0), c.symbol.upper()))
    return coins