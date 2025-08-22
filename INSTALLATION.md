# Installation Guide

## Prerequisites

This project requires Python 3.8+ (recommended Python 3.12) and pip for dependency management.

## Installation Options

### Option 1: Full Installation with FastAPI

If you have Python 3.8+ and want to run the complete API:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Visit the API documentation
open http://localhost:8000/docs
```

### Option 2: Algorithm Demonstrations Only

If you only want to run the algorithm demonstrations (requires only standard Python libraries):

```bash
# Run algorithm demonstrations
python algorithms/frequent_customers.py
python algorithms/transport_routes.py
python system_design/distributed_architecture.py
```

### Option 3: Docker Deployment

```bash
# Build the Docker image
docker build -t jikkosott .

# Run the container
docker run -p 8000:8000 jikkosott

# Visit the API
open http://localhost:8000/docs
```

## Testing

### With pytest (requires dependencies)
```bash
pip install -r requirements.txt
pytest tests/ -v
```

### Manual testing (no dependencies required)
```bash
# Test core business logic
python -c "
from decimal import Decimal
subtotal = Decimal('25000') * 2 + Decimal('3000') * 1
print(f'Order total test: {subtotal} COP')
"
```

## Verification

To verify the installation is working correctly:

1. **Algorithm Tests**: Run `python algorithms/frequent_customers.py`
2. **API Tests**: Run `python -c "from app.main import app; print('Success')"`
3. **Business Logic**: Test order calculations manually

## Dependencies

### Core Dependencies (FastAPI)
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- pydantic==2.5.0

### Testing Dependencies
- pytest==7.4.3
- pytest-asyncio==0.21.1
- httpx==0.25.2

### Optional Dependencies
- python-multipart==0.0.6 (for form data)

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError for FastAPI**
   - Solution: Run `pip install fastapi uvicorn`

2. **Python version too old**
   - Solution: Use Python 3.8+ or run algorithm demos only

3. **Permission errors**
   - Solution: Use `pip install --user` or virtual environment

### Environment Setup

For a clean installation:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Linux/Mac)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Minimum Requirements

- **For Algorithms Only**: Python 3.6+ (standard library only)
- **For Full API**: Python 3.8+, pip, 100MB disk space
- **For Production**: Python 3.12+, Docker, Kubernetes (optional)

## Quick Start

The fastest way to see the project working:

```bash
# Just run the algorithms (no dependencies)
python3 algorithms/transport_routes.py

# This should output the transport system demonstration
```
