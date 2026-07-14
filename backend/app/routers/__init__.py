from app.routers.health import router as health_router
from app.routers.departments import router as departments_router
from app.routers.users import router as users_router
from app.routers.complaints import router as complaints_router
from app.routers.assignments import router as assignments_router
from app.routers.status import router as status_router
from app.routers.notifications import router as notifications_router
from app.routers.feedback import router as feedback_router

__all__ = [
    "health_router",
    "departments_router",
    "users_router",
    "complaints_router",
    "assignments_router",
    "status_router",
    "notifications_router",
    "feedback_router",
]
