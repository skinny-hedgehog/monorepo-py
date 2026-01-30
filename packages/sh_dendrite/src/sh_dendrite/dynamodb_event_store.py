import logging
from dataclasses import asdict
from datetime import datetime

import httpx
from aiodynamo.client import Client
from aiodynamo.credentials import Credentials
from aiodynamo.errors import ConditionalCheckFailed
from aiodynamo.expressions import F
from aiodynamo.http.httpx import HTTPX
from aiodynamo.operations import Put, Update
from opentelemetry import trace

from sh_dendrite.concurrency_violation_error import ConcurrencyViolationError
from sh_dendrite.event import Event
from sh_dendrite.event_store import EventStore

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)

LOG_METADATA_ITEM = "#LOG_METADATA"


class DynamodbEventStore(EventStore):
    def __init__(self, table_name: str, region: str, profile: str = 'default') -> None:
        self.table_name = table_name
        self.region = region
        self.profile = profile
        self._client = None
        self._httpx_client = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    async def _ensure_client(self):
        """Ensure the aiodynamo client is initialized"""
        if self._client is None:
            # Create httpx client for HTTP connections
            self._httpx_client = httpx.AsyncClient()

            # Get credentials from AWS profile
            # For now, we'll use the default credentials chain
            # aiodynamo will automatically use AWS credentials from environment/profile
            credentials = Credentials.auto()

            # Create the aiodynamo client
            self._client = Client(
                HTTPX(self._httpx_client),
                credentials,
                self.region
            )

    async def close(self):
        """Close the HTTP client"""
        if self._httpx_client:
            await self._httpx_client.aclose()
            self._httpx_client = None
            self._client = None

    async def apply(self, log_id: str, event: Event, last_event: str | None):
        await self._ensure_client()

        # Prepare event item
        event_item = {
            'PK': log_id,               # partition key
            'SK': event.event_id,       # sort key
            'event_type': f"{event.__class__.__module__}.{event.__class__.__name__}"   # fully qualified type name
        }

        # if event is a dataclass convert it to a dictionary
        if hasattr(event, '__dataclass_fields__'):
            event_dict = asdict(event)
            event_item.update(event_dict)

        # Convert datetime objects to ISO format strings
        event_item['applied_time'] = event_item['applied_time'].isoformat()
        event_item['created_time'] = event_item['created_time'].isoformat()

        logger.info(f"DynamoDB Item: {event_item}")

        # Build transaction items using aiodynamo's Put and Update classes
        try:
            if last_event is None:
                # First event - need to create both event and metadata
                await self._client.transact_write_items([
                    Put(
                        table=self.table_name,
                        item=event_item
                    ),
                    Put(
                        table=self.table_name,
                        item={
                            'PK': log_id,
                            'SK': LOG_METADATA_ITEM,
                            'last_event': event.event_id
                        }
                    )
                ])
            else:
                # Subsequent event - update metadata with condition check
                metadata_key = {'PK': log_id, 'SK': LOG_METADATA_ITEM}

                await self._client.transact_write_items([
                    Put(
                        table=self.table_name,
                        item=event_item
                    ),
                    Update(
                        table=self.table_name,
                        key=metadata_key,
                        expression=F("last_event").set(event.event_id),
                        condition=F("last_event").equals(last_event)
                    )
                ])
        except ConditionalCheckFailed as e:
            logger.warning(f"Transaction failed due to conditional check: {e}")
            raise ConcurrencyViolationError(
                message=f"could not update log metadata because the last applied event id does not match the client's event id {last_event}",
                code="ConditionalCheckFailed",
                reason=str(e),
            ) from e
        except Exception as e:
            logger.error(f"Failed to apply event: {e}")
            raise

    async def get_log(self, log_id: str):
        await self._ensure_client()

        table = self._client.table(self.table_name)
        events = []

        # Query all items with the given log_id
        with tracer.start_as_current_span("dynamodb.query"):
            async for item in table.query(key_condition=F("PK").equals(log_id)):
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

    async def get_log_from(self, log_id: str, from_timestamp: datetime):
        # Logic to retrieve logs from a specific timestamp in DynamoDB
        await self._ensure_client()

        # Not implemented yet
        pass
