import os
from abc import abstractmethod
from dyntastic import Dyntastic
from pydantic import BaseModel, Field
from typing import Optional

class DynamoDbModelBase(Dyntastic):
    __table_region__ = os.environ.get("AWS_REGION")
    __table_host__ = os.environ.get("DYNAMO_ENDPOINT")
    __hash_key__ = "hash_key"

    @property
    @abstractmethod
    def __table_name__(self):  # over-ride this
        pass

    hash_key: str = Field(default=None, title="DynamoDB Partition Key")


class Prices(DynamoDbModelBase):
    __table_name__ = "prices"
    __hash_key__ = "coin"

    coin: str = Field(
        default=None,
        title="The abbreviation of the coin, i.e. BTC. This is the DynamoDB Partition Key",
    )
    price: str = Field(default=None, title="The price of the coin.")
    name: str = Field(default=None, title="The name of the coin.")


class Balances(DynamoDbModelBase):
    __table_name__ = "balances"
    __hash_key__ = "user_id"

    user_id: str = Field(
        default=None, title="The user's ID. This is the DynamoDB Partition Key"
    )
    balances: dict = Field(default=None, title="The user's balances.")

class Price(Dyntastic):
    __hash_key__ = "symbol"
    __table_name__ = "prices"
    symbol: str  # e.g., "BTC"
    name: str    # e.g., "Bitcoin"
    price: float # USD

class Balance(Dyntastic):
    __hash_key__ = "pk"
    __table_name__ = "balances"
    pk: str       # f"user#{user_id}#symbol#{symbol}"
    user_id: str
    symbol: str
    amount: float   

class CoinOut(BaseModel):
    symbol: str
    name: str
    price: float
    amount: float
    value: float