from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.schemas.response import StandardResponse
from app.services import department_service

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=StandardResponse[DepartmentResponse], status_code=status.HTTP_201_CREATED)
def create_department(dept_in: DepartmentCreate, db: Session = Depends(get_db)):
    """
    Create a new department. Fails if name already exists.
    """
    existing = department_service.get_department_by_name(db, dept_in.department_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department with name '{dept_in.department_name}' already exists."
        )
    db_dept = department_service.create_department(db, dept_in)
    return StandardResponse(
        success=True,
        message="Department created successfully.",
        data=db_dept
    )

@router.get("", response_model=StandardResponse[List[DepartmentResponse]])
def get_departments(db: Session = Depends(get_db)):
    """
    List all departments.
    """
    depts = department_service.get_departments(db)
    return StandardResponse(
        success=True,
        message="Departments retrieved successfully.",
        data=depts
    )

@router.get("/{id}", response_model=StandardResponse[DepartmentResponse])
def get_department(id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific department by ID.
    """
    db_dept = department_service.get_department_by_id(db, id)
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {id} not found."
        )
    return StandardResponse(
        success=True,
        message="Department retrieved successfully.",
        data=db_dept
    )

@router.put("/{id}", response_model=StandardResponse[DepartmentResponse])
def update_department(id: int, dept_in: DepartmentUpdate, db: Session = Depends(get_db)):
    """
    Update department name or description.
    """
    db_dept = department_service.get_department_by_id(db, id)
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {id} not found."
        )
    if dept_in.department_name:
        existing = department_service.get_department_by_name(db, dept_in.department_name)
        if existing and existing.department_id != id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Department with name '{dept_in.department_name}' already exists."
            )
    updated_dept = department_service.update_department(db, db_dept, dept_in)
    return StandardResponse(
        success=True,
        message="Department updated successfully.",
        data=updated_dept
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_department(id: int, db: Session = Depends(get_db)):
    """
    Delete a specific department by ID.
    """
    db_dept = department_service.get_department_by_id(db, id)
    if not db_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Department with ID {id} not found."
        )
    department_service.delete_department(db, db_dept)
    return StandardResponse(
        success=True,
        message="Department deleted successfully.",
        data={}
    )
