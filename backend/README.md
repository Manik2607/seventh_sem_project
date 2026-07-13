# Smart Civic Platform - Backend API

This is the FastAPI backend repository for the **Smart Civic Platform**, a Final Year Project designed to connect citizens with local government departments to report and track civic complaints.

## Tech Stack
- **Python 3.12+**
- **FastAPI**: Modern, high-performance web framework.
- **SQLAlchemy 2.0**: Object-relational mapping using modern type annotations (`Mapped`, `mapped_column`).
- **Pydantic v2**: High-performance data validation.
- **PostgreSQL**: Hosted on Supabase.
- **Uvicorn**: Asynchronous application server.

## Clean Architecture Directory Structure
The project is organized using clean architecture principles to isolate concerns:
```
backend/
├── app/
│   ├── main.py          # FastAPI application initialization & routes registration
│   ├── config.py        # Environmental configuration settings using pydantic-settings
│   ├── database.py      # SQLAlchemy engine, session maker, base model, and DB dependency
│   ├── models/          # SQLAlchemy database models defining the schema
│   ├── schemas/         # Pydantic schemas for request validation & serialization
│   ├── routers/         # API path controllers / router modules
│   ├── services/        # Core business logic / workflows (to be implemented)
│   ├── utils/           # Shared utility functions and helpers (to be implemented)
│   └── constants/       # Global constants like UserRoles
├── .env                 # Local environment configuration file
├── requirements.txt     # Python packages list
└── README.md            # Setup and execution guide
```

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3.12+ installed.

### 2. Set Up Virtual Environment
Create and activate a python virtual environment:

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
Install packages listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory (already preconfigured for localhost) and update the `DATABASE_URL` with your Supabase PostgreSQL connection string:

```ini
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres"
PROJECT_NAME="Smart Civic Platform API"
API_V1_STR="/api/v1"
```

## Running the Application

To run the server locally with reload enabled:

```bash
uvicorn app.main:app --reload
```

- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
