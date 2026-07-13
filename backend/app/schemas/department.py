from pydantic import BaseModel, ConfigDict

class DepartmentBase(BaseModel):
    department_name: str
    description: str | None = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    department_name: str | None = None
    description: str | None = None

class DepartmentResponse(DepartmentBase):
    department_id: int

    model_config = ConfigDict(from_attributes=True)
