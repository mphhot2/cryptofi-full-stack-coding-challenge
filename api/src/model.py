import os
from abc import abstractmethod
from dyntastic import Dyntastic
from pydantic import BaseModel, Field


class DynamoDbModelBase(Dyntastic):
    __table_region__ = os.environ.get("AWS_REGION")
    __table_host__ = os.environ.get("DYNAMO_ENDPOINT")
    __hash_key__ = "hash_key"

    @property
    @abstractmethod
    def __table_name__(self):  # over-ride this on each implementing class
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
