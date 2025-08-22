"""
Unit tests for OrderService business logic.

This module contains comprehensive tests for the order processing service,
including subtotal calculation, shipping costs, discount application,
and complete order processing workflows.
"""

import pytest
from decimal import Decimal
from app.services.order_service import OrderService
from app.models.orders import OrderRequest, Product, SocioeconomicStratum


class TestOrderService:
    """Test cases for OrderService class."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = OrderService()
    
    def test_calculate_subtotal_single_product(self):
        """Test subtotal calculation with a single product."""
        order = OrderRequest(
            products=[Product(name="Pizza", price=Decimal('25000'), quantity=1)],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        subtotal = self.service.calculate_subtotal(order)
        assert subtotal == Decimal('25000.00')
    
    def test_calculate_subtotal_multiple_products(self):
        """Test subtotal calculation with multiple products."""
        order = OrderRequest(
            products=[
                Product(name="Pizza", price=Decimal('25000'), quantity=2),
                Product(name="Soda", price=Decimal('3000'), quantity=3),
                Product(name="Salad", price=Decimal('15000'), quantity=1)
            ],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        # (25000 * 2) + (3000 * 3) + (15000 * 1) = 50000 + 9000 + 15000 = 74000
        subtotal = self.service.calculate_subtotal(order)
        assert subtotal == Decimal('74000.00')
    
    def test_calculate_subtotal_decimal_prices(self):
        """Test subtotal calculation with decimal prices."""
        order = OrderRequest(
            products=[
                Product(name="Coffee", price=Decimal('4.50'), quantity=2),
                Product(name="Pastry", price=Decimal('3.75'), quantity=1)
            ],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        # (4.50 * 2) + (3.75 * 1) = 9.00 + 3.75 = 12.75
        subtotal = self.service.calculate_subtotal(order)
        assert subtotal == Decimal('12.75')
    
    @pytest.mark.parametrize("stratum,expected_cost", [
        (SocioeconomicStratum.STRATUM_1, Decimal('2000')),
        (SocioeconomicStratum.STRATUM_2, Decimal('3000')),
        (SocioeconomicStratum.STRATUM_3, Decimal('5000')),
        (SocioeconomicStratum.STRATUM_4, Decimal('6000')),
        (SocioeconomicStratum.STRATUM_5, Decimal('8000')),
        (SocioeconomicStratum.STRATUM_6, Decimal('10000')),
    ])
    def test_calculate_shipping_cost_all_strata(self, stratum, expected_cost):
        """Test shipping cost calculation for all socioeconomic strata."""
        shipping_cost = self.service.calculate_shipping_cost(stratum)
        assert shipping_cost == expected_cost
    
    @pytest.mark.parametrize("subtotal,expected_percentage,expected_amount", [
        (Decimal('30000'), Decimal('0'), Decimal('0')),      # No discount
        (Decimal('50000'), Decimal('0.05'), Decimal('2500')), # 5% discount
        (Decimal('75000'), Decimal('0.05'), Decimal('3750')), # 5% discount
        (Decimal('100000'), Decimal('0.10'), Decimal('10000')), # 10% discount
        (Decimal('150000'), Decimal('0.10'), Decimal('15000')), # 10% discount
        (Decimal('200000'), Decimal('0.15'), Decimal('30000')), # 15% discount
        (Decimal('300000'), Decimal('0.15'), Decimal('45000')), # 15% discount
    ])
    def test_calculate_discount_all_tiers(self, subtotal, expected_percentage, expected_amount):
        """Test discount calculation for all discount tiers."""
        percentage, amount = self.service.calculate_discount(subtotal)
        assert percentage == expected_percentage
        assert amount == expected_amount
    
    def test_process_order_no_discount(self):
        """Test complete order processing without discount."""
        order = OrderRequest(
            products=[Product(name="Burger", price=Decimal('15000'), quantity=2)],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        
        result = self.service.process_order(order)
        
        # Subtotal: 15000 * 2 = 30000
        # Shipping: 5000 (stratum 3)
        # Discount: 0 (under 50000 threshold)
        # Total: 30000 + 5000 = 35000
        
        assert result['subtotal'] == Decimal('30000.00')
        assert result['shipping_cost'] == Decimal('5000')
        assert result['discount_percentage'] == Decimal('0')
        assert result['discount_amount'] == Decimal('0')
        assert result['total_cost'] == Decimal('35000.00')
        
        # Check breakdown
        breakdown = result['breakdown']
        assert len(breakdown['products']) == 1
        assert breakdown['products'][0]['name'] == "Burger"
        assert breakdown['products'][0]['total'] == 30000.0
        assert breakdown['stratum'] == 3
        assert not breakdown['discount_applied']
    
    def test_process_order_with_discount(self):
        """Test complete order processing with discount applied."""
        order = OrderRequest(
            products=[
                Product(name="Pizza", price=Decimal('25000'), quantity=3),
                Product(name="Drinks", price=Decimal('5000'), quantity=5)
            ],
            stratum=SocioeconomicStratum.STRATUM_5
        )
        
        result = self.service.process_order(order)
        
        # Subtotal: (25000 * 3) + (5000 * 5) = 75000 + 25000 = 100000
        # Shipping: 8000 (stratum 5)
        # Discount: 10% on 100000 = 10000
        # Total: 100000 + 8000 - 10000 = 98000
        
        assert result['subtotal'] == Decimal('100000.00')
        assert result['shipping_cost'] == Decimal('8000')
        assert result['discount_percentage'] == Decimal('0.10')
        assert result['discount_amount'] == Decimal('10000.00')
        assert result['total_cost'] == Decimal('98000.00')
        
        # Check breakdown
        breakdown = result['breakdown']
        assert len(breakdown['products']) == 2
        assert breakdown['stratum'] == 5
        assert breakdown['discount_applied']
        assert breakdown['total_before_discount'] == 108000.0
        assert breakdown['final_total'] == 98000.0
    
    def test_process_order_maximum_discount(self):
        """Test order processing with maximum discount tier."""
        order = OrderRequest(
            products=[Product(name="Family Meal", price=Decimal('250000'), quantity=1)],
            stratum=SocioeconomicStratum.STRATUM_1
        )
        
        result = self.service.process_order(order)
        
        # Subtotal: 250000
        # Shipping: 2000 (stratum 1)
        # Discount: 15% on 250000 = 37500
        # Total: 250000 + 2000 - 37500 = 214500
        
        assert result['subtotal'] == Decimal('250000.00')
        assert result['shipping_cost'] == Decimal('2000')
        assert result['discount_percentage'] == Decimal('0.15')
        assert result['discount_amount'] == Decimal('37500.00')
        assert result['total_cost'] == Decimal('214500.00')
    
    def test_process_order_edge_case_exact_threshold(self):
        """Test order processing with exact discount threshold amount."""
        order = OrderRequest(
            products=[Product(name="Order", price=Decimal('50000'), quantity=1)],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        
        result = self.service.process_order(order)
        
        # Subtotal: 50000 (exactly at 5% discount threshold)
        # Shipping: 5000 (stratum 3)
        # Discount: 5% on 50000 = 2500
        # Total: 50000 + 5000 - 2500 = 52500
        
        assert result['subtotal'] == Decimal('50000.00')
        assert result['discount_percentage'] == Decimal('0.05')
        assert result['discount_amount'] == Decimal('2500.00')
        assert result['total_cost'] == Decimal('52500.00')
    
    def test_process_order_empty_products_validation(self):
        """Test that empty products list raises validation error."""
        with pytest.raises(ValueError):
            OrderRequest(
                products=[],
                stratum=SocioeconomicStratum.STRATUM_3
            )
    
    def test_breakdown_structure(self):
        """Test that breakdown structure contains all expected fields."""
        order = OrderRequest(
            products=[Product(name="Test Product", price=Decimal('10000'), quantity=1)],
            stratum=SocioeconomicStratum.STRATUM_3
        )
        
        result = self.service.process_order(order)
        breakdown = result['breakdown']
        
        # Check required fields in breakdown
        required_fields = [
            'products', 'subtotal', 'shipping_cost', 'stratum',
            'discount_applied', 'discount_threshold_met',
            'total_before_discount', 'final_total'
        ]
        
        for field in required_fields:
            assert field in breakdown, f"Missing field in breakdown: {field}"
        
        # Check product structure
        product = breakdown['products'][0]
        product_fields = ['name', 'price', 'quantity', 'total']
        for field in product_fields:
            assert field in product, f"Missing field in product breakdown: {field}"
