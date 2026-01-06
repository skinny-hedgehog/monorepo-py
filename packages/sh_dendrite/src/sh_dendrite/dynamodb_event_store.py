from dataclasses import asdict
from sh_dendrite.event import Event
from datetime import datetime
import boto3
from sh_dendrite.event_store import EventStore
from opentelemetry import trace
import logging

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

class DynamodbEventStore(EventStore):
    def __init__(self, table_name: str, region: str, profile: str = 'default') -> None:
        session = boto3.Session(profile_name=profile)
        self.dynamodb = session.resource('dynamodb', region_name=region)
        self.table = self.dynamodb.Table(table_name)

    # TODO: extend apply to enable putting a series of events in a single call
    def apply(self, log_id: str, event: Event):
        item = {
            'PK': log_id,  # partition key
            'SK': event.event_name,  # sort key
            'event_type': f"{event.__class__.__module__}.{event.__class__.__name__}",   # fully qualified type name
        }

        # if event is a dataclass convert it to a dictionary
        if hasattr(event, '__dataclass_fields__'):
            event_dict = asdict(event)
            item.update(event_dict)

        logger.info(f"DynamoDB Item: {item}")

        self.table.put_item(Item=item)

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
            event_type = item.get('event_type')
            event_data = {k: v for k, v in item.items() if k not in ['PK', 'SK', 'event_type']}
            # Reconstruct the Event object based on the event_type
            event_class = Event.class_from(event_type)
            if event_class:
                event = event_class(**event_data)
                events.append(event)
        return events

    def get_log_from(self, log_id: str, from_timestamp: datetime):
        # Logic to retrieve logs from a specific timestamp in DynamoDB
        pass