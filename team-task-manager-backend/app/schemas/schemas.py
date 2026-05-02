"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


# ===================== USER SCHEMAS =====================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema.

    The ``role`` field accepts any casing ("admin", "Admin", "ADMIN") and
    normalises it to the lowercase canonical value before validation.
    Unknown values silently fall back to "member" so the endpoint never
    crashes on a bad client payload.
    """
    password: str = Field(..., min_length=8, max_length=72)
    role: Optional[UserRole] = UserRole.MEMBER

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        """Accept any casing; map to lowercase canonical value or fall back."""
        if v is None:
            return UserRole.MEMBER
        if isinstance(v, UserRole):
            return v
        cleaned = str(v).strip().lower()
        if cleaned == "admin":
            return UserRole.ADMIN
        if cleaned == "member":
            return UserRole.MEMBER
        return UserRole.MEMBER


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    projects: List['ProjectResponse'] = []
    assigned_tasks: List['TaskResponse'] = []


# ===================== PROJECT SCHEMAS =====================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    creator: UserResponse
    members: List[UserResponse] = []
    tasks: List['TaskResponse'] = []


class ProjectMemberAdd(BaseModel):
    user_id: int
    role: UserRole = UserRole.MEMBER


class ProjectMemberRemove(BaseModel):
    user_id: int


# ===================== TASK SCHEMAS =====================

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    project_id: int
    assigned_to: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    assigned_to: Optional[int] = None
    assigned_user_name: Optional[str] = None
    assigned_to_id: Optional[int] = None
    status: TaskStatus
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskDetailResponse(TaskResponse):
    project: ProjectResponse
    assigned_user: Optional[UserResponse] = None


# ===================== AUTH SCHEMAS =====================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    refresh_token: str


# ===================== DASHBOARD SCHEMAS =====================

class DashboardStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    total_projects: int
    tasks_by_priority: dict
    tasks_by_status: dict


# ===================== PAGINATION =====================

class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    items: List
    total: int
    page: int
    per_page: int
    total_pages: int


# Forward-reference resolution
UserDetailResponse.model_rebuild()
ProjectResponse.model_rebuild()
ProjectDetailResponse.model_rebuild()
TaskResponse.model_rebuild()
TaskDetailResponse.model_rebuild()