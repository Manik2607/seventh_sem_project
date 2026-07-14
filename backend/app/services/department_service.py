from sqlalchemy.orm import Session
from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate

def get_departments(db: Session):
    """
    Get list of all departments.
    """
    return db.query(Department).all()

def get_department_by_id(db: Session, department_id: int):
    """
    Get a single department by ID.
    """
    return db.query(Department).filter(Department.department_id == department_id).first()

def get_department_by_name(db: Session, department_name: str):
    """
    Get a single department by name (used for validation).
    """
    return db.query(Department).filter(Department.department_name == department_name).first()

def create_department(db: Session, dept_in: DepartmentCreate):
    """
    Create a new department.
    """
    db_dept = Department(
        department_name=dept_in.department_name,
        description=dept_in.description
    )
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept

def update_department(db: Session, db_dept: Department, dept_in: DepartmentUpdate):
    """
    Update an existing department.
    """
    if dept_in.department_name is not None:
        db_dept.department_name = dept_in.department_name
    if dept_in.description is not None:
        db_dept.description = dept_in.description
    db.commit()
    db.refresh(db_dept)
    return db_dept

def delete_department(db: Session, db_dept: Department):
    """
    Delete a department.
    """
    db.delete(db_dept)
    db.commit()
    return True
