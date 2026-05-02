"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    """Task status"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    MEMBER = "member"


# ===================== USER SCHEMAS =====================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=72)
    role: Optional[UserRole] = UserRole.MEMBER

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, v):
        """
        Accept any casing (admin / Admin / ADMIN) and map it to the correct
        UserRole enum value.  Unknown / missing values fall back to MEMBER so
        the endpoint never silently creates an account with a broken role.
        """
        if v is None:
            return UserRole.MEMBER
        if isinstance(v, UserRole):
            return v
        normalized = str(v).strip().lower()
        if normalized == "admin":
            return UserRole.ADMIN
        if normalized == "member":
            return UserRole.MEMBER
        # Unknown value → safe default instead of a 422 that confuses callers
        return UserRole.MEMBER


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """Detailed user response"""
    projects: List['ProjectResponse'] = []
    assigned_tasks: List['TaskResponse'] = []


# ===================== PROJECT SCHEMAS =====================

class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectCreate(ProjectBase):
    """Project creation schema"""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema"""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Project response schema"""
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response"""
    creator: UserResponse
    members: List[UserResponse] = []
    tasks: List['TaskResponse'] = []


class ProjectMemberAdd(BaseModel):
    """Add member to project schema"""
    user_id: int
    role: UserRole = UserRole.MEMBER


class ProjectMemberRemove(BaseModel):
    """Remove member from project schema"""
    user_id: int


# ===================== TASK SCHEMAS =====================

class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """Task creation schema"""
    project_id: int
    assigned_to: Optional[int] = None
    # Accept either `assigned_to` or `assigned_to_id` from clients
    assigned_to_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Task update schema"""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[int] = None
    assigned_to_id: Optional[int] = None


class TaskResponse(TaskBase):
    """Task response schema"""
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
    """Detailed task response"""
    project: ProjectResponse
    assigned_user: Optional[UserResponse] = None


# ===================== AUTH SCHEMAS =====================

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Token refresh schema"""
    refresh_token: str


# ===================== DASHBOARD SCHEMAS =====================

class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    overdue_tasks: int
    total_projects: int
    tasks_by_priority: dict
    tasks_by_status: dict


# ===================== PAGINATION =====================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Paginated response"""
    items: List
    total: int
    page: int
    per_page: int
    total_pages: int


# Update forward references
UserDetailResponse.model_rebuild()
ProjectResponse.model_rebuild()
ProjectDetailResponse.model_rebuild()
TaskResponse.model_rebuild()
TaskDetailResponse.model_rebuild()