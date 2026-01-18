import logging
import os

import psycopg
from fastapi import FastAPI

from domain.ledger import LedgerReadModel, LedgerCreatedEvent, LedgerCreditedEvent, LedgerDebitEvent
from routes.account import AccountRouter
from routes.ledger import LedgerRouter
from sh_dendrite.aggregate import uuid_log_id_generator
from sh_dendrite.aggregate_factory import AggregateFactory
from sh_dendrite.dynamodb_event_store import DynamodbEventStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

event_store = DynamodbEventStore(
    table_name=os.getenv('EVENT_STORE_TABLE_NAME'),
    region=os.getenv('AWS_REGION'),
    profile=os.getenv('AWS_PROFILE')
)

conn = psycopg.connect(
        dbname=os.getenv('RM_DB_NAME'),
        user=os.getenv('RM_DB_USER'),
        password=os.getenv('RM_DB_PASSWORD'),
        host=os.getenv('RM_DB_HOST')
    )

ledger_read_model = LedgerReadModel(conn)

aggregate_factory = AggregateFactory(
    event_store = event_store,
    log_id_generator = uuid_log_id_generator,
    event_handlers = {
        LedgerCreatedEvent: [ledger_read_model],
        LedgerCreditedEvent: [ledger_read_model],
        LedgerDebitEvent: [ledger_read_model]
    }
)

logger.info("Initialized AggregateFactory with DynamoDB Event Store and Ledger Read Model")

account_router = AccountRouter(aggregate_factory)
ledger_router = LedgerRouter(aggregate_factory)

app = FastAPI()

app.include_router(account_router.get_router())
app.include_router(ledger_router.get_router())