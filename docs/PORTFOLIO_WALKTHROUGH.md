# Portfolio walkthrough — how to present the project

## 60–90 second explanation

“I built a streaming data engineering pipeline for a simulated quick-commerce delivery business. A Python application uses Faker to generate related order, delivery, product, and rider events. The events are published to four Confluent Kafka topics, then a Kafka S3 Sink Connector lands JSON files in Amazon S3. Snowflake reads the files through an external stage and processes them through a medallion-style Bronze, Silver, and Gold design. Bronze retains raw payloads and file lineage, Silver extracts typed event fields and handles deduplication, and Gold exposes business aggregates for order status, product popularity, rider status, and delivery performance. I validated the path with a 10-order test batch: 40 Kafka messages were acknowledged, 44 records were visible in the staged files and in each warehouse layer, and the Gold layer returned 21 aggregate rows.”

## Suggested demo order

1. Show `1_data_generation/` and explain the four event generators.
2. Show `main.py` and the Kafka producer; point to the 40/40 delivery confirmation from the test run.
3. Show the four raw prefixes under the S3 bucket and a partitioned JSON object.
4. In Snowflake, show the external stage and the query that counted 11 records per topic.
5. Show Bronze table counts and the metadata/lineage columns.
6. Show Silver table counts and explain typed transformations and business-key deduplication.
7. Show the four Gold tables and sample aggregates.
8. Close with current limitations and next steps: automate orchestration, add data-quality tests, monitoring, and optional BI.

## Questions you should be ready to answer

**Why Kafka and S3?** Kafka decouples event generation from storage/processing, while S3 provides durable, inexpensive raw-object storage and a replayable landing zone.

**Why Bronze, Silver, and Gold?** Bronze preserves raw source payloads and lineage; Silver provides cleaned, typed, queryable event records; Gold presents business-level aggregations.

**Why keep file metadata in Bronze?** It supports source traceability, load troubleshooting, and identifying which S3 object/row produced a warehouse record.

**Why are there 22 files but 44 records?** The sink writes records in batches by topic/partition and time partition. An S3 object can contain multiple records, so object count and record count are different measures.

**Is the pipeline fully automated?** The Python-to-Kafka and Kafka-to-S3 path was exercised, but Snowflake loading and transformations were manually initiated in worksheets. Scheduled orchestration is a future improvement, not a claimed feature.

**Why no Power BI?** It was deliberately skipped in this validated build. The project currently demonstrates ingestion and warehouse modelling through the Gold layer.

## Resume bullet

Built a quick-commerce streaming data pipeline using Python/Faker, Confluent Kafka, Amazon S3, and Snowflake; generated and published 40 test events across four topics, landed partitioned JSON files in S3, and validated 44 records through Bronze/Silver and 21 Gold aggregate rows.
