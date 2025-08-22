"""
Order-related data models for the food delivery API.

This module defines Pydantic models for handling order requests and responses,
including product information, pricing calculations, and Colombian socioeconomic
stratum considerations.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from enum import IntEnum


class SocioeconomicStratum(IntEnum):
    """
    Colombian socioeconomic stratum classification.
    
    Stratum 1-6 represent different socioeconomic levels where:
    - Stratum 1-2: Lower income levels
    - Stratum 3-4: Middle income levels  
    - Stratum 5-6: Higher income levels
    """
    STRATUM_1 = 1
    STRATUM_2 = 2
    STRATUM_3 = 3
    STRATUM_4 = 4
    STRATUM_5 = 5
    STRATUM_6 = 6


class Product(BaseModel):
    """
    Represents a product in an order.
    
    Attributes:
        name: Product name
        price: Unit price of the product
        quantity: Number of units ordered
    """
    name: str = Field(..., description="Product name", min_length=1)
    price: Decimal = Field(..., description="Unit price", gt=0)
    quantity: int = Field(..., description="Quantity ordered", gt=0)
    
    @validator('price', pre=True)
    @classmethod
    def validate_price(cls, v):
        """Ensure price is a valid decimal with at most 2 decimal places."""
        if isinstance(v, (int, float)):
            return Decimal(str(v)).quantize(Decimal('0.01'))
        return Decimal(str(v)).quantize(Decimal('0.01'))


class OrderRequest(BaseModel):
    """
    Request model for order processing.
    
    Attributes:
        products: List of products in the order
        stratum: Colombian socioeconomic stratum (affects shipping cost)
        delivery_address: Delivery address for distance calculation
    """
    products: List[Product] = Field(..., description="List of products", min_items=1)
    stratum: SocioeconomicStratum = Field(..., description="Colombian socioeconomic stratum")
    delivery_address: Optional[str] = Field(None, description="Delivery address")
    
    @validator('products')
    @classmethod
    def validate_products_not_empty(cls, v):
        """Ensure products list is not empty."""
        if not v:
            raise ValueError("Products list cannot be empty")
        return v


class OrderResponse(BaseModel):
    """
    Response model for processed orders.
    
    Attributes:
        subtotal: Total cost of products before shipping and discounts
        shipping_cost: Cost of delivery
        discount_percentage: Percentage discount applied
        discount_amount: Monetary amount of discount
        total_cost: Final total cost after shipping and discounts
        breakdown: Detailed breakdown of the calculation
    """
    subtotal: Decimal = Field(..., description="Subtotal before shipping and discounts")
    shipping_cost: Decimal = Field(..., description="Delivery cost")
    discount_percentage: Decimal = Field(..., description="Discount percentage applied")
    discount_amount: Decimal = Field(..., description="Discount amount")
    total_cost: Decimal = Field(..., description="Final total cost")
    breakdown: dict = Field(..., description="Detailed calculation breakdown")
    
    class Config:
        json_encoders = {
            Decimal: float
        }
