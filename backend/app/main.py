from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from app.config import settings
from app.routers import (
    health_router,
    departments_router,
    users_router,
    complaints_router,
    assignments_router,
    status_router,
    notifications_router,
    feedback_router,
)


# Initialize FastAPI app with descriptive metadata for Swagger/ReDoc docs
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    Backend REST API server for the **Smart Civic Platform** (Final Year Project).
    
    This backend manages civic complaints registration, routing to government departments,
    officer assignment workflows, and citizen feedback.
    """,
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware to support API consumers (Expo React Native and Admin dashboards)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API routers directly under the root to match exact route requirements
app.include_router(health_router)
app.include_router(departments_router)
app.include_router(users_router)
app.include_router(complaints_router)
app.include_router(assignments_router)
app.include_router(status_router)
app.include_router(notifications_router)
app.include_router(feedback_router)


# Custom handler for FastAPI HTTPExceptions to wrap them in standard envelope
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": None
        }
    )

# Custom handler for input validation errors (e.g. invalid type, missing field)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        # Clean up locations e.g. body -> email
        loc = " -> ".join(str(l) for l in err["loc"][1:]) if len(err["loc"]) > 1 else str(err["loc"][0])
        errors.append(f"[{loc}]: {err['msg']}")
    
    combined_message = "Validation failed: " + "; ".join(errors)
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": combined_message,
            "data": None
        }
    )

# Custom handler for any unhandled application exceptions
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": f"Internal Server Error: {str(exc)}",
            "data": None
        }
    )

@app.get("/")
def read_root():
    return {
        "success": True,
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "data": {
            "docs": "/docs",
            "health": "/health",
            "departments": "/departments",
            "users": "/users"
        }
    }
