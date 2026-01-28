### Create a ledger

```bash
uv run --env-file .env \
  python main.py create_ledger
```

### Update a ledger

```bash
uv run --env-file .env \
  python main.py update_ledger 13608973-2467-49d8-a44a-322ab1f37950 1
```
Argments:
1. ID of the ledger to update - the harness will simply credit ConcurrentLedger by 1
2. Seconds to sleep between loading the aggregate from the event log and applying a credit event

### To run with OpenTelemetry

```bash
uv run --env-file .env \
  opentelemetry-instrument \
  python main.py update_ledger 13608973-2467-49d8-a44a-322ab1f37950 1
```