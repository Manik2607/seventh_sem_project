from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserLogin, UserResponse
from app.schemas.response import StandardResponse
from app.services import user_service, department_service
from app.models.user import UserRoleEnum

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=StandardResponse[UserResponse], status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user. Performs checks for duplicate email, role, and department viability.
    """
    # Check duplicate email
    existing_user = user_service.get_user_by_email(db, user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_in.email}' is already registered."
        )
    
    # Check department
    if user_in.department_id is not None:
        db_dept = department_service.get_department_by_id(db, user_in.department_id)
        if not db_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {user_in.department_id} does not exist."
            )
            
    db_user = user_service.register_user(db, user_in)
    return StandardResponse(
        success=True,
        message="User registered successfully.",
        data=db_user
    )

@router.post("/login", response_model=StandardResponse[UserResponse])
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user via email and password (no JWT token is generated).
    """
    user = user_service.authenticate_user(db, login_in.email, login_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    return StandardResponse(
        success=True,
        message="Login successful.",
        data=user
    )

@router.get("", response_model=StandardResponse[List[UserResponse]])
def get_users(db: Session = Depends(get_db)):
    """
    List all registered users.
    """
    users = user_service.get_users(db)
    return StandardResponse(
        success=True,
        message="Users retrieved successfully.",
        data=users
    )

@router.get("/{id}", response_model=StandardResponse[UserResponse])
def get_user(id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific user by ID.
    """
    db_user = user_service.get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )
    return StandardResponse(
        success=True,
        message="User details retrieved successfully.",
        data=db_user
    )

@router.put("/{id}", response_model=StandardResponse[UserResponse])
def update_user(id: int, user_in: UserUpdate, db: Session = Depends(get_db)):
    """
    Update profile or credentials of a user.
    """
    db_user = user_service.get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )
        
    if user_in.email:
        existing = user_service.get_user_by_email(db, user_in.email)
        if existing and existing.user_id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email '{user_in.email}' is already registered."
            )
            
    if user_in.department_id is not None:
        db_dept = department_service.get_department_by_id(db, user_in.department_id)
        if not db_dept:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with ID {user_in.department_id} does not exist."
            )
            
    updated_user = user_service.update_user(db, db_user, user_in)
    return StandardResponse(
        success=True,
        message="User updated successfully.",
        data=updated_user
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_user(id: int, db: Session = Depends(get_db)):
    """
    Delete a user by ID.
    """
    db_user = user_service.get_user_by_id(db, id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {id} not found."
        )
    user_service.delete_user(db, db_user)
    return StandardResponse(
        success=True,
        message="User deleted successfully.",
        data={}
    )
