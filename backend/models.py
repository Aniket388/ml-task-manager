from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RoleEnum(str, Enum):
    Admin = "Admin"
    Member = "Member"


class TaskStatusEnum(str, Enum):
    Todo = "Todo"
    InProgress = "InProgress"
    Done = "Done"


class PriorityEnum(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: RoleEnum = RoleEnum.Member


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: str
    name: str
    email: EmailStr
    role: RoleEnum


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: Optional[str] = Field(default="", max_length=1000)


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)


class ProjectOut(BaseModel):
    id: str
    name: str
    description: str
    owner_id: str
    created_at: datetime


class TaskCreate(BaseModel):
    project_id: str
    title: str = Field(min_length=2, max_length=150)
    description: str = Field(default="", max_length=2000)
    status: TaskStatusEnum = TaskStatusEnum.Todo
    priority: PriorityEnum = PriorityEnum.Medium


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=150)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None


class TaskOut(BaseModel):
    id: str
    project_id: str
    title: str
    description: str
    status: TaskStatusEnum
    priority: PriorityEnum
    created_by: str
    created_at: datetime


class PriorityPredictionRequest(BaseModel):
    description: str = Field(min_length=2, max_length=2000)


class PriorityPredictionResponse(BaseModel):
    priority: PriorityEnum
