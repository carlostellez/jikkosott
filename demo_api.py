#!/usr/bin/env python3
"""
Interactive API Demo Script

This script demonstrates all the Food Delivery API endpoints with real examples.
Run this after starting the API server to see it in action.

Usage:
    python demo_api.py

Requirements:
    - API server running on http://localhost:8000
    - requests library (pip install requests)
"""

import requests
import json
import time
import sys
from typing import Dict, Any


class FoodDeliveryAPIDemo:
    """Demo class for testing the Food Delivery API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the demo with API base URL."""
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'FoodDeliveryDemo/1.0'
        })
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🍕 {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{'-'*40}")
        print(f"📊 {title}")
        print(f"{'-'*40}")
    
    def make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict[str, Any]:
        """Make a request to the API and handle errors."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            print(f"🌐 {method.upper()} {endpoint}")
            print(f"📤 Status: {response.status_code}")
            
            if data:
                print("📋 Request Data:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Response:")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(json.dumps(error_data, indent=2, ensure_ascii=False))
                except:
                    print(response.text)
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error: Could not connect to {url}")
            print("💡 Make sure the API server is running:")
            print("   docker-compose up --build")
            print("   OR")
            print("   python -m uvicorn app.main:app --reload --port 8000")
            return None
        except Exception as e:
            print(f"❌ Unexpected Error: {e}")
            return None
    
    def test_health_check(self):
        """Test the health check endpoint."""
        self.print_section("Health Check")
        result = self.make_request('GET', '/health')
        return result is not None
    
    def test_api_info(self):
        """Test the root API information endpoint."""
        self.print_section("API Information")
        result = self.make_request('GET', '/')
        return result is not None
    
    def test_shipping_costs(self):
        """Test the shipping costs endpoint."""
        self.print_section("Colombian Shipping Costs by Stratum")
        result = self.make_request('GET', '/api/v1/orders/shipping-costs')
        
        if result and 'shipping_costs' in result:
            print("\n📋 Shipping Cost Analysis:")
            costs = result['shipping_costs']
            for stratum in range(1, 7):
                cost = costs.get(str(stratum), 'N/A')
                print(f"   Stratum {stratum}: {cost:,} COP")
        
        return result is not None
    
    def test_discount_tiers(self):
        """Test the discount tiers endpoint."""
        self.print_section("Available Discount Tiers")
        result = self.make_request('GET', '/api/v1/orders/discount-tiers')
        
        if result and 'discount_tiers' in result:
            print("\n📋 Discount Tier Analysis:")
            for tier in result['discount_tiers']:
                threshold = tier['threshold']
                percentage = tier['discount_percentage'] * 100
                print(f"   💰 {percentage:.0f}% discount for orders over {threshold:,.0f} COP")
        
        return result is not None
    
    def test_order_calculation_simple(self):
        """Test a simple order calculation."""
        self.print_section("Simple Order Calculation")
        
        order_data = {
            "products": [
                {
                    "name": "Pizza Margherita",
                    "price": 25000,
                    "quantity": 1
                }
            ],
            "stratum": 3,
            "delivery_address": "Carrera 7 #123-45, Bogotá"
        }
        
        result = self.make_request('POST', '/api/v1/orders/calculate', order_data)
        
        if result:
            print(f"\n📊 Order Summary:")
            print(f"   Subtotal: {result['subtotal']:,.0f} COP")
            print(f"   Shipping: {result['shipping_cost']:,.0f} COP (Stratum {order_data['stratum']})")
            print(f"   Discount: {result['discount_percentage']*100:.1f}% ({result['discount_amount']:,.0f} COP)")
            print(f"   💰 TOTAL: {result['total_cost']:,.0f} COP")
        
        return result is not None
    
    def test_order_with_discount(self):
        """Test an order that qualifies for discount."""
        self.print_section("Order with Discount (100K+ COP)")
        
        order_data = {
            "products": [
                {
                    "name": "Family Combo",
                    "price": 80000,
                    "quantity": 1
                },
                {
                    "name": "Extra Drinks",
                    "price": 25000,
                    "quantity": 1
                }
            ],
            "stratum": 4,
            "delivery_address": "Calle 80 #45-23, Medellín"
        }
        
        result = self.make_request('POST', '/api/v1/orders/calculate', order_data)
        
        if result:
            print(f"\n📊 Order Summary:")
            print(f"   Subtotal: {result['subtotal']:,.0f} COP")
            print(f"   Shipping: {result['shipping_cost']:,.0f} COP (Stratum {order_data['stratum']})")
            print(f"   🎉 Discount: {result['discount_percentage']*100:.0f}% ({result['discount_amount']:,.0f} COP)")
            print(f"   💰 TOTAL: {result['total_cost']:,.0f} COP")
            
            savings = result['subtotal'] + result['shipping_cost'] - result['total_cost']
            print(f"   💵 You saved: {savings:,.0f} COP!")
        
        return result is not None
    
    def test_maximum_discount(self):
        """Test an order that qualifies for maximum discount."""
        self.print_section("Maximum Discount Order (200K+ COP)")
        
        order_data = {
            "products": [
                {
                    "name": "Catering Package",
                    "price": 250000,
                    "quantity": 1
                }
            ],
            "stratum": 6,  # Highest stratum
            "delivery_address": "Zona Rosa, Bogotá"
        }
        
        result = self.make_request('POST', '/api/v1/orders/calculate', order_data)
        
        if result:
            print(f"\n📊 Order Summary:")
            print(f"   Subtotal: {result['subtotal']:,.0f} COP")
            print(f"   Shipping: {result['shipping_cost']:,.0f} COP (Premium Stratum {order_data['stratum']})")
            print(f"   🎉 MAX Discount: {result['discount_percentage']*100:.0f}% ({result['discount_amount']:,.0f} COP)")
            print(f"   💰 TOTAL: {result['total_cost']:,.0f} COP")
            
            savings = result['subtotal'] + result['shipping_cost'] - result['total_cost']
            print(f"   💵 You saved: {savings:,.0f} COP!")
        
        return result is not None
    
    def test_all_strata(self):
        """Test order calculation for all Colombian strata."""
        self.print_section("Colombian Strata Comparison")
        
        base_order = {
            "products": [
                {
                    "name": "Standard Meal",
                    "price": 20000,
                    "quantity": 1
                }
            ],
            "delivery_address": "Test Address"
        }
        
        print("📊 Shipping costs by socioeconomic stratum:")
        for stratum in range(1, 7):
            order_data = {**base_order, "stratum": stratum}
            result = self.make_request('POST', '/api/v1/orders/calculate', order_data)
            
            if result:
                shipping = result['shipping_cost']
                total = result['total_cost']
                print(f"   Stratum {stratum}: {shipping:,.0f} COP shipping → {total:,.0f} COP total")
            
            time.sleep(0.1)  # Small delay to be nice to the server
    
    def test_error_handling(self):
        """Test error handling with invalid data."""
        self.print_section("Error Handling Tests")
        
        # Test invalid stratum
        print("🧪 Testing invalid stratum (should fail):")
        invalid_order = {
            "products": [{"name": "Test", "price": 10000, "quantity": 1}],
            "stratum": 7  # Invalid stratum
        }
        self.make_request('POST', '/api/v1/orders/calculate', invalid_order)
        
        time.sleep(0.5)
        
        # Test negative price
        print("\n🧪 Testing negative price (should fail):")
        invalid_order = {
            "products": [{"name": "Test", "price": -1000, "quantity": 1}],
            "stratum": 3
        }
        self.make_request('POST', '/api/v1/orders/calculate', invalid_order)
        
        time.sleep(0.5)
        
        # Test empty products
        print("\n🧪 Testing empty products (should fail):")
        invalid_order = {
            "products": [],
            "stratum": 3
        }
        self.make_request('POST', '/api/v1/orders/calculate', invalid_order)
    
    def run_complete_demo(self):
        """Run the complete API demonstration."""
        self.print_header("Food Delivery API Demonstration")
        print("🚀 Testing all endpoints and scenarios...")
        print(f"🌐 API Base URL: {self.base_url}")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Information", self.test_api_info),
            ("Shipping Costs", self.test_shipping_costs),
            ("Discount Tiers", self.test_discount_tiers),
            ("Simple Order", self.test_order_calculation_simple),
            ("Order with Discount", self.test_order_with_discount),
            ("Maximum Discount", self.test_maximum_discount),
            ("All Strata Comparison", self.test_all_strata),
            ("Error Handling", self.test_error_handling),
        ]
        
        results = []
        for test_name, test_func in tests:
            try:
                success = test_func()
                results.append((test_name, success))
                if success:
                    print("✅ Test completed successfully")
                else:
                    print("❌ Test failed")
            except Exception as e:
                print(f"💥 Test crashed: {e}")
                results.append((test_name, False))
            
            time.sleep(1)  # Pause between tests
        
        # Summary
        self.print_header("Demo Summary")
        successful = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"📊 Results: {successful}/{total} tests successful")
        
        for test_name, success in results:
            status = "✅" if success else "❌"
            print(f"   {status} {test_name}")
        
        if successful == total:
            print("\n🎉 All tests passed! The Food Delivery API is working perfectly.")
            print("\n📚 Next steps:")
            print("   • Visit http://localhost:8000/docs for interactive API documentation")
            print("   • Try the API with your own data using curl or Postman")
            print("   • Run the test suite: docker-compose exec api python -m pytest tests/ -v")
        else:
            print(f"\n⚠️  {total - successful} tests failed. Check the API server and try again.")
        
        return successful == total


def main():
    """Main function to run the demo."""
    print("🍕 Food Delivery API Demo")
    print("=" * 40)
    
    # Check for custom URL
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        print(f"Using custom API URL: {base_url}")
    
    # Run the demo
    demo = FoodDeliveryAPIDemo(base_url)
    success = demo.run_complete_demo()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
