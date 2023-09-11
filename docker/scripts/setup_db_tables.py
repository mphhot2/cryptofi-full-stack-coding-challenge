import json

from src.model import Prices, Balances
from botocore.exceptions import ClientError


class DbSetup:
    def run(self):
        self._create_pricees_table()
        self._create_balances_table()
        self._fill_prices_table()
        self._fill_balances_table()

    def _create_pricees_table(self):
        try:
            Prices.create_table()
        except ClientError:
            print("Price table already exists")
            # Delete all records
            prices = Prices.scan()
            for price in prices:
                price.delete()

    def _create_balances_table(self):
        try:
            Balances.create_table()
        except ClientError:
            print("Balances table already exists")
            # Delete all records
            balances = Balances.scan()
            for balance in balances:
                balance.delete()

    def _fill_prices_table(self):
        with open("data/prices.json", "r") as f:
            prices = json.load(f)

        for price in prices.get("prices"):
            price_record = Prices(
                coin=price.get("coin"),
                # range_key=f"COIN#{price.get('coin')}",
                price=price.get("price"),
                name=price.get("name"),
            )
            price_record.save()

    def _fill_balances_table(self):
        with open("data/balances.json", "r") as f:
            balances = json.load(f)

        for balance in balances.get("user_balances"):
            balance_record = Balances(
                user_id=balance.get("user_id"),
                # range_key=f"BALANCE#{balance.get('user_id')}",
                balances=balance.get("balances"),
            )
            balance_record.save()


if __name__ == "__main__":
    db_setup = DbSetup()
    db_setup.run()
