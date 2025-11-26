# Data Quality Testing - Quick Reference

## Quick Start

```bash
# Generate test data with default data quality issues
python generate_sales_orders_csv.py

# Output files:
# - sales_orders.csv
# - sales_order_parts.csv
# - sales_order_services.csv
# - data_validation_manifest.json (if GENERATE_MANIFEST=True)
```

## Hyperparameter Quick Reference

### Missing/Null Values (in generate_sales_orders_csv.py)

```python
MISSING_CUSTOMER_ID_RATE = 0.007      # 0.7% - Empty customer IDs
MISSING_ORDER_DATE_RATE = 0.0002      # 0.02% - Empty order dates
MISSING_TAX_RATE = 0.001              # 0.1% - Empty tax values
MISSING_INVOICE_NUMBER_RATE = 0.0005  # 0.05% - Empty invoice numbers
MISSING_PAYMENT_METHOD_RATE = 0.002   # 0.2% - Empty payment methods
MISSING_SUBTOTAL_RATE = 0.0003        # 0.03% - Empty subtotals
```

### Invalid Data Formats

```python
INVALID_DATE_FORMAT_RATE = 0.0008     # 0.08% - Malformed dates
WHITESPACE_CUSTOMER_ID_RATE = 0.001   # 0.1% - IDs with whitespace
FORMATTED_NUMBER_RATE = 0.0015        # 0.15% - Numbers with commas
CURRENCY_SYMBOL_RATE = 0.0005         # 0.05% - Numbers with $ symbol
```

### Edge Cases

```python
DUPLICATE_ORDER_ID_RATE = 0.0001      # 0.01% - Duplicate IDs
NEGATIVE_AMOUNT_RATE = 0.0005         # 0.05% - Negative amounts
FUTURE_DATE_RATE = 0.001              # 0.1% - Dates after ORDER_DATE_END
PAST_DATE_RATE = 0.0008               # 0.08% - Dates before ORDER_DATE_START
ZERO_QUANTITY_RATE = 0.0003           # 0.03% - Zero quantities
```

### Manifest Generation

```python
GENERATE_MANIFEST = True              # Generate validation manifest JSON
```

## Common Test Scenarios

### Scenario 1: Clean Data (No Issues)
Set all rates to `0.0` - produces 100% valid data

### Scenario 2: Default Testing (Current Settings)
Use default rates - realistic mix of data quality issues

### Scenario 3: Stress Test
Increase all rates by 10x to test pipeline resilience

### Scenario 4: Specific Issue Testing
Set only one category to non-zero to isolate specific behavior

## Expected Issue Counts (Default Settings, 791,532 orders)

| Issue Type | Expected Count |
|-----------|----------------|
| Missing Customer IDs | ~5,541 |
| Missing Order Dates | ~158 |
| Missing Tax | ~791 |
| Invalid Date Formats | ~633 |
| Duplicate Order IDs | ~79 |
| Future Dates | ~791 |
| Past Dates | ~633 |

## Validation Checklist

After generating data and running through ETL pipeline:

- [ ] Check Glue Crawler schema inference (especially for columns with high null rates)
- [ ] Verify date columns properly typed (not STRING due to invalid formats)
- [ ] Confirm numeric columns not typed as STRING (due to formatting)
- [ ] Validate duplicate order IDs are detected/handled
- [ ] Check negative amounts are flagged/rejected
- [ ] Verify out-of-range dates are filtered/quarantined
- [ ] Compare actual vs. expected issue counts from manifest
- [ ] Ensure no unexpected data loss (check row counts)

## Manifest Contents

The `data_validation_manifest.json` includes:

- **generation_timestamp**: When data was generated
- **configuration**: All generation parameters
- **data_quality_parameters**: All DQ testing rates
- **expected_counts**: Row counts by table and order type
- **expected_issues**: Anticipated DQ issue counts
- **revenue_statistics**: Aggregate statistics for validation
- **files**: Paths to generated CSV files

## Troubleshooting

**Q: Getting STRING type instead of DOUBLE for numeric columns?**  
A: Set `FORMATTED_NUMBER_RATE` and `CURRENCY_SYMBOL_RATE` to 0.0

**Q: Date columns showing as STRING?**  
A: Set `INVALID_DATE_FORMAT_RATE` to 0.0

**Q: Need clean data for baseline testing?**  
A: Set all `*_RATE` parameters to 0.0

**Q: Want to test only null handling?**  
A: Set only `MISSING_*_RATE` parameters to non-zero values

## Files Generated

```
autocorp/
├── sales_orders.csv                  # Main orders table
├── sales_order_parts.csv             # Parts line items
├── sales_order_services.csv          # Service line items
└── data_validation_manifest.json     # Validation metadata
```

## Additional Resources

See `DATA_QUALITY_TESTING.md` for comprehensive documentation including:
- Detailed parameter descriptions
- Testing workflow
- AWS Glue specific considerations
- Best practices
- Troubleshooting guide
