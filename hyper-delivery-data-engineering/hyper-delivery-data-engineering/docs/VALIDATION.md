# Validation and test evidence

This page records the checks shown during the project walkthrough. The validated run was performed on **3 November 2026**.

## 1. Python and Kafka producer

The event generator was run from PowerShell with:

```powershell
python .\1_data_generation\main.py --count 10
```

The terminal showed:

```text
Kafka delivery completed successfully. Messages delivered: 40
Orders generated: 10
Expected messages: 40
Messages confirmed delivered: 40
```

Result: **40 of 40 Kafka messages were confirmed delivered** — 10 each for orders, deliveries, products, and riders.

## 2. S3 landing and Snowflake stage

The S3 bucket observed was `hyper-delivery-data-20261012-k7m4`, with four prefixes below `raw/`:

- `quick_commerce_order_events/`
- `quick_commerce_delivery_events/`
- `quick_commerce_product_events/`
- `quick_commerce_rider_events/`

The Snowflake command `LIST @HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE;` returned 22 objects. The grouped file inventory was:

| Topic prefix | Files | Bytes |
|---|---:|---:|
| Delivery | 6 | 3,371 |
| Order | 5 | 2,761 |
| Product | 5 | 2,290 |
| Rider | 6 | 1,484 |
| **Total** | **22** | **9,906** |

A separate query read the staged JSON files and counted event records:

| Event type | Records | Files |
|---|---:|---:|
| Deliveries | 11 | 6 |
| Orders | 11 | 5 |
| Products | 11 | 5 |
| Riders | 11 | 6 |
| **Total** | **44** | **22** |

This includes the earlier single event per type plus the 10-event batch per type. The 22 S3 objects are not 22 records; each object may contain more than one event.

## 3. Bronze layer

The four existing Bronze tables were queried after the `COPY INTO` loads:

| Bronze table | Rows |
|---|---:|
| `BRONZE_ORDER_EVENTS` | 11 |
| `BRONZE_DELIVERY_EVENTS` | 11 |
| `BRONZE_PRODUCT_EVENTS` | 11 |
| `BRONZE_RIDER_EVENTS` | 11 |
| **Total** | **44** |

## 4. Silver layer

Before the incremental Silver update, each table had one row and one business-key match against Bronze. The incremental transformations then ran and the post-run count query returned:

| Silver table | Rows |
|---|---:|
| `SILVER_ORDER_EVENTS` | 11 |
| `SILVER_DELIVERY_EVENTS` | 11 |
| `SILVER_PRODUCT_EVENTS` | 11 |
| `SILVER_RIDER_EVENTS` | 11 |
| **Total** | **44** |

The update used business-key checks to avoid inserting an already-present event. For a production implementation, enforce/monitor uniqueness at the model level and account for concurrent executions; standard Snowflake tables do not automatically enforce ordinary primary-key uniqueness.

## 5. Gold layer

The four Gold tables were refreshed from Silver. A read-only query returned 21 total aggregate rows:

| Gold table | Rows | Meaning |
|---|---:|---|
| `GOLD_ORDERS_STATUS` | 4 | Four order-status groups |
| `GOLD_PRODUCT_POPULARITY` | 5 | Five product aggregates |
| `GOLD_RIDER_STATUS` | 1 | One latest rider-status group (the batch generated riders as `BUSY`) |
| `GOLD_BUSINESS_METRICS` | 11 | City/time-window business metric groups |
| **Total** | **21** | **Aggregate rows, not raw events** |

The inspected Gold records included order status counts of 3 `PACKED`, 3 `CONFIRMED`, 3 `DELIVERED`, and 2 `OUT_FOR_DELIVERY`, which sum to 11 orders. One visible product aggregate was `Milk 1L` with a total order count of 5.

## 6. Summary

| Pipeline stage | Evidence | Status |
|---|---|---|
| Python generators | Four generators used in the batch | Passed |
| Kafka publishing | 40/40 delivery confirmations | Passed |
| S3 sink | Topic-specific raw folders and objects visible | Passed |
| Snowflake stage | 22 objects listed; 44 records read | Passed |
| Bronze | 44 rows across four tables | Passed |
| Silver | 44 rows across four tables | Passed |
| Gold | 21 aggregate rows across four tables | Passed |

## 7. What these tests do not prove

- They do not prove continuous/automatic end-to-end orchestration. Snowflake SQL stages were manually executed during the walkthrough.
- They do not constitute a load, stress, failover, or recovery test.
- They do not validate Power BI; Power BI was intentionally skipped.
- They do not prove a production-grade schema evolution, dead-letter, alerting, or secrets-rotation process.
- A successful producer callback alone does not prove downstream S3/Snowflake completion; that was separately checked in this run using S3 objects and Snowflake stage/table queries.

## 8. Re-run verification queries

### Snowflake staged-record count

Run this after listing the stage, or use the full external-stage query from the walkthrough:

```sql
SELECT
    CASE
        WHEN METADATA$FILENAME ILIKE '%quick_commerce_order_events/%' THEN 'ORDERS'
        WHEN METADATA$FILENAME ILIKE '%quick_commerce_delivery_events/%' THEN 'DELIVERIES'
        WHEN METADATA$FILENAME ILIKE '%quick_commerce_product_events/%' THEN 'PRODUCTS'
        WHEN METADATA$FILENAME ILIKE '%quick_commerce_rider_events/%' THEN 'RIDERS'
    END AS EVENT_TYPE,
    COUNT(*) AS RECORD_COUNT,
    COUNT(DISTINCT METADATA$FILENAME) AS FILE_COUNT
FROM @HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE
  (FILE_FORMAT => 'HYPER_DELIVERY_DB.BRONZE.JSON_FORMAT')
WHERE METADATA$FILENAME ILIKE '%quick_commerce_%'
GROUP BY EVENT_TYPE
ORDER BY EVENT_TYPE;
```

### Bronze and Silver counts

```sql
SELECT 'BRONZE_ORDERS' AS TABLE_NAME, COUNT(*) AS ROWS_COUNT
FROM HYPER_DELIVERY_DB.BRONZE.BRONZE_ORDER_EVENTS
UNION ALL SELECT 'BRONZE_DELIVERIES', COUNT(*)
FROM HYPER_DELIVERY_DB.BRONZE.BRONZE_DELIVERY_EVENTS
UNION ALL SELECT 'BRONZE_PRODUCTS', COUNT(*)
FROM HYPER_DELIVERY_DB.BRONZE.BRONZE_PRODUCT_EVENTS
UNION ALL SELECT 'BRONZE_RIDERS', COUNT(*)
FROM HYPER_DELIVERY_DB.BRONZE.BRONZE_RIDER_EVENTS
UNION ALL SELECT 'SILVER_ORDERS', COUNT(*)
FROM HYPER_DELIVERY_DB.SILVER.SILVER_ORDER_EVENTS
UNION ALL SELECT 'SILVER_DELIVERIES', COUNT(*)
FROM HYPER_DELIVERY_DB.SILVER.SILVER_DELIVERY_EVENTS
UNION ALL SELECT 'SILVER_PRODUCTS', COUNT(*)
FROM HYPER_DELIVERY_DB.SILVER.SILVER_PRODUCT_EVENTS
UNION ALL SELECT 'SILVER_RIDERS', COUNT(*)
FROM HYPER_DELIVERY_DB.SILVER.SILVER_RIDER_EVENTS;
```

### Gold counts

```sql
SELECT 'GOLD_ORDERS_STATUS' AS TABLE_NAME, COUNT(*) AS ROWS_COUNT
FROM HYPER_DELIVERY_DB.GOLD.GOLD_ORDERS_STATUS
UNION ALL SELECT 'GOLD_PRODUCT_POPULARITY', COUNT(*)
FROM HYPER_DELIVERY_DB.GOLD.GOLD_PRODUCT_POPULARITY
UNION ALL SELECT 'GOLD_RIDER_STATUS', COUNT(*)
FROM HYPER_DELIVERY_DB.GOLD.GOLD_RIDER_STATUS
UNION ALL SELECT 'GOLD_BUSINESS_METRICS', COUNT(*)
FROM HYPER_DELIVERY_DB.GOLD.GOLD_BUSINESS_METRICS;
```
