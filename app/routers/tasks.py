from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.response import APIResponse
from app.schemas.task import TaskResponse, TaskUpdate
from app.schemas.user import CurrentUser
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/{task_id}", response_model=APIResponse[TaskResponse])
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    task = TaskService.get_task_details(db, task_id, current_user)
    return APIResponse(message="Task retrieved successfully", data=task)


@router.patch("/{task_id}", response_model=APIResponse[TaskResponse])
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    task = TaskService.update_task(db, task_id, task_in, current_user)
    return APIResponse(message="Task updated successfully", data=task)


@router.delete("/{task_id}", response_model=APIResponse[None])
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_active_user),
):
    TaskService.delete_task(db, task_id, current_user)
    return APIResponse(message="Task deleted successfully")
