import uuid
from datetime import datetime, timedelta
import boto3
from typing import List, Dict
import os

records_to_generate = 99999
table_name = os.getenv('EVENT_STORE_TABLE_NAME')
region = os.getenv('AWS_REGION')
profile = os.getenv('AWS_PROFILE')

def chunk_items(items: List[Dict], chunk_size: int = 25):
    """Split items into chunks of specified size"""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

session = boto3.Session(profile_name=profile, region_name=region)
dynamodb = session.client('dynamodb')

# Generate a single UUID for all records
log_id = f"{records_to_generate}_{str(uuid.uuid4())}"
base_time = datetime.now()

# Generate all items first
all_items = [
    {
        "PutRequest": {
            "Item": {
                "PK": {"S": log_id},
                "SK": {"S": f"{base_time.strftime('%Y%m%d%H%M%S%f')}_LedgerCreated"},
                "event_type": {"S": "src.domain.ledger.LedgerCreatedEvent"},
                "initial_balance": {"N": "0.0"}
            }
        }
    }
] + [
    {
        "PutRequest": {
            "Item": {
                "PK": {"S": log_id},
                "SK": {"S": f"{(base_time + timedelta(seconds=i+1)).strftime('%Y%m%d%H%M%S%f')}_LedgerCredited"},
                "event_type": {"S": "src.domain.ledger.LedgerCreditedEvent"},
                "amount": {"N": "1.0"}
            }
        }
    } for i in range(records_to_generate)
]

# Process in batches of 25
for batch in chunk_items(all_items):
    response = dynamodb.batch_write_item(
        RequestItems={
            "sh-event-store": batch
        }
    )
    print(f"Processed batch of {len(batch)} items")

print(f"Generated events with UUID: {log_id}")