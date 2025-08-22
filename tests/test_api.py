"""
Integration tests for the FastAPI order processing endpoints.

This module contains tests for the complete API functionality including
request/response validation, error handling, and end-to-end workflows.
"""

import pytest
from fastapi.testclient import TestClient
from decimal import Decimal
from app.main import app

client = TestClient(app)


class TestOrderAPI:
    """Test cases for order processing API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Food Delivery Order Processing API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "healthy"
        assert "endpoints" in data
    
    def test_health_check_endpoint(self):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "food-delivery-api"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
    
    def test_calculate_order_simple_success(self):
        """Test successful order calculation with simple order."""
        order_data = {
            "products": [
                {
                    "name": "Pizza Margherita",
                    "price": 25000,
                    "quantity": 1
                }
            ],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] == 25000.0
        assert data["shipping_cost"] == 5000.0
        assert data["discount_percentage"] == 0.0
        assert data["discount_amount"] == 0.0
        assert data["total_cost"] == 30000.0
        
        # Check breakdown structure
        breakdown = data["breakdown"]
        assert len(breakdown["products"]) == 1
        assert breakdown["products"][0]["name"] == "Pizza Margherita"
        assert breakdown["stratum"] == 3
        assert not breakdown["discount_applied"]
    
    def test_calculate_order_with_discount(self):
        """Test order calculation with discount applied."""
        order_data = {
            "products": [
                {
                    "name": "Family Combo",
                    "price": 80000,
                    "quantity": 1
                },
                {
                    "name": "Dessert",
                    "price": 25000,
                    "quantity": 1
                }
            ],
            "stratum": 4
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] == 105000.0  # 80000 + 25000
        assert data["shipping_cost"] == 6000.0  # Stratum 4
        assert data["discount_percentage"] == 0.10  # 10% for orders over 100k
        assert data["discount_amount"] == 10500.0  # 10% of 105000
        assert data["total_cost"] == 100500.0  # 105000 + 6000 - 10500
        
        # Check breakdown
        breakdown = data["breakdown"]
        assert breakdown["discount_applied"]
        assert breakdown["stratum"] == 4
    
    def test_calculate_order_maximum_discount(self):
        """Test order calculation with maximum discount tier."""
        order_data = {
            "products": [
                {
                    "name": "Catering Package",
                    "price": 250000,
                    "quantity": 1
                }
            ],
            "stratum": 6
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] == 250000.0
        assert data["shipping_cost"] == 10000.0  # Stratum 6 premium
        assert data["discount_percentage"] == 0.15  # 15% for orders over 200k
        assert data["discount_amount"] == 37500.0  # 15% of 250000
        assert data["total_cost"] == 222500.0  # 250000 + 10000 - 37500
    
    def test_calculate_order_all_strata(self):
        """Test order calculation for all socioeconomic strata."""
        base_order = {
            "products": [
                {
                    "name": "Standard Meal",
                    "price": 20000,
                    "quantity": 1
                }
            ]
        }
        
        expected_shipping = {
            1: 2000, 2: 3000, 3: 5000,
            4: 6000, 5: 8000, 6: 10000
        }
        
        for stratum in range(1, 7):
            order_data = {**base_order, "stratum": stratum}
            response = client.post("/api/v1/orders/calculate", json=order_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["shipping_cost"] == expected_shipping[stratum]
            assert data["breakdown"]["stratum"] == stratum
    
    def test_calculate_order_validation_empty_products(self):
        """Test validation error for empty products list."""
        order_data = {
            "products": [],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 422
    
    def test_calculate_order_validation_invalid_stratum(self):
        """Test validation error for invalid stratum."""
        order_data = {
            "products": [
                {
                    "name": "Pizza",
                    "price": 25000,
                    "quantity": 1
                }
            ],
            "stratum": 7  # Invalid stratum
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 422
    
    def test_calculate_order_validation_negative_price(self):
        """Test validation error for negative price."""
        order_data = {
            "products": [
                {
                    "name": "Invalid Product",
                    "price": -1000,
                    "quantity": 1
                }
            ],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 422
    
    def test_calculate_order_validation_zero_quantity(self):
        """Test validation error for zero quantity."""
        order_data = {
            "products": [
                {
                    "name": "Product",
                    "price": 10000,
                    "quantity": 0
                }
            ],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 422
    
    def test_calculate_order_validation_missing_fields(self):
        """Test validation error for missing required fields."""
        order_data = {
            "products": [
                {
                    "name": "Product",
                    "price": 10000
                    # Missing quantity
                }
            ],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 422
    
    def test_get_shipping_costs(self):
        """Test shipping costs endpoint."""
        response = client.get("/api/v1/orders/shipping-costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "shipping_costs" in data
        assert "currency" in data
        assert data["currency"] == "COP"
        
        shipping_costs = data["shipping_costs"]
        assert len(shipping_costs) == 6
        
        # Verify all strata are present with correct costs
        expected_costs = {
            "1": 2000, "2": 3000, "3": 5000,
            "4": 6000, "5": 8000, "6": 10000
        }
        
        for stratum, cost in expected_costs.items():
            assert stratum in shipping_costs
            assert shipping_costs[stratum] == cost
    
    def test_get_discount_tiers(self):
        """Test discount tiers endpoint."""
        response = client.get("/api/v1/orders/discount-tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert "discount_tiers" in data
        assert "currency" in data
        assert data["currency"] == "COP"
        
        discount_tiers = data["discount_tiers"]
        assert len(discount_tiers) == 3
        
        # Verify discount tiers structure and values
        expected_tiers = [
            {"threshold": 200000, "discount_percentage": 0.15},
            {"threshold": 100000, "discount_percentage": 0.10},
            {"threshold": 50000, "discount_percentage": 0.05}
        ]
        
        for i, tier in enumerate(discount_tiers):
            assert "threshold" in tier
            assert "discount_percentage" in tier
            assert "description" in tier
            assert tier["threshold"] == expected_tiers[i]["threshold"]
            assert tier["discount_percentage"] == expected_tiers[i]["discount_percentage"]
    
    def test_calculate_order_with_decimal_prices(self):
        """Test order calculation with decimal prices."""
        order_data = {
            "products": [
                {
                    "name": "Coffee",
                    "price": 4.5,
                    "quantity": 3
                },
                {
                    "name": "Pastry",
                    "price": 2.75,
                    "quantity": 2
                }
            ],
            "stratum": 2
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        # (4.5 * 3) + (2.75 * 2) = 13.5 + 5.5 = 19.0
        assert data["subtotal"] == 19.0
        assert data["shipping_cost"] == 3000.0  # Stratum 2
        assert data["total_cost"] == 3019.0  # No discount (under threshold)
    
    def test_calculate_order_large_quantities(self):
        """Test order calculation with large quantities."""
        order_data = {
            "products": [
                {
                    "name": "Bulk Item",
                    "price": 1000,
                    "quantity": 100
                }
            ],
            "stratum": 1
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] == 100000.0  # 1000 * 100
        assert data["shipping_cost"] == 2000.0  # Stratum 1
        assert data["discount_percentage"] == 0.10  # 10% discount
        assert data["discount_amount"] == 10000.0
        assert data["total_cost"] == 92000.0  # 100000 + 2000 - 10000
    
    def test_response_headers(self):
        """Test that response includes expected headers."""
        response = client.get("/health")
        assert response.status_code == 200
        assert "X-Process-Time" in response.headers
        
        # Verify process time is a valid number
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    
    def test_404_error_handling(self):
        """Test 404 error handling for non-existent endpoints."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        
        data = response.json()
        assert "error" in data
        assert data["error"] == "Resource not found"
        assert data["status_code"] == 404


class TestAPIDocumentation:
    """Test cases for API documentation and metadata."""
    
    def test_openapi_schema_generation(self):
        """Test that OpenAPI schema is properly generated."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        schema = response.json()
        assert "info" in schema
        assert schema["info"]["title"] == "Food Delivery Order API"
        assert schema["info"]["version"] == "1.0.0"
        
        # Check that our endpoints are documented
        paths = schema["paths"]
        assert "/api/v1/orders/calculate" in paths
        assert "/api/v1/orders/shipping-costs" in paths
        assert "/api/v1/orders/discount-tiers" in paths
    
    def test_docs_endpoint_accessible(self):
        """Test that documentation endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_get_shipping_costs_success(self):
        """Test successful retrieval of shipping costs."""
        response = client.get("/api/v1/orders/shipping-costs")
        assert response.status_code == 200
        
        data = response.json()
        assert "shipping_costs" in data
        assert "currency" in data
        assert "description" in data
        assert data["currency"] == "COP"
        
        # Verify all strata are present
        shipping_costs = data["shipping_costs"]
        for stratum in range(1, 7):
            assert str(stratum) in shipping_costs
            assert isinstance(shipping_costs[str(stratum)], (int, float))
            assert shipping_costs[str(stratum)] > 0
    
    def test_get_shipping_costs_format_validation(self):
        """Test shipping costs response format validation."""
        response = client.get("/api/v1/orders/shipping-costs")
        assert response.status_code == 200
        
        data = response.json()
        required_fields = ["shipping_costs", "currency", "description"]
        for field in required_fields:
            assert field in data
        
        # Verify costs are properly formatted
        shipping_costs = data["shipping_costs"]
        assert len(shipping_costs) == 6  # 6 strata levels
        
        # Verify ascending cost order (higher stratum = higher cost)
        costs = [shipping_costs[str(i)] for i in range(1, 7)]
        assert costs == sorted(costs)  # Should be in ascending order
    
    def test_get_shipping_costs_all_strata_present(self):
        """Test that all Colombian socioeconomic strata are represented."""
        response = client.get("/api/v1/orders/shipping-costs")
        assert response.status_code == 200
        
        data = response.json()
        shipping_costs = data["shipping_costs"]
        
        # Expected strata and minimum costs
        expected_strata = {
            "1": 1000,  # Minimum expected cost for stratum 1
            "2": 2000,  # Minimum expected cost for stratum 2
            "3": 3000,  # etc.
            "4": 4000,
            "5": 5000,
            "6": 6000
        }
        
        for stratum, min_cost in expected_strata.items():
            assert stratum in shipping_costs
            assert shipping_costs[stratum] >= min_cost
    
    def test_get_discount_tiers_success(self):
        """Test successful retrieval of discount tiers."""
        response = client.get("/api/v1/orders/discount-tiers")
        assert response.status_code == 200
        
        data = response.json()
        assert "discount_tiers" in data
        assert "currency" in data
        assert data["currency"] == "COP"
        
        # Verify discount tiers structure
        discount_tiers = data["discount_tiers"]
        assert isinstance(discount_tiers, list)
        assert len(discount_tiers) >= 3  # At least 3 discount tiers
        
        for tier in discount_tiers:
            required_fields = ["threshold", "discount_percentage", "description"]
            for field in required_fields:
                assert field in tier
            
            assert tier["threshold"] > 0
            assert 0 < tier["discount_percentage"] <= 1.0
            assert isinstance(tier["description"], str)
    
    def test_get_discount_tiers_format_validation(self):
        """Test discount tiers response format validation."""
        response = client.get("/api/v1/orders/discount-tiers")
        assert response.status_code == 200
        
        data = response.json()
        discount_tiers = data["discount_tiers"]
        
        # Verify tiers are sorted by threshold (descending)
        thresholds = [tier["threshold"] for tier in discount_tiers]
        assert thresholds == sorted(thresholds, reverse=True)
        
        # Verify percentages are sorted by discount (descending) 
        percentages = [tier["discount_percentage"] for tier in discount_tiers]
        assert percentages == sorted(percentages, reverse=True)
    
    def test_get_discount_tiers_all_tiers_present(self):
        """Test that all expected discount tiers are present."""
        response = client.get("/api/v1/orders/discount-tiers")
        assert response.status_code == 200
        
        data = response.json()
        discount_tiers = data["discount_tiers"]
        
        # Expected minimum discount tiers
        expected_tiers = [
            {"min_threshold": 200000, "min_percentage": 0.10},
            {"min_threshold": 100000, "min_percentage": 0.05},
            {"min_threshold": 50000, "min_percentage": 0.03}
        ]
        
        # Verify we have at least the expected tiers
        for expected in expected_tiers:
            found = False
            for tier in discount_tiers:
                if (tier["threshold"] >= expected["min_threshold"] and 
                    tier["discount_percentage"] >= expected["min_percentage"]):
                    found = True
                    break
            assert found, f"Expected tier with threshold >= {expected['min_threshold']} not found"
    
    def test_calculate_order_edge_case_zero_discount_threshold(self):
        """Test order calculation at exact discount thresholds."""
        # Test at exact 50,000 COP threshold
        order_data = {
            "products": [
                {
                    "name": "Exact Threshold Test",
                    "price": 50000,
                    "quantity": 1
                }
            ],
            "stratum": 3
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] == 50000.0
        assert data["discount_percentage"] > 0  # Should have discount at threshold
        assert data["discount_amount"] > 0
    
    def test_calculate_order_maximum_products(self):
        """Test order calculation with many products."""
        # Test with 10 different products
        products = []
        for i in range(10):
            products.append({
                "name": f"Product {i+1}",
                "price": 5000 + (i * 1000),  # Varying prices
                "quantity": i + 1  # Varying quantities
            })
        
        order_data = {
            "products": products,
            "stratum": 4
        }
        
        response = client.post("/api/v1/orders/calculate", json=order_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["subtotal"] > 0
        assert len(data["breakdown"]["products"]) == 10
        
        # Verify each product is calculated correctly
        for i, product_breakdown in enumerate(data["breakdown"]["products"]):
            expected_total = (5000 + (i * 1000)) * (i + 1)
            assert product_breakdown["total"] == expected_total
