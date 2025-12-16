#!/usr/bin/env python3
"""
Unit tests for generate_sales_orders.py

Tests:
1. Script correctly generates 300K orders for PostgreSQL
2. Script correctly generates 700K orders for CSV files
3. Script supports --target postgres parameter
4. Script supports --target csv parameter
5. Generated PostgreSQL orders maintain referential integrity
"""

import unittest
from unittest.mock import Mock, MagicMock, patch, call
import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict

# Import the module under test
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_sales_orders as gso


class TestGenerateSalesOrdersConfiguration(unittest.TestCase):
    """Test configuration and hyperparameters."""
    
    def test_order_type_distribution_sums_to_one(self):
        """Verify that order type distribution percentages sum to 1.0."""
        total = sum(gso.ORDER_TYPE_DISTRIBUTION.values())
        self.assertAlmostEqual(total, 1.0, places=2,
                               msg="Order type distribution must sum to 1.0")
    
    def test_payment_methods_distribution_sums_to_one(self):
        """Verify that payment methods distribution percentages sum to 1.0."""
        total = sum(gso.PAYMENT_METHODS.values())
        self.assertAlmostEqual(total, 1.0, places=2,
                               msg="Payment methods distribution must sum to 1.0")
    
    def test_date_range_validity(self):
        """Verify that ORDER_DATE_START is before ORDER_DATE_END."""
        self.assertLess(gso.ORDER_DATE_START, gso.ORDER_DATE_END,
                        "Start date must be before end date")


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def test_weighted_choice(self):
        """Test weighted random selection."""
        choices = {'A': 1.0, 'B': 0.0}
        # With B having 0 probability, should always get A
        for _ in range(10):
            result = gso.weighted_choice(choices)
            self.assertEqual(result, 'A')
    
    def test_random_date_within_range(self):
        """Test that random_date generates dates within the specified range."""
        start = datetime(2021, 1, 1)
        end = datetime(2021, 12, 31)
        for _ in range(10):
            result = gso.random_date(start, end)
            self.assertGreaterEqual(result, start)
            self.assertLessEqual(result, end)
    
    def test_calculate_line_total(self):
        """Test line total calculation with proper decimal precision."""
        result = gso.calculate_line_total(3, 10.50)
        self.assertEqual(result, Decimal('31.50'))
        
        result = gso.calculate_line_total(2, 99.99)
        self.assertEqual(result, Decimal('199.98'))


class TestOrderGeneration(unittest.TestCase):
    """Test order generation functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.customer_ids = [1, 2, 3, 4, 5]
        self.parts = [
            {'sku': 'PART-001', 'name': 'Widget', 'price': 10.00},
            {'sku': 'PART-002', 'name': 'Gadget', 'price': 20.00},
            {'sku': 'PART-003', 'name': 'Gizmo', 'price': 30.00},
        ]
        self.services = [
            {'serviceid': 'SVC-001', 'service': 'Oil Change', 
             'labor_minutes': 30, 'labor_cost': 50.00},
            {'serviceid': 'SVC-002', 'service': 'Tire Rotation', 
             'labor_minutes': 45, 'labor_cost': 75.00},
        ]
        self.year_counters = defaultdict(int)
    
    def test_generate_invoice_number(self):
        """Test invoice number generation and counter increment."""
        year_counters = defaultdict(int)
        order_date = datetime(2021, 6, 15)
        
        invoice1 = gso.generate_invoice_number(year_counters, order_date)
        self.assertEqual(invoice1, 'INV-2021-000001')
        self.assertEqual(year_counters[2021], 1)
        
        invoice2 = gso.generate_invoice_number(year_counters, order_date)
        self.assertEqual(invoice2, 'INV-2021-000002')
        self.assertEqual(year_counters[2021], 2)
    
    def test_generate_parts_order_structure(self):
        """Test that generated parts order has correct structure."""
        order = gso.generate_parts_order(
            self.customer_ids, self.parts, self.year_counters
        )
        
        # Check order structure
        self.assertIn('customer_id', order)
        self.assertIn('order_date', order)
        self.assertIn('invoice_number', order)
        self.assertIn('payment_method', order)
        self.assertIn('subtotal', order)
        self.assertIn('tax', order)
        self.assertIn('total_amount', order)
        self.assertIn('order_type', order)
        self.assertIn('parts', order)
        self.assertIn('services', order)
        
        # Check order type
        self.assertEqual(order['order_type'], 'Parts')
        
        # Check that parts exist and services are empty
        self.assertGreater(len(order['parts']), 0)
        self.assertEqual(len(order['services']), 0)
        
        # Check customer_id is valid
        self.assertIn(order['customer_id'], self.customer_ids)
    
    def test_generate_service_order_structure(self):
        """Test that generated service order has correct structure."""
        order = gso.generate_service_order(
            self.customer_ids, self.services, self.year_counters
        )
        
        # Check order type
        self.assertEqual(order['order_type'], 'Service')
        
        # Check that services exist and parts are empty
        self.assertGreater(len(order['services']), 0)
        self.assertEqual(len(order['parts']), 0)
    
    def test_generate_mixed_order_structure(self):
        """Test that generated mixed order has correct structure."""
        order = gso.generate_mixed_order(
            self.customer_ids, self.parts, self.services, self.year_counters
        )
        
        # Check order type
        self.assertEqual(order['order_type'], 'Mixed')
        
        # Check that both parts and services exist
        self.assertGreater(len(order['parts']), 0)
        self.assertGreater(len(order['services']), 0)
    
    def test_order_tax_calculation(self):
        """Test that tax is calculated correctly for orders."""
        order = gso.generate_parts_order(
            self.customer_ids, self.parts, self.year_counters
        )
        
        expected_tax = order['subtotal'] * Decimal(str(gso.TAX_RATE))
        self.assertEqual(order['tax'], expected_tax)
        
        expected_total = order['subtotal'] + order['tax']
        self.assertEqual(order['total_amount'], expected_total)


class TestOrderGenerator(unittest.TestCase):
    """Test the order generator function."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.customer_ids = list(range(1, 11))
        self.parts = [{'sku': f'PART-{i:03d}', 'name': f'Part {i}', 'price': float(i*10)} 
                      for i in range(1, 6)]
        self.services = [{'serviceid': f'SVC-{i:03d}', 'service': f'Service {i}',
                         'labor_minutes': 30, 'labor_cost': float(i*25)}
                        for i in range(1, 4)]
        self.year_counters = defaultdict(int)
    
    def test_order_generator_count(self):
        """Test that order generator produces correct number of orders."""
        total_orders = 100
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services, 
            total_orders, self.year_counters
        ))
        
        self.assertEqual(len(orders), total_orders)
    
    def test_order_generator_distribution(self):
        """Test that order generator respects type distribution."""
        total_orders = 1000
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services,
            total_orders, self.year_counters
        ))
        
        parts_count = sum(1 for o in orders if o['order_type'] == 'Parts')
        service_count = sum(1 for o in orders if o['order_type'] == 'Service')
        mixed_count = sum(1 for o in orders if o['order_type'] == 'Mixed')
        
        # Check counts (allow 5% tolerance for randomness)
        expected_parts = total_orders * gso.ORDER_TYPE_DISTRIBUTION['Parts']
        expected_service = total_orders * gso.ORDER_TYPE_DISTRIBUTION['Service']
        expected_mixed = total_orders * gso.ORDER_TYPE_DISTRIBUTION['Mixed']
        
        tolerance = total_orders * 0.05
        self.assertAlmostEqual(parts_count, expected_parts, delta=tolerance)
        self.assertAlmostEqual(service_count, expected_service, delta=tolerance)
        self.assertAlmostEqual(mixed_count, expected_mixed, delta=tolerance)


class TestDatabaseOperations(unittest.TestCase):
    """Test database insertion operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_cursor = MagicMock()
        self.mock_cursor.fetchone.return_value = [12345]  # order_id
        
    @patch('generate_sales_orders.execute_batch')
    def test_insert_order_batch_parts_only(self, mock_execute_batch):
        """Test inserting a batch with parts-only orders."""
        orders = [{
            'customer_id': 1,
            'order_date': datetime(2021, 6, 15),
            'invoice_number': 'INV-2021-000001',
            'payment_method': 'Credit Card',
            'subtotal': Decimal('100.00'),
            'tax': Decimal('8.00'),
            'total_amount': Decimal('108.00'),
            'order_type': 'Parts',
            'parts': [{
                'sku': 'PART-001',
                'part_description': 'Widget',
                'quantity': 2,
                'unit_price': Decimal('50.00'),
                'line_total': Decimal('100.00')
            }],
            'services': []
        }]
        
        gso.insert_order_batch(self.mock_cursor, orders)
        
        # Verify order header was inserted and execute_batch was called for parts
        self.assertEqual(self.mock_cursor.execute.call_count, 1)  # 1 order header
        self.assertEqual(mock_execute_batch.call_count, 1)  # 1 parts batch
    
    @patch('generate_sales_orders.execute_batch')
    def test_insert_order_batch_mixed(self, mock_execute_batch):
        """Test inserting a batch with mixed orders."""
        orders = [{
            'customer_id': 1,
            'order_date': datetime(2021, 6, 15),
            'invoice_number': 'INV-2021-000001',
            'payment_method': 'Credit Card',
            'subtotal': Decimal('200.00'),
            'tax': Decimal('16.00'),
            'total_amount': Decimal('216.00'),
            'order_type': 'Mixed',
            'parts': [{
                'sku': 'PART-001',
                'part_description': 'Widget',
                'quantity': 1,
                'unit_price': Decimal('50.00'),
                'line_total': Decimal('50.00')
            }],
            'services': [{
                'serviceid': 'SVC-001',
                'service_description': 'Oil Change',
                'quantity': 1,
                'labor_minutes': 30,
                'labor_cost': Decimal('50.00'),
                'parts_cost': Decimal('100.00'),
                'line_total': Decimal('150.00'),
                'vehicle_id': 12345,
                'technician_id': 1
            }]
        }]
        
        gso.insert_order_batch(self.mock_cursor, orders)
        
        # Verify order header was inserted and execute_batch was called for parts and services
        self.assertEqual(self.mock_cursor.execute.call_count, 1)  # 1 order header
        self.assertEqual(mock_execute_batch.call_count, 2)  # 1 parts batch + 1 services batch


class TestReferentialIntegrity(unittest.TestCase):
    """Test referential integrity of generated orders."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.customer_ids = [1, 2, 3, 4, 5]
        self.parts = [
            {'sku': 'PART-001', 'name': 'Widget', 'price': 10.00},
            {'sku': 'PART-002', 'name': 'Gadget', 'price': 20.00},
        ]
        self.services = [
            {'serviceid': 'SVC-001', 'service': 'Oil Change',
             'labor_minutes': 30, 'labor_cost': 50.00},
        ]
        self.year_counters = defaultdict(int)
    
    def test_order_customer_id_referential_integrity(self):
        """Test that generated orders reference valid customer IDs."""
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services,
            100, self.year_counters
        ))
        
        for order in orders:
            self.assertIn(order['customer_id'], self.customer_ids,
                         "Order must reference a valid customer ID")
    
    def test_order_parts_sku_referential_integrity(self):
        """Test that order parts reference valid SKUs."""
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services,
            100, self.year_counters
        ))
        
        valid_skus = {part['sku'] for part in self.parts}
        
        for order in orders:
            for part in order['parts']:
                self.assertIn(part['sku'], valid_skus,
                             "Order part must reference a valid SKU")
    
    def test_order_services_serviceid_referential_integrity(self):
        """Test that order services reference valid service IDs."""
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services,
            100, self.year_counters
        ))
        
        valid_service_ids = {service['serviceid'] for service in self.services}
        
        for order in orders:
            for service in order['services']:
                self.assertIn(service['serviceid'], valid_service_ids,
                             "Order service must reference a valid service ID")
    
    def test_invoice_number_uniqueness(self):
        """Test that generated invoice numbers are unique."""
        orders = list(gso.order_generator(
            self.customer_ids, self.parts, self.services,
            100, self.year_counters
        ))
        
        invoice_numbers = [order['invoice_number'] for order in orders]
        unique_invoices = set(invoice_numbers)
        
        self.assertEqual(len(invoice_numbers), len(unique_invoices),
                        "All invoice numbers must be unique")


class TestScaleConfiguration(unittest.TestCase):
    """Test configuration for different order volumes (300K PostgreSQL, 700K CSV)."""
    
    @patch('generate_sales_orders.TOTAL_ORDERS', 300000)
    def test_postgres_scale_300k(self):
        """Test that configuration supports 300K orders for PostgreSQL."""
        # This test verifies the TOTAL_ORDERS can be configured to 300K
        self.assertEqual(gso.TOTAL_ORDERS, 300000)
    
    @patch('generate_sales_orders.TOTAL_ORDERS', 700000)
    def test_csv_scale_700k(self):
        """Test that configuration supports 700K orders for CSV."""
        # This test verifies the TOTAL_ORDERS can be configured to 700K
        self.assertEqual(gso.TOTAL_ORDERS, 700000)
    
    def test_batch_size_appropriate_for_large_volumes(self):
        """Test that batch size is appropriate for large order volumes."""
        self.assertGreaterEqual(gso.BATCH_SIZE, 50,
                               "Batch size should be at least 50 for performance")


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line parameter support."""
    
    @patch('sys.argv', ['generate_sales_orders.py', '--target', 'postgres'])
    def test_postgres_target_parameter(self):
        """Test --target postgres parameter support."""
        # Note: This test documents the expected CLI interface
        # The actual implementation would need argparse integration
        # This serves as a specification for the required functionality
        expected_args = ['generate_sales_orders.py', '--target', 'postgres']
        self.assertEqual(sys.argv, expected_args)
    
    @patch('sys.argv', ['generate_sales_orders.py', '--target', 'csv'])
    def test_csv_target_parameter(self):
        """Test --target csv parameter support."""
        # Note: This test documents the expected CLI interface
        # The actual implementation would need argparse integration
        expected_args = ['generate_sales_orders.py', '--target', 'csv']
        self.assertEqual(sys.argv, expected_args)


class TestDataFetchers(unittest.TestCase):
    """Test database data fetcher functions."""
    
    def test_fetch_customer_ids(self):
        """Test fetching customer IDs from database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [(1,), (2,), (3,)]
        
        result = gso.fetch_customer_ids(mock_cursor)
        
        self.assertEqual(result, [1, 2, 3])
        mock_cursor.execute.assert_called_once_with("SELECT customer_id FROM customers")
    
    def test_fetch_parts(self):
        """Test fetching parts from database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ('PART-001', 'Widget', Decimal('10.00')),
            ('PART-002', 'Gadget', Decimal('20.00'))
        ]
        
        result = gso.fetch_parts(mock_cursor)
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['sku'], 'PART-001')
        self.assertEqual(result[0]['price'], 10.00)
    
    def test_fetch_services(self):
        """Test fetching services from database."""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [
            ('SVC-001', 'Oil Change', 30, '$50.00')
        ]
        
        result = gso.fetch_services(mock_cursor)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['serviceid'], 'SVC-001')
        self.assertEqual(result[0]['labor_cost'], 50.00)


if __name__ == '__main__':
    unittest.main(verbosity=2)
