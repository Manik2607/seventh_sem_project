from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password, verify_password

def get_users(db: Session):
    """
    Get all registered users.
    """
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    """
    Get user by unique ID.
    """
    return db.query(User).filter(User.user_id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """
    Get user by email address (case-insensitive search).
    """
    return db.query(User).filter(User.email == email.lower().strip()).first()

def register_user(db: Session, user_in: UserCreate):
    """
    Register and hash password for a new user.
    """
    db_user = User(
        email=user_in.email.lower().strip(),
        password=hash_password(user_in.password),
        name=user_in.name,
        phone=user_in.phone,
        role=user_in.role,  # UserRoleEnum
        department_id=user_in.department_id
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user by checking email and hashing password.
    """
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user

def update_user(db: Session, db_user: User, user_in: UserUpdate):
    """
    Update details of an existing user.
    """
    if user_in.email is not None:
        db_user.email = user_in.email.lower().strip()
    if user_in.name is not None:
        db_user.name = user_in.name
    if user_in.phone is not None:
        db_user.phone = user_in.phone
    if user_in.role is not None:
        db_user.role = user_in.role
    if user_in.department_id is not None:
        db_user.department_id = user_in.department_id
    if user_in.password is not None:
        db_user.password = hash_password(user_in.password)
        
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    """
    Delete a user from the system.
    """
    db.delete(db_user)
    db.commit()
    return True
