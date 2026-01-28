import logging
from dataclasses import asdict
from datetime import datetime

import boto3
from boto3.dynamodb.types import TypeSerializer
from botocore.exceptions import ClientError
from opentelemetry import trace

from sh_dendrite.concurrency_violoation_error import ConcurrencyViolationError
from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

LOG_METADATA_ITEM = "#LOG_METADATA"


class DynamodbEventStore(EventStore):
    def __init__(self, table_name: str, region: str, profile: str = 'default') -> None:
        session = boto3.Session(profile_name=profile)
        # TODO don't keep both high and low level clients
        self.dynamodb_high_level = session.resource('dynamodb', region_name=region)
        self.dynamodb_low_level = session.client('dynamodb', region_name=region)
        self.table = self.dynamodb_high_level.Table(table_name)
        self.serializer = TypeSerializer()

    def apply(self, log_id: str, event: Event, last_event: str | None):
        event_item = {
            'PK': log_id,               # partition key
            'SK': event.event_id,       # sort key
            'event_type': f"{event.__class__.__module__}.{event.__class__.__name__}"   # fully qualified type name
        }

        # if event is a dataclass convert it to a dictionary
        if hasattr(event, '__dataclass_fields__'):
            event_dict =  asdict(event)
            event_item.update(event_dict)

        event_item['applied_time'] = event_item['applied_time'].isoformat()
        event_item['created_time'] = event_item['created_time'].isoformat()

        logger.info(f"DynamoDB Item: {event_item}")

        transact_items = []

        transact_items.append({
            'Put': {
                'TableName': self.table.name,
                'Item': {k: self.serializer.serialize(v) for k, v in event_item.items()}
            }
        })

        if last_event is None:
            transact_items.append({
                'Put': {
                    'TableName': self.table.name,
                    'Item': {
                        'PK': self.serializer.serialize(log_id),
                        'SK': self.serializer.serialize(LOG_METADATA_ITEM),
                        'last_event': self.serializer.serialize(event.event_id)
                    }
                }
            })
        else:
            transact_items.append({
                'Update': {
                    'TableName': self.table.name,
                    'Key': {
                        'PK': self.serializer.serialize(log_id),
                        'SK': self.serializer.serialize(LOG_METADATA_ITEM),
                    },
                    'UpdateExpression': 'SET last_event = :event_name',
                    'ConditionExpression': 'last_event = :last_event',
                    'ExpressionAttributeValues': {
                        ':last_event': self.serializer.serialize(last_event),
                        ':event_name': self.serializer.serialize(event.event_id)
                    }
                }
            })


        logger.info(f"DynamoDB Transaction Items: {transact_items}")

        try:
            self.dynamodb_low_level.transact_write_items(TransactItems=transact_items)
        except ClientError as e:
            if e.response["Error"]["Code"] == "TransactionCanceledException":
                cancellation_reasons = e.response.get("CancellationReasons", [])
                logger.warning(f"Transaction failed. Cancellation reasons: {cancellation_reasons}")

                for reason in cancellation_reasons:
                    if reason.get("Code") == "ConditionalCheckFailed":
                        raise ConcurrencyViolationError(
                            message=f"could not update log metadata because the last applied event id does not match the client's event id {last_event}",
                            code=reason.get("Code"),
                            reason=reason.get("Message"),
                        ) from e
            raise


    def get_log(self, log_id: str):
        # Initialize variables for pagination
        all_items = []
        last_evaluated_key = None

        while True:
            with tracer.start_as_current_span("dynamodb.query_page"):
                if last_evaluated_key:
                    response = self.table.query(
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(log_id),
                        ExclusiveStartKey=last_evaluated_key
                    )
                else:
                    response = self.table.query(
                        KeyConditionExpression=boto3.dynamodb.conditions.Key('PK').eq(log_id)
                    )

                items = response.get('Items', [])
                all_items.extend(items)

                last_evaluated_key = response.get('LastEvaluatedKey')
                if not last_evaluated_key:
                    break

        events = []

        for item in all_items:
            sk = item.get('SK')
            logger.info(f"get_log: item with SK: {sk}")
            if sk == LOG_METADATA_ITEM:
                continue  # skip metadata item
            event_type = item.get('event_type')

            # get all non-control attributes
            event_data = {k: v for k, v in item.items() if k not in ['PK', 'SK', 'event_type', 'created_time', 'applied_time', 'event_id']}

            # Reconstruct the Event object based on the event_type
            event_class = Event.class_from(event_type)
            if event_class:
                event = event_class(**event_data)
                event.event_id = item['event_id']
                event.created_time = datetime.fromisoformat(item['created_time'])
                event.applied_time = datetime.fromisoformat(item['applied_time'])
                events.append(event)
        return events

    def get_log_from(self, log_id: str, from_timestamp: datetime):
        # Logic to retrieve logs from a specific timestamp in DynamoDB
        pass