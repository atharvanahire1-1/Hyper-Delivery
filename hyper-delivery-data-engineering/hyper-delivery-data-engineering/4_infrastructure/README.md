
# Infrastructure

Status: Resources provisioned manually.

The project uses the following infrastructure:

- AWS S3 for raw event storage
- Kafka for event streaming
- Snowflake storage integration for S3 access
- Snowflake external stage and JSON file format
- Snowflake virtual warehouse

Infrastructure-as-Code deployment using Terraform or CloudFormation
has not yet been implemented.

No credentials or private keys should be stored in this directory.
