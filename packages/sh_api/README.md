# Incentivize Backend

# Running With Telemetry
We'll use the Microsoft Aspire dashboard to collect and visualize OpenTelemetry data. To run the Aspire server, run 
the following Docker command:

```bash
docker run --rm -it \
  -p 18888:18888 \
  -p 4317:18889 \
  --name aspire-dashboard \
  mcr.microsoft.com/dotnet/aspire-dashboard:latest
``` 

Then run the web server normally. The API already uses the FastAPI OpenTelementry auto-instrumentation library and the 
relevant `fx` classes have manually-instrumented spans.

## Stress Test URLs
* 10 events: `curl http://localhost:8000/ledger/8fe0a2b4-c9ae-4a41-9524-2ee521b2af27`
* 100 events: `curl http://localhost:8000/ledger/99_df40e446-a795-443a-b578-b1b3e19f1010`
* 1,000 events: `curl http://localhost:8000/ledger/999_2c687afd-7119-4499-815b-20d2f506ab49`
* 10,000 events: `curl http://localhost:8000/ledger/9999_232259f1-26d5-4a70-bf1b-5a8ef06de99f`
* 100,000 events: `curl http://localhost:8000/ledger/99999_2ceb29d1-1564-4966-855f-8a99d450f543`

## Credits and Debits
Posting a credit to update the event store and an externalized read model
```curl -X POST -H "Content-Type: application/json" -d '{"amount":34.0}' http://localhost:8000/ledger/bb796ae8-ea33-416d-aaac-5e707abdb7fb/credits```

Posting a debit to update the event store and an externalized read model
```curl -X POST -H "Content-Type: application/json" -d '{"amount":18.5}' http://localhost:8000/ledger/bb796ae8-ea33-416d-aaac-5e707abdb7fb/debits```

## TODO
- [x] Create DynamoDB table for the event store
- [x] Save an applied event to the Dyanmodb event store
- [x] Fetch a log from Dynamodb
- [x] Rehydrate an aggregate from the event store
- [x] Add OpenTelemetry support and monitor using Aspire 
- [x] Ensure that we can measure the time to hydrate an aggregate given a number of different event sizes (10, 100, 
1,000, 10,000, 100,000). Based on an assumption of 100 ms for an HTTPS connection, we should try to stay under 200 ms.
- [x] Create mechanism for creating, registering, and invoking event handlers
- [x] Create an event handler that updates a sql based read model
- [ ] Create an event handler to update a TODO list read model (based on SQS)
- [ ] Create tooling/pattern to either rehydrate or bootstrap a read model
- [ ] add error handling and logging - figure out a better way to work with Open Telemetry
- [ ] see whether there's a better way to split out the fx into a different package and leverage UV's workspace ability