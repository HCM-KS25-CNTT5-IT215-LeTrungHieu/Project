from fastapi import BackgroundTasks
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.models.project import Project, ProjectMember, ProjectMemberRoleEnum
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectMemberCreate, ProjectUpdate
from app.schemas.user import CurrentUser
from app.services.activity_log_service import ActivityLogService


class ProjectService:
    @staticmethod
    def get_project_by_id(db: Session, project_id: int) -> Project:
        project = db.scalar(select(Project).where(Project.id == project_id))
        if not project:
            raise NotFoundException(detail="Project not found")
        return project

    @staticmethod
    def create_project(
        db: Session,
        project_in: ProjectCreate,
        current_user: CurrentUser,
        background_tasks: BackgroundTasks,
    ) -> Project:

        db_project = Project(
            name=project_in.name,
            description=project_in.description,
            owner_id=current_user.id,
        )
        db.add(db_project)
        db.flush()
        db.refresh(db_project)

        db_member = ProjectMember(
            project_id=db_project.id,
            user_id=current_user.id,
            role=ProjectMemberRoleEnum.OWNER.value,
        )
        db.add(db_member)
        db.flush()

        background_tasks.add_task(
            ActivityLogService.log_action,
            project_id=db_project.id,
            user_id=current_user.id,
            action="CREATE_PROJECT",
            details=f"Project '{db_project.name}' created",
        )

        return db_project

    @staticmethod
    def get_user_projects(
        db: Session, current_user: CurrentUser, search: str | None = None
    ) -> list[Project]:

        stmt = (
            select(Project)
            .join(ProjectMember)
            .where(ProjectMember.user_id == current_user.id)
        )

        if search:
            stmt = stmt.where(Project.name.ilike(f"%{search}%"))

        return list(db.scalars(stmt).all())

    @staticmethod
    def get_project_details(
        db: Session, project_id: int, current_user: CurrentUser
    ) -> Project:
        project = ProjectService.get_project_by_id(db, project_id)

        is_member = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
        )

        if not is_member and project.owner_id != current_user.id:
            raise ForbiddenException(detail="You do not have access to this project")

        return project

    @staticmethod
    def update_project(
        db: Session,
        project_id: int,
        project_in: ProjectUpdate,
        current_user: CurrentUser,
        background_tasks: BackgroundTasks,
    ) -> Project:
        project = ProjectService.get_project_by_id(db, project_id)

        if project.owner_id != current_user.id:
            raise ForbiddenException(
                detail="Only the project owner can update the project"
            )

        update_data = project_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)

        db.flush()
        db.refresh(project)
        background_tasks.add_task(
            ActivityLogService.log_action,
            project_id=project.id,
            user_id=current_user.id,
            action="UPDATE_PROJECT",
            details="Project details updated",
        )
        return project

    @staticmethod
    def delete_project(db: Session, project_id: int, current_user: CurrentUser) -> None:
        project = ProjectService.get_project_by_id(db, project_id)

        if project.owner_id != current_user.id:
            raise ForbiddenException(detail="Only the owner can delete this project")

        from app.models.activity_log import ActivityLog
        from app.models.task import Task

        db.execute(delete(ActivityLog).where(ActivityLog.project_id == project_id))
        db.execute(delete(Task).where(Task.project_id == project_id))
        db.execute(delete(ProjectMember).where(ProjectMember.project_id == project_id))
        db.delete(project)
        db.flush()

    @staticmethod
    def add_project_member(
        db: Session,
        project_id: int,
        member_in: ProjectMemberCreate,
        current_user: CurrentUser,
        background_tasks: BackgroundTasks,
    ) -> ProjectMember:
        project = ProjectService.get_project_by_id(db, project_id)

        if project.owner_id != current_user.id:
            raise ForbiddenException(detail="Only the project owner can add members")

        user_to_add = db.scalar(select(User).where(User.id == member_in.user_id))
        if not user_to_add:
            raise NotFoundException(detail="User to add not found")

        db_member = ProjectMember(
            project_id=project_id,
            user_id=member_in.user_id,
            role=member_in.role.value,
        )
        db.add(db_member)
        try:
            db.flush()
        except IntegrityError:
            db.rollback()
            raise BadRequestException(detail="User is already a member of this project")
        db.refresh(db_member)
        background_tasks.add_task(
            ActivityLogService.log_action,
            project_id=project_id,
            user_id=current_user.id,
            action="ADD_MEMBER",
            details=f"User {member_in.user_id} added with role {member_in.role.value}",
        )
        return db_member

    @staticmethod
    def remove_project_member(
        db: Session,
        project_id: int,
        user_id: int,
        current_user: CurrentUser,
        background_tasks: BackgroundTasks,
    ) -> None:
        project = ProjectService.get_project_by_id(db, project_id)

        if project.owner_id != current_user.id:
            raise ForbiddenException(detail="Only the project owner can remove members")

        if project.owner_id == user_id:
            raise BadRequestException(detail="Cannot remove the owner from the project")

        member = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
            )
        )

        if not member:
            raise NotFoundException(detail="User is not a member of this project")

        db.delete(member)
        db.flush()

        background_tasks.add_task(
            ActivityLogService.log_action,
            project_id=project_id,
            user_id=current_user.id,
            action="REMOVE_MEMBER",
            details=f"User {user_id} removed",
        )

    @staticmethod
    def get_project_members(
        db: Session, project_id: int, current_user: CurrentUser
    ) -> list[ProjectMember]:
        project = ProjectService.get_project_by_id(db, project_id)

        is_member = db.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id,
            )
        )

        if not is_member and project.owner_id != current_user.id:
            raise ForbiddenException(detail="You do not have access to this project")

        return list(
            db.scalars(
                select(ProjectMember).where(ProjectMember.project_id == project_id)
            ).all()
        )
