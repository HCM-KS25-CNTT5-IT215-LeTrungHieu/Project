from typing import List

from fastapi import APIRouter, Depends, Query, status, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.user import CurrentUser
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ProjectMemberCreate,
    ProjectMemberResponse,
)
from app.schemas.response import APIResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskListResponse
from app.schemas.activity_log import ActivityLogListResponse
from app.models.task import TaskStatusEnum, TaskPriorityEnum
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.activity_log_service import ActivityLogService

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=APIResponse[ProjectResponse], status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    project = ProjectService.create_project(db, project_in, current_user, background_tasks)
    return APIResponse(
        message="Project created successfully", data=project
    )


@router.get("", response_model=APIResponse[List[ProjectResponse]])
def get_projects(
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    projects = ProjectService.get_user_projects(db, current_user, search)
    return APIResponse(message="Projects retrieved successfully", data=projects)


@router.get("/{project_id}", response_model=APIResponse[ProjectResponse])
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    project = ProjectService.get_project_details(db, project_id, current_user)
    return APIResponse(message="Project retrieved successfully", data=project)


@router.patch("/{project_id}", response_model=APIResponse[ProjectResponse])
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    project = ProjectService.update_project(db, project_id, project_in, current_user, background_tasks)
    return APIResponse(message="Project updated successfully", data=project)


@router.delete("/{project_id}", response_model=APIResponse[None])
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    ProjectService.delete_project(db, project_id, current_user)
    return APIResponse(message="Project deleted successfully")


@router.post("/{project_id}/members", response_model=APIResponse[ProjectMemberResponse], status_code=status.HTTP_201_CREATED)
def add_project_member(
    project_id: int,
    member_in: ProjectMemberCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    member = ProjectService.add_project_member(db, project_id, member_in, current_user, background_tasks)
    return APIResponse(
        message="Member added successfully", data=member
    )


@router.delete("/{project_id}/members/{user_id}", response_model=APIResponse[None])
def remove_project_member(
    project_id: int,
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    ProjectService.remove_project_member(db, project_id, user_id, current_user, background_tasks)
    return APIResponse(message="Member removed successfully")


@router.get("/{project_id}/members", response_model=APIResponse[List[ProjectMemberResponse]])
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    members = ProjectService.get_project_members(db, project_id, current_user)
    return APIResponse(message="Members retrieved successfully", data=members)


@router.post("/{project_id}/tasks", response_model=APIResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
def create_task(
    project_id: int,
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    task = TaskService.create_task(db, project_id, task_in, current_user)
    return APIResponse(message="Task created successfully", data=task)


@router.get("/{project_id}/tasks", response_model=APIResponse[TaskListResponse])
def get_tasks(
    project_id: int,
    search: str | None = None,
    status: TaskStatusEnum | None = None,
    priority: TaskPriorityEnum | None = None,
    assignee_id: int | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|due_date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    tasks_data = TaskService.get_project_tasks(
        db=db,
        project_id=project_id,
        current_user=current_user,
        search=search,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return APIResponse(message="Tasks retrieved successfully", data=tasks_data)


@router.get("/{project_id}/activity-logs", response_model=APIResponse[ActivityLogListResponse])
def get_activity_logs(
    project_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    # Verify user has access to project
    ProjectService.get_project_details(db, project_id, current_user)
    
    logs_data = ActivityLogService.get_project_logs(db, project_id, limit, offset)
    return APIResponse(message="Activity logs retrieved successfully", data=logs_data)
