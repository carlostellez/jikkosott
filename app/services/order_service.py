"""
Order processing service with business logic for calculating totals, shipping, and discounts.

This service handles the core business logic for processing orders including:
- Subtotal calculation
- Shipping cost calculation based on Colombian socioeconomic stratum
- Discount application based on order value
- Final total calculation
"""

from decimal import Decimal
from typing import Dict, Any
from app.models.orders import OrderRequest, SocioeconomicStratum


class OrderService:
    """
    Service class for processing orders and calculating costs.
    
    This class encapsulates the business logic for order processing,
    including Colombian-specific considerations like socioeconomic stratum
    affecting shipping costs.
    """
    
    # Shipping costs based on Colombian socioeconomic stratum
    SHIPPING_COSTS = {
        SocioeconomicStratum.STRATUM_1: Decimal('2000'),  # Subsidized shipping
        SocioeconomicStratum.STRATUM_2: Decimal('3000'),  # Reduced shipping
        SocioeconomicStratum.STRATUM_3: Decimal('5000'),  # Standard shipping
        SocioeconomicStratum.STRATUM_4: Decimal('6000'),  # Standard shipping
        SocioeconomicStratum.STRATUM_5: Decimal('8000'),  # Premium shipping
        SocioeconomicStratum.STRATUM_6: Decimal('10000'), # Premium shipping
    }
    
    # Discount tiers based on order value (Colombian Pesos)
    DISCOUNT_TIERS = [
        (Decimal('200000'), Decimal('0.15')),  # 15% discount for orders over 200,000 COP
        (Decimal('100000'), Decimal('0.10')),  # 10% discount for orders over 100,000 COP
        (Decimal('50000'), Decimal('0.05')),   # 5% discount for orders over 50,000 COP
    ]
    
    def calculate_subtotal(self, order_request: OrderRequest) -> Decimal:
        """
        Calculate the subtotal of all products in the order.
        
        Args:
            order_request: The order request containing products
            
        Returns:
            Decimal: The subtotal amount
        """
        subtotal = Decimal('0')
        for product in order_request.products:
            subtotal += product.price * product.quantity
        return subtotal.quantize(Decimal('0.01'))
    
    def calculate_shipping_cost(self, stratum: SocioeconomicStratum) -> Decimal:
        """
        Calculate shipping cost based on Colombian socioeconomic stratum.
        
        Args:
            stratum: The socioeconomic stratum of the customer
            
        Returns:
            Decimal: The shipping cost
        """
        return self.SHIPPING_COSTS.get(stratum, self.SHIPPING_COSTS[SocioeconomicStratum.STRATUM_3])
    
    def calculate_discount(self, subtotal: Decimal) -> tuple[Decimal, Decimal]:
        """
        Calculate discount percentage and amount based on order value.
        
        Args:
            subtotal: The subtotal amount before shipping
            
        Returns:
            tuple: (discount_percentage, discount_amount)
        """
        for threshold, percentage in self.DISCOUNT_TIERS:
            if subtotal >= threshold:
                discount_amount = (subtotal * percentage).quantize(Decimal('0.01'))
                return percentage, discount_amount
        
        return Decimal('0'), Decimal('0')
    
    def process_order(self, order_request: OrderRequest) -> Dict[str, Any]:
        """
        Process a complete order and calculate all costs.
        
        Args:
            order_request: The order request to process
            
        Returns:
            Dict: Complete order calculation breakdown
        """
        # Calculate subtotal
        subtotal = self.calculate_subtotal(order_request)
        
        # Calculate shipping cost
        shipping_cost = self.calculate_shipping_cost(order_request.stratum)
        
        # Calculate discount
        discount_percentage, discount_amount = self.calculate_discount(subtotal)
        
        # Calculate total cost
        total_before_discount = subtotal + shipping_cost
        total_cost = (total_before_discount - discount_amount).quantize(Decimal('0.01'))
        
        # Create detailed breakdown
        breakdown = {
            "products": [
                {
                    "name": product.name,
                    "price": float(product.price),
                    "quantity": product.quantity,
                    "total": float(product.price * product.quantity)
                }
                for product in order_request.products
            ],
            "subtotal": float(subtotal),
            "shipping_cost": float(shipping_cost),
            "stratum": order_request.stratum.value,
            "discount_applied": float(discount_percentage) > 0,
            "discount_threshold_met": float(subtotal),
            "total_before_discount": float(total_before_discount),
            "final_total": float(total_cost)
        }
        
        return {
            "subtotal": subtotal,
            "shipping_cost": shipping_cost,
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "total_cost": total_cost,
            "breakdown": breakdown
        }
