from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriorityEnum, TaskStatusEnum


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatusEnum = TaskStatusEnum.TODO
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    assignee_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    status: TaskStatusEnum | None = None
    priority: TaskPriorityEnum | None = None
    due_date: datetime | None = None
    assignee_id: int | None = None


class TaskResponse(TaskBase):
    id: int
    project_id: int
    assignee_id: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int
