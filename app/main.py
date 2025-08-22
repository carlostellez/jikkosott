"""
FastAPI application for food delivery order processing.

This application provides RESTful APIs for processing food delivery orders
with Colombian market considerations including socioeconomic stratum-based
shipping costs and order value-based discounts.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from app.routers import orders

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Food Delivery Order API",
    description="""
    A comprehensive API for processing food delivery orders with Colombian market considerations.
    
    ## Features
    
    * **Order Processing**: Calculate total costs including products, shipping, and discounts
    * **Colombian Stratum Support**: Shipping costs based on socioeconomic stratum (1-6)
    * **Dynamic Discounts**: Automatic discounts based on order value thresholds
    * **Comprehensive Validation**: Input validation with detailed error responses
    * **RESTful Design**: Clean, intuitive API endpoints following REST principles
    
    ## Socioeconomic Stratum
    
    Colombian socioeconomic classification affects shipping costs:
    - **Stratum 1-2**: Lower income levels (subsidized shipping)
    - **Stratum 3-4**: Middle income levels (standard shipping)
    - **Stratum 5-6**: Higher income levels (premium shipping)
    
    ## Discount Tiers
    
    Automatic discounts based on order subtotal:
    - **5%**: Orders over 50,000 COP
    - **10%**: Orders over 100,000 COP  
    - **15%**: Orders over 200,000 COP
    """,
    version="1.0.0",
    contact={
        "name": "Tech Lead Assessment",
        "email": "contact@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.exception_handler(404)
async def not_found_handler(request: Request, _exc):
    """Custom 404 error handler."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "message": f"The requested resource {request.url.path} was not found",
            "status_code": 404
        }
    )


@app.exception_handler(500)
async def internal_server_error_handler(_request: Request, exc):
    """Custom 500 error handler."""
    logger.error("Internal server error: %s", str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred while processing your request",
            "status_code": 500
        }
    )


# Include routers
app.include_router(orders.router)


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint providing API information and health check.
    
    Returns:
        dict: API information and status
    """
    return {
        "message": "Food Delivery Order Processing API",
        "version": "1.0.0",
        "status": "healthy",
        "documentation": "/docs",
        "endpoints": {
            "calculate_order": "/api/v1/orders/calculate",
            "shipping_costs": "/api/v1/orders/shipping-costs",
            "discount_tiers": "/api/v1/orders/discount-tiers"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "food-delivery-api",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
