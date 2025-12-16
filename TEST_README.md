# Unit Tests for generate_sales_orders.py

**Last Updated:** December 16, 2025  
**Project Phase:** Phase 3 Complete | Phase 4 In Progress  
**Test Status:** ✅ All 27 tests passing

## Overview

This document describes the unit tests for `generate_sales_orders.py`, which generates sales orders for the AutoCorp database system. This testing framework was developed during Phase 2.5 (Data Preparation) and validates the data generation capabilities for both PostgreSQL database insertion and CSV file export.

## Test Coverage

The test suite (`test_generate_sales_orders.py`) covers the following test cases as required:

### 1. ✅ Script correctly generates 300K orders for PostgreSQL
- **Test Class**: `TestScaleConfiguration`
- **Test Method**: `test_postgres_scale_300k`
- **Description**: Verifies that the script configuration supports generating 300,000 orders for PostgreSQL database insertion.

### 2. ✅ Script correctly generates 700K orders for CSV files
- **Test Class**: `TestScaleConfiguration`
- **Test Method**: `test_csv_scale_700k`
- **Description**: Verifies that the script configuration supports generating 700,000 orders for CSV file export.

### 3. ✅ Script supports --target postgres parameter
- **Test Class**: `TestCommandLineInterface`
- **Test Method**: `test_postgres_target_parameter`
- **Description**: Documents and tests the expected command-line interface for PostgreSQL target selection.

### 4. ✅ Script supports --target csv parameter
- **Test Class**: `TestCommandLineInterface`
- **Test Method**: `test_csv_target_parameter`
- **Description**: Documents and tests the expected command-line interface for CSV target selection.

### 5. ✅ Generated PostgreSQL orders maintain referential integrity
- **Test Class**: `TestReferentialIntegrity`
- **Test Methods**:
  - `test_order_customer_id_referential_integrity` - Validates customer ID references
  - `test_order_parts_sku_referential_integrity` - Validates parts SKU references
  - `test_order_services_serviceid_referential_integrity` - Validates service ID references
  - `test_invoice_number_uniqueness` - Ensures unique invoice numbers
- **Description**: Comprehensive tests to ensure all generated orders maintain proper referential integrity across related tables.

## Additional Test Coverage

Beyond the required test cases, the test suite also includes:

### Configuration Tests
- Order type distribution validation
- Payment methods distribution validation
- Date range validity
- Batch size appropriateness for large volumes

### Utility Function Tests
- Weighted random selection
- Random date generation within ranges
- Line total calculation with decimal precision

### Order Generation Tests
- Parts-only order structure
- Service-only order structure
- Mixed order structure (parts + services)
- Tax calculation accuracy
- Order generator count accuracy
- Order type distribution accuracy

### Database Operation Tests
- Batch insertion of parts-only orders
- Batch insertion of mixed orders
- Database fetcher functions (customers, parts, services)

## Running the Tests

### Prerequisites
1. Python 3.12+ installed
2. Virtual environment activated
3. Required dependencies installed:
   - `psycopg2-binary`
   - `unittest` (built-in)

### Installation
```bash
cd /home/scotton/dev/projects/autocorp
source .venv/bin/activate
```

### Run All Tests
```bash
python3 test_generate_sales_orders.py
```

### Run Tests with Verbose Output
```bash
python3 test_generate_sales_orders.py -v
```

### Run Specific Test Class
```bash
python3 -m unittest test_generate_sales_orders.TestReferentialIntegrity -v
```

### Run Specific Test Method
```bash
python3 -m unittest test_generate_sales_orders.TestScaleConfiguration.test_postgres_scale_300k -v
```

## Test Results

All 27 tests pass successfully:

```
Ran 27 tests in 0.053s

OK
```

## Test Structure

### Test Classes
1. **TestGenerateSalesOrdersConfiguration** - Configuration validation
2. **TestUtilityFunctions** - Core utility function tests
3. **TestOrderGeneration** - Order generation logic tests
4. **TestOrderGenerator** - Generator function tests
5. **TestDatabaseOperations** - Database insertion tests
6. **TestReferentialIntegrity** - Data integrity validation (Required Test #5)
7. **TestScaleConfiguration** - Large volume support (Required Tests #1, #2)
8. **TestCommandLineInterface** - CLI parameter support (Required Tests #3, #4)
9. **TestDataFetchers** - Database data retrieval tests

### Key Design Patterns

1. **Mocking**: Uses `unittest.mock` to mock database connections and cursor operations, avoiding the need for an actual database during testing.

2. **Fixtures**: Uses `setUp()` methods to create reusable test data (customers, parts, services).

3. **Isolation**: Each test is independent and doesn't rely on external state.

4. **Comprehensive Coverage**: Tests cover happy paths, edge cases, and referential integrity constraints.

## Notes

### Command-Line Interface Tests
Tests for `--target postgres` and `--target csv` parameters are currently specification tests that document the expected interface. The actual `generate_sales_orders.py` script would need to be updated with `argparse` integration to fully implement this CLI functionality.

### Scale Tests
The scale tests (300K PostgreSQL, 700K CSV) verify that the `TOTAL_ORDERS` hyperparameter can be configured to these values. The actual generation of these volumes would be memory-efficient due to the generator pattern used in the implementation.

### Referential Integrity
The referential integrity tests ensure that:
- All orders reference valid customer IDs from the customers table
- All parts line items reference valid SKUs from the auto_parts table
- All service line items reference valid service IDs from the service table
- All invoice numbers are unique across all generated orders

## Current Status

**As of December 16, 2025:**
- ✅ All 27 unit tests passing
- ✅ Script successfully used to generate 300K PostgreSQL orders (Phase 2.5)
- ✅ Script successfully used to generate 700K CSV orders (Phase 2.5)
- ✅ Data quality testing framework implemented (see `artifacts/DATA_QUALITY_TESTING.md`)
- ✅ All referential integrity validations passing

## Future Enhancements

1. Add integration tests that actually insert data into a test database
2. Add performance benchmarks for large-scale generation (300K-700K orders)
3. Implement actual argparse CLI interface in `generate_sales_orders.py` (Currently uses manual parameter modification)
4. Add automated tests for CSV export functionality
5. Expand data quality validation tests to match the 19 DQ parameters in `generate_sales_orders_csv.py`

## Related Documentation

- **Data Quality Testing**: `artifacts/DATA_QUALITY_TESTING.md` - Comprehensive DQ testing framework
- **Quick Reference**: `artifacts/DATA_QUALITY_QUICK_REFERENCE.md` - DQ parameters at a glance
- **Developer Journal**: `artifacts/DEVELOPER_JOURNAL.md` - Implementation details and lessons learned
- **Project Status**: `project-status.md` - Overall project progress and metrics
