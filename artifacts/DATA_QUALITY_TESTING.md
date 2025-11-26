# Data Quality Testing Documentation

## Overview
The `generate_sales_orders_csv.py` script includes comprehensive data quality testing features designed to validate AWS DataSync → Glue Crawler → Data Catalog ETL pipelines. These features intentionally inject various data quality issues to test pipeline robustness and error handling.

## Purpose
- Test ETL pipeline handling of missing/null values
- Validate data type inference and schema detection by Glue Crawlers
- Test business logic validation and constraint enforcement
- Verify data transformation and cleaning processes
- Ensure proper error handling and logging in the pipeline

## Data Quality Testing Categories

### 1. Missing/Null Values

Tests how the pipeline handles incomplete data:

| Parameter | Default Rate | Description | Expected Behavior |
|-----------|-------------|-------------|-------------------|
| `MISSING_CUSTOMER_ID_RATE` | 0.007 (0.7%) | Customer IDs set to empty string | Should be interpreted as NULL in target |
| `MISSING_ORDER_DATE_RATE` | 0.0002 (0.02%) | Order dates set to empty string | Should be interpreted as NULL/NaT |
| `MISSING_TAX_RATE` | 0.001 (0.1%) | Tax values set to empty string | Should be interpreted as NaN |
| `MISSING_INVOICE_NUMBER_RATE` | 0.0005 (0.05%) | Invoice numbers set to empty | Tests handling of missing required fields |
| `MISSING_PAYMENT_METHOD_RATE` | 0.002 (0.2%) | Payment methods set to empty | Tests categorical field null handling |
| `MISSING_SUBTOTAL_RATE` | 0.0003 (0.03%) | Subtotals set to empty | Tests numeric field null handling |

**Testing Focus:**
- Schema inference with sparse data
- NULL constraint violations
- Referential integrity checks
- Default value substitution

### 2. Invalid Data Formats

Tests pipeline validation and data cleansing:

| Parameter | Default Rate | Description | Examples |
|-----------|-------------|-------------|----------|
| `INVALID_DATE_FORMAT_RATE` | 0.0008 (0.08%) | Malformed date strings | "2024-13-45", "invalid-date", "2024/06/15" |
| `WHITESPACE_CUSTOMER_ID_RATE` | 0.001 (0.1%) | IDs with leading/trailing whitespace | " 123", "456 ", "  789  " |
| `FORMATTED_NUMBER_RATE` | 0.0015 (0.15%) | Numbers with comma formatting | "1,234.56" |
| `CURRENCY_SYMBOL_RATE` | 0.0005 (0.05%) | Numbers with currency symbols | "$123.45" |

**Testing Focus:**
- Date parsing and validation
- String trimming/normalization
- Numeric type conversion
- Data cleansing transformations

### 3. Edge Cases and Business Logic Violations

Tests constraint enforcement and data validation rules:

| Parameter | Default Rate | Description | Impact |
|-----------|-------------|-------------|--------|
| `DUPLICATE_ORDER_ID_RATE` | 0.0001 (0.01%) | Duplicate primary key values | Should trigger uniqueness constraint errors |
| `NEGATIVE_AMOUNT_RATE` | 0.0005 (0.05%) | Negative monetary amounts | Business rule violation (amounts should be positive) |
| `FUTURE_DATE_RATE` | 0.001 (0.1%) | Dates beyond `ORDER_DATE_END` | Tests date range validation |
| `PAST_DATE_RATE` | 0.0008 (0.08%) | Dates before `ORDER_DATE_START` | Tests date range validation |
| `ZERO_QUANTITY_RATE` | 0.0003 (0.03%) | Line items with quantity = 0 | Business rule violation (quantities should be positive) |

**Testing Focus:**
- Primary key uniqueness constraints
- CHECK constraints on numeric ranges
- Business rule validation
- Temporal consistency checks

## Validation Manifest

When `GENERATE_MANIFEST = True`, the script generates a `data_validation_manifest.json` file containing:

### Manifest Structure

```json
{
  "generation_timestamp": "ISO-8601 timestamp",
  "configuration": {
    "total_orders": 791532,
    "order_type_distribution": {...},
    "date_range": {...},
    "tax_rate": 0.08
  },
  "data_quality_parameters": {
    "missing_values": {...},
    "invalid_data": {...},
    "edge_cases": {...}
  },
  "expected_counts": {
    "total_orders": 791532,
    "parts_line_items": 1234567,
    "service_line_items": 234567,
    "orders_by_type": {...}
  },
  "expected_issues": {
    "missing_customer_ids": 5541,
    "missing_order_dates": 158,
    "missing_tax": 791,
    "invalid_dates": 633,
    "duplicate_order_ids": 79,
    "future_dates": 791,
    "past_dates": 633
  },
  "revenue_statistics": {...},
  "files": {...}
}
```

### Using the Manifest

The manifest serves as ground truth for validation:

1. **Pre-ETL Validation**: Document expected data quality issues before pipeline execution
2. **Post-ETL Verification**: Compare actual issues found vs. expected issues
3. **Data Lineage**: Track data generation parameters and timestamps
4. **Regression Testing**: Use manifest to ensure consistent test scenarios

## Testing Workflow

### 1. Generate Test Data

```bash
python generate_sales_orders_csv.py
```

This creates:
- `sales_orders.csv` - Main orders table
- `sales_order_parts.csv` - Parts line items
- `sales_order_services.csv` - Service line items
- `data_validation_manifest.json` - Validation metadata

### 2. Upload to S3 via DataSync

Configure DataSync to sync the generated CSV files to S3.

### 3. Run Glue Crawler

Configure and run Glue Crawler to:
- Infer schema from CSV files
- Detect data types (handling nulls and invalid values)
- Create/update Data Catalog tables

**Key Questions to Validate:**
- How does the crawler handle columns with high null rates?
- Are date columns properly typed despite invalid formats?
- Are numeric columns properly typed despite comma formatting?

### 4. Execute Glue ETL Job

Run your ETL transformations and validate:

**Data Cleansing:**
- Are invalid dates filtered or fixed?
- Are whitespace issues trimmed?
- Are formatted numbers properly parsed?

**Constraint Enforcement:**
- Are duplicate order IDs detected and handled?
- Are negative amounts flagged or rejected?
- Are out-of-range dates filtered?

**Null Handling:**
- How are missing values handled in aggregations?
- Are nulls properly propagated or substituted?

### 5. Compare Results Against Manifest

Use the manifest's `expected_issues` section to verify:
- Expected number of issues detected
- No unexpected data loss
- Proper error logging and handling

## Customizing Test Scenarios

### Scenario 1: Clean Data (Production Simulation)

Set all rates to 0.0:

```python
MISSING_CUSTOMER_ID_RATE = 0.0
MISSING_ORDER_DATE_RATE = 0.0
# ... set all rates to 0.0
```

**Use Case:** Establish baseline performance and validate pipeline with clean data.

### Scenario 2: High Null Rate (Stress Test)

Increase null rates:

```python
MISSING_CUSTOMER_ID_RATE = 0.05  # 5%
MISSING_ORDER_DATE_RATE = 0.03   # 3%
MISSING_TAX_RATE = 0.02          # 2%
```

**Use Case:** Test pipeline resilience with degraded data quality.

### Scenario 3: Format Testing (Data Ingestion Validation)

Focus on format issues:

```python
INVALID_DATE_FORMAT_RATE = 0.01   # 1%
FORMATTED_NUMBER_RATE = 0.05      # 5%
CURRENCY_SYMBOL_RATE = 0.02       # 2%
WHITESPACE_CUSTOMER_ID_RATE = 0.03  # 3%
```

**Use Case:** Validate data cleansing and parsing logic.

### Scenario 4: Business Rule Violations

Test constraint enforcement:

```python
DUPLICATE_ORDER_ID_RATE = 0.001    # 0.1%
NEGATIVE_AMOUNT_RATE = 0.002       # 0.2%
ZERO_QUANTITY_RATE = 0.001         # 0.1%
FUTURE_DATE_RATE = 0.005           # 0.5%
```

**Use Case:** Validate business logic and constraint checks.

## AWS Glue Specific Considerations

### Schema Inference

Glue Crawlers infer schema based on sampled data:

- **High null rates** may cause incorrect type inference
- **Mixed formats** (e.g., both "123.45" and "$123.45") may result in STRING type instead of DOUBLE
- **Invalid dates** may prevent TIMESTAMP type detection

**Recommendation:** Review inferred schema in Data Catalog after each test run.

### Data Type Mapping

| CSV Content | Expected Glue Type | Notes |
|-------------|-------------------|--------|
| Empty string | NULL | Depends on column type |
| "2024-01-15 10:30:00" | TIMESTAMP | If all valid dates |
| Mixed valid/invalid dates | STRING | If crawler detects invalid formats |
| "123.45" | DOUBLE | If no formatting |
| "1,234.56" or "$123.45" | STRING | Due to non-numeric characters |

### Partitioning Considerations

If using date-based partitioning:

- **Missing order_dates**: Where do these records land?
- **Invalid date formats**: May cause partition creation failures
- **Out-of-range dates**: May create unexpected partitions

**Recommendation:** Test partition handling with `MISSING_ORDER_DATE_RATE` and `INVALID_DATE_FORMAT_RATE` > 0.

## Best Practices

### 1. Start with Low Rates
Begin with default rates (< 1%) to understand baseline behavior before stress testing.

### 2. Test One Category at a Time
Isolate testing by enabling only one category of issues to pinpoint specific behaviors.

### 3. Keep the Manifest
Archive manifests with test results for regression testing and documentation.

### 4. Monitor Glue Metrics
Track Glue Crawler and ETL job metrics:
- Records processed
- Records failed
- Schema changes detected
- Partition updates

### 5. Validate End-to-End
Ensure data quality checks exist at multiple pipeline stages:
- Pre-load validation
- ETL transformation validation
- Post-load data quality checks
- Business logic validation in analytics layer

## Troubleshooting

### Issue: Glue Crawler Types Column as STRING Instead of DOUBLE

**Likely Cause:** `FORMATTED_NUMBER_RATE` or `CURRENCY_SYMBOL_RATE` > 0

**Solution:** 
- Set rates to 0.0 for clean data test
- Or implement data cleansing in ETL to strip formatting

### Issue: Records Lost After ETL

**Likely Cause:** Aggressive filtering of invalid data without logging

**Solution:**
- Compare `expected_counts` in manifest with actual output row counts
- Review ETL job logs for filtered records
- Implement quarantine table for invalid records

### Issue: Duplicate Key Errors in Target Database

**Expected Behavior:** This tests primary key constraint enforcement

**Solution:**
- Verify ETL handles duplicates (dedupe, reject, or log)
- Check if duplicate tracking is working correctly

### Issue: Partition Explosion

**Likely Cause:** `FUTURE_DATE_RATE` or `PAST_DATE_RATE` creating unexpected partitions

**Solution:**
- Implement date range filtering in ETL
- Validate partition schemes handle invalid dates gracefully

## Summary

This data quality testing framework provides comprehensive coverage for:
- ✅ Missing value handling
- ✅ Invalid format detection
- ✅ Business rule enforcement
- ✅ Edge case handling
- ✅ ETL pipeline robustness

Use the manifest-based approach to establish reproducible test scenarios and track pipeline behavior over time.
