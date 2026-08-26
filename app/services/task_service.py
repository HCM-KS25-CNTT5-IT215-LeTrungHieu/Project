from typing import Any

from sqlalchemy import asc, delete, desc, func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.project import Project, ProjectMember
from app.models.task import Task, TaskPriorityEnum, TaskStatusEnum
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    @staticmethod
    def _check_project_membership(
        db: Session, project_id: int, user_id: int
    ) -> ProjectMember:
        member = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id,
            )
        )
        if not member:
            raise ForbiddenException(detail="You are not a member of this project")
        return member

    @staticmethod
    def _get_task(db: Session, task_id: int) -> Task:
        task = db.scalar(select(Task).where(Task.id == task_id))
        if not task:
            raise NotFoundException(detail="Task not found")
        return task

    @staticmethod
    def create_task(
        db: Session, project_id: int, task_in: TaskCreate, current_user: User
    ) -> Task:
        project = db.scalar(select(Project).where(Project.id == project_id))
        if not project:
            raise NotFoundException(detail="Project not found")

        TaskService._check_project_membership(db, project_id, current_user.id)

        if task_in.assignee_id:
            assignee_member = db.scalar(
                select(ProjectMember).where(
                    ProjectMember.project_id == project_id,
                    ProjectMember.user_id == task_in.assignee_id,
                )
            )
            if not assignee_member:
                raise BadRequestException(detail="Assignee must be a member of the project")

        db_task = Task(
            project_id=project_id,
            title=task_in.title,
            description=task_in.description,
            assignee_id=task_in.assignee_id,
            status=task_in.status.value,
            priority=task_in.priority.value,
            due_date=task_in.due_date,
        )
        db.add(db_task)
        db.flush()
        db.refresh(db_task)
        return db_task

    @staticmethod
    def get_project_tasks(
        db: Session,
        project_id: int,
        current_user: User,
        search: str | None = None,
        status: TaskStatusEnum | None = None,
        priority: TaskPriorityEnum | None = None,
        assignee_id: int | None = None,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> dict[str, Any]:
        project = db.scalar(select(Project).where(Project.id == project_id))
        if not project:
            raise NotFoundException(detail="Project not found")

        TaskService._check_project_membership(db, project_id, current_user.id)

        stmt = select(Task).where(Task.project_id == project_id)

        if search:
            stmt = stmt.where(Task.title.ilike(f"%{search}%"))
        if status:
            stmt = stmt.where(Task.status == status.value)
        if priority:
            stmt = stmt.where(Task.priority == priority.value)
        if assignee_id is not None:
            stmt = stmt.where(Task.assignee_id == assignee_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt)

        order_column = getattr(Task, sort_by, Task.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(order_column))
        else:
            stmt = stmt.order_by(desc(order_column))

        stmt = stmt.limit(limit).offset(offset)
        tasks = list(db.scalars(stmt).all())

        return {"items": tasks, "total": total}

    @staticmethod
    def get_task_details(db: Session, task_id: int, current_user: User) -> Task:
        task = TaskService._get_task(db, task_id)
        TaskService._check_project_membership(db, task.project_id, current_user.id)
        return task

    @staticmethod
    def update_task(
        db: Session, task_id: int, task_in: TaskUpdate, current_user: User
    ) -> Task:
        task = TaskService._get_task(db, task_id)

        TaskService._check_project_membership(db, task.project_id, current_user.id)
        project = db.scalar(select(Project).where(Project.id == task.project_id))

        if project.owner_id != current_user.id and task.assignee_id != current_user.id:
            raise ForbiddenException(
                detail="Only the project owner or task assignee can update the task"
            )

        if task_in.assignee_id is not None:
            assignee_member = db.scalar(
                select(ProjectMember).where(
                    ProjectMember.project_id == task.project_id,
                    ProjectMember.user_id == task_in.assignee_id,
                )
            )
            if not assignee_member:
                raise BadRequestException(detail="Assignee must be a member of the project")

        update_data = task_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if isinstance(value, (TaskStatusEnum, TaskPriorityEnum)):
                value = value.value
            setattr(task, field, value)

        db.flush()
        db.refresh(task)
        return task

    @staticmethod
    def delete_task(db: Session, task_id: int, current_user: User) -> None:
        task = TaskService._get_task(db, task_id)

        TaskService._check_project_membership(db, task.project_id, current_user.id)
        project = db.scalar(select(Project).where(Project.id == task.project_id))

        if project.owner_id != current_user.id:
            raise ForbiddenException(detail="Only the project owner can delete tasks")

        db.execute(delete(Task).where(Task.id == task_id))
        db.flush()
