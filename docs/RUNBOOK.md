# Runbook — from a fresh checkout to a validated batch

This runbook documents the manual workflow used for the AWS + Snowflake implementation. Resource creation is intentionally separated from daily runs: once the integration, bucket, connector, stage, tables, and topics exist, do not recreate them for every batch.

## A. One-time prerequisites

- Python installed (the walkthrough used Python 3.14 on Windows).
- Kafka cluster access and four existing topics.
- Kafka S3 Sink Connector configured and running with permissions to write to the target S3 bucket.
- Existing S3 bucket and topic prefixes.
- Existing Snowflake database, storage integration, stage, JSON file format, and Bronze/Silver/Gold schemas/tables.
- The SQL setup files in the project checkout.

## B. Python environment

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r .\1_data_generation\requirements.txt
```

Configure `1_data_generation/.env` with the seven variables listed in the root README. Use credentials from the Kafka provider, not values from screenshots or source control.

Quick dependency check:

```powershell
python -c "import dotenv, faker; from confluent_kafka import Producer; print('Python dependencies OK')"
```

## C. Publish events

```powershell
python .\1_data_generation\main.py --count 10
```

Expected producer summary for the demonstrated batch: 10 orders and 40 Kafka messages confirmed delivered. The producer flush result is a Kafka acknowledgement, not proof that S3 and Snowflake have completed their downstream work.

## D. Confirm S3 sink output

Check the four existing S3 prefixes:

```text
s3://hyper-delivery-data-20261012-k7m4/raw/quick_commerce_order_events/
s3://hyper-delivery-data-20261012-k7m4/raw/quick_commerce_delivery_events/
s3://hyper-delivery-data-20261012-k7m4/raw/quick_commerce_product_events/
s3://hyper-delivery-data-20261012-k7m4/raw/quick_commerce_rider_events/
```

S3 Sink Connector buffering/flush settings determine when new objects appear. Refresh the object listing and check timestamps. Do not expect one object per event.

## E. Snowflake stage check

Use the existing Snowflake worksheet and run:

```sql
LIST @HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE;
```

Then run the staged JSON record-count query in `VALIDATION.md`. Check that each event type has the expected records before loading Bronze.

## F. Load Bronze

Use the existing Bronze `COPY INTO` statements (from the current `2_snowflake/02_bronze` SQL file) and existing external stage/file format. Routine loads should not use `FORCE = TRUE`. Review copy results and load errors before proceeding.

After loading, verify the four Bronze table counts. The walkthrough reached 11 records in each table (44 total).

## G. Transform Silver

Run the existing Silver transformation or the project's incremental insert/deduplication statements. Verify the exact Silver table columns before executing any modified statement. Do not rerun the original setup file blindly if it contains plain `INSERT` statements.

The walkthrough's incremental update checked business keys and reached 11 records in each Silver table (44 total). Review query results for rejected/cast-failed values as well as row counts.

## H. Refresh Gold

Run the existing `2_snowflake/04_gold/setup_hyper_delivery_gold_layer.sql` script after confirming Silver is current. The script observed in the walkthrough uses `CREATE OR REPLACE TABLE` for its Gold aggregates. It rebuilds those tables from Silver; it does not refresh Bronze or Silver.

Verify the four Gold counts. The walkthrough returned 21 aggregate rows across the four Gold tables.

## I. Safe operational habits

- Never paste credentials, API secrets, private keys, or PEM contents into SQL worksheets or README files.
- Keep `.env`, private key files, and generated credential files out of Git.
- Do not rerun resource-creation scripts blindly in an established environment.
- Avoid `COPY INTO ... FORCE = TRUE` for normal incremental ingestion.
- Do not rerun non-idempotent Silver inserts without checking business-key duplicates.
- Inspect `CREATE OR REPLACE`, `TRUNCATE`, `DELETE`, and `DROP` statements before execution.
- Treat the current process as a manually orchestrated demo until a scheduler and failure handling are added.
