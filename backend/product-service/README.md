# Products Service

FastAPI-based Products CRUD service with PostgreSQL.

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+

### Installation
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment: `cp .env.example .env`
6. Update `.env` with your database credentials
7. Run: `uvicorn app.main:app --reload`

### API Documentation
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## Project Structure
