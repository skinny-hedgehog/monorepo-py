# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Repository Overview

This is a Python monorepo using **uv** as the package manager and workspace tool. It contains:
- `packages/sh_dendrite`: A lightweight event-sourcing framework library
- `packages/api`: A FastAPI application that uses sh_dendrite for event-sourced ledgers
- `infrastructure/`: Terraform IaC for AWS resources (DynamoDB event store)

## Architecture

### sh_dendrite Framework
Event-sourcing framework with these core concepts:
- **Event**: Base class for domain events with `event_type` and `event_name` properties
- **Aggregate**: Base class for event-sourced aggregates, handles `on()` for replaying events and `apply()` for persisting new events
- **EventStore**: Abstract interface with `apply()`, `get_log()`, and `get_log_from()` methods. Implementations: `DynamodbEventStore`, `InMemoryEventStore`
- **AggregateFactory**: Creates new aggregates or loads existing ones by replaying events from the store
- **EventHandler**: Interface for side effects (e.g., updating read models)

### API Application
Event-sourced ledger system with CQRS pattern:
- **Domain**: `Ledger` aggregate with commands (CreateLedger, CreditLedger, DebitLedger) and corresponding events
- **Read Model**: `LedgerReadModel` maintains PostgreSQL projections of ledger state
- **Event Flow**: Command → Aggregate → EventStore (DynamoDB) → EventHandler → Read Model (PostgreSQL)

Event handlers are registered in `main.py` via the `AggregateFactory` constructor, mapping event types to handler lists. When `apply()` is called on an aggregate, events are persisted to DynamoDB then dispatched to all registered handlers.

## Development Commands

### Environment Setup
```bash
# Install dependencies and sync workspace
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Running the API
```bash
# Run FastAPI dev server (from packages/api/)
cd packages/api
fastapi dev main.py

# With OpenTelemetry dashboard (run first):
docker run --rm -it \
  -p 18888:18888 \
  -p 4317:18889 \
  --name aspire-dashboard \
  mcr.microsoft.com/dotnet/aspire-dashboard:latest
```

### Testing
```bash
# Run all tests from repository root
pytest packages/

# Run tests for specific package
pytest packages/sh_dendrite/
pytest packages/api/

# Run single test file
pytest packages/api/tests/setup_account/test_create_account_new.py
```

Test configuration:
- API tests use `conftest.py` to add `src/` to Python path
- Tests import from domain modules via the modified path
- Use `SingleLogEventStore` for testing event-sourced aggregates without external dependencies

### Infrastructure
```bash
# Terraform is in infrastructure/environments/dev/
cd infrastructure/environments/dev
terraform init
terraform plan
terraform apply
```

## Environment Configuration

API requires `.env` file in `packages/api/`:
```
EVENT_STORE_TABLE_NAME=sh-event-store
AWS_REGION=us-east-1
AWS_PROFILE=sh_dev
RM_DB_NAME=postgres
RM_DB_USER=skinny_hedgehog_pg_rms
RM_DB_PASSWORD=<password>
RM_DB_HOST=localhost
```

## Workspace Structure

This is a **uv workspace** defined in root `pyproject.toml`. Workspace members:
- `packages/sh_dendrite`: Framework library (can be built and distributed)
- `packages/api`: Application package (depends on sh_dendrite via `workspace = true`)

When adding dependencies:
```bash
# Add to specific package
cd packages/api
uv add <package>

# Add dev dependencies
uv add --dev <package>
```

## Coding Patterns

### Creating Event-Sourced Aggregates
1. Define command dataclasses
2. Define event dataclasses inheriting from `Event`
3. Create aggregate inheriting from `Aggregate` with:
   - `on(event)` method for state mutations (used during replay)
   - Command handler methods that create events and call `self.apply(event)`
4. Register event handlers in `main.py` when constructing `AggregateFactory`

### Testing Event-Sourced Aggregates
Use `SingleLogEventStore` from `tests.single_log_event_store` for isolated testing without external dependencies. See `test_create_account_new.py` for example pattern.

### OpenTelemetry
The framework includes manual instrumentation with spans in `Aggregate.apply()` and `AggregateFactory.load()`. FastAPI uses auto-instrumentation via the `fastapi[standard]` dependency.
