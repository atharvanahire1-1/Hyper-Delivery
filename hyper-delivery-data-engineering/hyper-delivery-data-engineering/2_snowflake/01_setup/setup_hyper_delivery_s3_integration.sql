
-- ============================================================
-- HYPER DELIVERY DATA ENGINEERING
-- SNOWFLAKE + AWS S3 INTEGRATION SETUP
-- ============================================================

-- 1. SET ROLE

USE ROLE ACCOUNTADMIN;


-- 2. CREATE DATABASE AND SCHEMA

CREATE DATABASE IF NOT EXISTS HYPER_DELIVERY_DB;

CREATE SCHEMA IF NOT EXISTS
    HYPER_DELIVERY_DB.BRONZE;


-- ============================================================
-- 3. CREATE AWS S3 STORAGE INTEGRATION
-- ============================================================

-- Replace these placeholders with your AWS configuration.
-- Do not publish your actual account-specific values.

CREATE STORAGE INTEGRATION HYPER_DELIVERY_S3_INT
    TYPE = EXTERNAL_STAGE
    STORAGE_PROVIDER = S3
    ENABLED = TRUE
    STORAGE_AWS_ROLE_ARN =
        'arn:aws:iam::<AWS_ACCOUNT_ID>:role/<IAM_ROLE_NAME>'
    STORAGE_ALLOWED_LOCATIONS = (
        's3://<BUCKET_NAME>/raw/'
    );


-- 4. GET AWS TRUST CONFIGURATION DETAILS

-- Use STORAGE_AWS_IAM_USER_ARN and STORAGE_AWS_EXTERNAL_ID
-- from this output to configure the AWS IAM role trust policy.

DESC INTEGRATION HYPER_DELIVERY_S3_INT;


-- ============================================================
-- 5. CREATE JSON FILE FORMAT
-- ============================================================

CREATE FILE FORMAT IF NOT EXISTS
    HYPER_DELIVERY_DB.BRONZE.JSON_FORMAT
    TYPE = JSON;


-- ============================================================
-- 6. CREATE EXTERNAL S3 STAGE
-- ============================================================

CREATE STAGE IF NOT EXISTS
    HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE
    URL = 's3://<BUCKET_NAME>/raw/'
    STORAGE_INTEGRATION = HYPER_DELIVERY_S3_INT
    FILE_FORMAT = HYPER_DELIVERY_DB.BRONZE.JSON_FORMAT;


-- ============================================================
-- 7. VERIFY STAGE
-- ============================================================

DESC STAGE
    HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE;


-- List files available in the raw S3 directory.
LIST @HYPER_DELIVERY_DB.BRONZE.S3_RAW_STAGE;


-- ============================================================
-- 8. VERIFY DATABASE AND SCHEMA
-- ============================================================

SHOW SCHEMAS IN DATABASE HYPER_DELIVERY_DB;

SHOW STAGES IN SCHEMA HYPER_DELIVERY_DB.BRONZE;

-- ============================================================
-- END OF SETUP
-- ============================================================
