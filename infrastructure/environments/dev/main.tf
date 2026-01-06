# add a dynamodb table named event-store with a partition key called PK and a sort key called SK
resource "aws_dynamodb_table" "event_store" {
    name         = "sh-event-store"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "PK"
    range_key    = "SK"

    attribute {
        name = "PK"
        type = "S"
    }

    attribute {
        name = "SK"
        type = "S"
    }

    tags = var.tags

    lifecycle {
        ignore_changes = [
        billing_mode,
        tags,
        ]
    }
}