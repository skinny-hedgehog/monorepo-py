import argparse
import logging
import os
import time
from decimal import Decimal

from concurrency_ledger import ConcurrencyLedger
from sh_dendrite.aggregate import uuid_log_id_generator
from sh_dendrite.aggregate_factory import AggregateFactory
from sh_dendrite.dynamodb_event_store import DynamodbEventStore

logging.basicConfig(level=logging.INFO)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('boto3').setLevel(logging.WARNING)


factory = AggregateFactory(
    DynamodbEventStore(os.getenv('EVENT_STORE_TABLE_NAME'), os.getenv('AWS_REGION'), os.getenv('AWS_PROFILE')),
    uuid_log_id_generator,{})

active_ledger: ConcurrencyLedger | None = None

def create_ledger():
    print("Creating ledger...")
    global active_ledger
    active_ledger = factory.new(ConcurrencyLedger)
    active_ledger.create_ledger(Decimal(0.0))
    print(f"Active ledger: {active_ledger.log_id} created with initial balance of {active_ledger.balance}")


def update_ledger(ledger_name: str, sleep_time: float = 0.0):
    global active_ledger

    active_ledger = factory.load(ConcurrencyLedger, ledger_name)
    print(f"Active ledger: {active_ledger.log_id} fetched with balance of {active_ledger.balance}")

    if sleep_time > 0:
        print(f"Sleeping for {sleep_time} seconds...")
        time.sleep(sleep_time)

    print(f"Updating ledger: {ledger_name}")
    active_ledger.update_ledger(Decimal(1.0))

    print(f"Active ledger: {active_ledger.log_id} updated with balance of {active_ledger.balance}")


def main():
    parser = argparse.ArgumentParser(description="Concurrency Test Harness CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # create_ledger command
    subparsers.add_parser("create_ledger", help="Create a new ledger")

    # update_ledger command
    update_parser = subparsers.add_parser("update_ledger", help="Update a ledger by name with specified sleep time")
    update_parser.add_argument("ledger_name", type=str, help="Name of the ledger")
    update_parser.add_argument("sleep_time", type=float, help="Time in seconds to sleep between each update")

    args = parser.parse_args()

    match args.command:
        case "create_ledger":
            create_ledger()
        case "update_ledger":
            update_ledger(args.ledger_name, args.sleep_time)


if __name__ == "__main__":
    main()
