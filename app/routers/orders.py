"""
Order management API endpoints.

This module provides RESTful API endpoints for processing food delivery orders,
including calculation of totals, shipping costs, and discounts based on
Colombian socioeconomic considerations.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.orders import OrderRequest, OrderResponse
from app.services.order_service import OrderService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["orders"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)

# Initialize order service
order_service = OrderService()


@router.post("/calculate", response_model=OrderResponse, status_code=status.HTTP_200_OK)
async def calculate_order_total(order_request: OrderRequest) -> OrderResponse:
    """
    Calculate the total cost of an order including shipping and applicable discounts.
    
    This endpoint processes a food delivery order by:
    1. Calculating the subtotal from products and quantities
    2. Determining shipping cost based on Colombian socioeconomic stratum
    3. Applying discounts based on order value thresholds
    4. Returning the complete cost breakdown
    
    Args:
        order_request: Order details including products, quantities, and customer stratum
        
    Returns:
        OrderResponse: Complete order calculation with breakdown
        
    Raises:
        HTTPException: If validation fails or processing error occurs
        
    Example:
        ```json
        {
            "products": [
                {
                    "name": "Pizza Margherita",
                    "price": 25000,
                    "quantity": 2
                },
                {
                    "name": "Coca Cola",
                    "price": 3000,
                    "quantity": 1
                }
            ],
            "stratum": 3,
            "delivery_address": "Carrera 7 #123-45, Bogotá"
        }
        ```
    """
    try:
        logger.info("Processing order with %d products for stratum %d", len(order_request.products), order_request.stratum)
        
        # Process the order using the service
        calculation_result = order_service.process_order(order_request)
        
        # Create and return response
        response = OrderResponse(**calculation_result)
        
        logger.info("Order processed successfully. Total: %s", response.total_cost)
        return response
        
    except ValueError as e:
        logger.error("Validation error processing order: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid order data: {str(e)}"
        ) from e
    except Exception as e:
        logger.error("Unexpected error processing order: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the order"
        ) from e


@router.get("/shipping-costs", status_code=status.HTTP_200_OK)
async def get_shipping_costs():
    """
    Get shipping costs for all Colombian socioeconomic strata.
    
    Returns:
        dict: Mapping of stratum levels to shipping costs in Colombian Pesos
        
    Example response:
        ```json
        {
            "shipping_costs": {
                "1": 2000,
                "2": 3000,
                "3": 5000,
                "4": 6000,
                "5": 8000,
                "6": 10000
            },
            "currency": "COP"
        }
        ```
    """
    try:
        shipping_costs = {
            str(stratum.value): float(cost) 
            for stratum, cost in order_service.SHIPPING_COSTS.items()
        }
        
        return {
            "shipping_costs": shipping_costs,
            "currency": "COP",
            "description": "Shipping costs by Colombian socioeconomic stratum"
        }
    except Exception as e:
        logger.error("Error retrieving shipping costs: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving shipping costs"
        ) from e


@router.get("/discount-tiers", status_code=status.HTTP_200_OK)
async def get_discount_tiers():
    """
    Get available discount tiers based on order value.
    
    Returns:
        dict: Discount tiers with thresholds and percentages
        
    Example response:
        ```json
        {
            "discount_tiers": [
                {
                    "threshold": 200000,
                    "discount_percentage": 0.15,
                    "description": "15% discount for orders over 200,000 COP"
                }
            ],
            "currency": "COP"
        }
        ```
    """
    try:
        discount_tiers = [
            {
                "threshold": float(threshold),
                "discount_percentage": float(percentage),
                "description": f"{float(percentage)*100:.0f}% discount for orders over {float(threshold):,.0f} COP"
            }
            for threshold, percentage in order_service.DISCOUNT_TIERS
        ]
        
        return {
            "discount_tiers": discount_tiers,
            "currency": "COP"
        }
    except Exception as e:
        logger.error("Error retrieving discount tiers: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving discount tiers"
        ) from e
