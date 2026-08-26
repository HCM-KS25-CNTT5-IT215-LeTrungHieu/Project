import logging

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from app.core.security import get_password_hash
from app.models.base import Base
from app.models.project import Project, ProjectMember, ProjectMemberRoleEnum
from app.models.task import Task, TaskPriorityEnum, TaskStatusEnum
from app.models.user import RoleEnum, User

logger = logging.getLogger(__name__)


def init_db(engine):

    if not database_exists(engine.url):
        create_database(engine.url)
        logger.info(f"Database created at {engine.url}")
    else:
        logger.info(f"Database already exists at {engine.url}")

    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created.")


def seed_data(db: Session):

    admin_email = "admin@example.com"
    admin_user = db.scalar(select(User).where(User.email == admin_email))

    if not admin_user:
        logger.info("Seeding Admin user...")
        admin_user = User(
            email=admin_email,
            full_name="System Administrator",
            password_hash=get_password_hash("admin123"),
            role=RoleEnum.ADMIN.value,
            is_active=True,
        )
        db.add(admin_user)
        db.flush()

        logger.info("Seeding Normal user...")
        normal_user = User(
            email="user@example.com",
            full_name="Regular User",
            password_hash=get_password_hash("user123"),
            role=RoleEnum.USER.value,
            is_active=True,
        )
        db.add(normal_user)
        db.flush()

        logger.info("Seeding Sample Project...")
        project = Project(
            name="Sample Workspace",
            description="Dự án mẫu được tạo tự động khi khởi chạy hệ thống.",
            owner_id=admin_user.id,
        )
        db.add(project)
        db.flush()

        project_member = ProjectMember(
            project_id=project.id,
            user_id=admin_user.id,
            role=ProjectMemberRoleEnum.OWNER.value,
        )
        db.add(project_member)
        db.flush()

        normal_member = ProjectMember(
            project_id=project.id,
            user_id=normal_user.id,
            role=ProjectMemberRoleEnum.MEMBER.value,
        )
        db.add(normal_member)
        db.flush()

        logger.info("Seeding Sample Task...")
        task = Task(
            title="Nhiệm vụ đầu tiên",
            description="Tìm hiểu hệ thống và bắt đầu sử dụng dự án mẫu.",
            status=TaskStatusEnum.TODO.value,
            priority=TaskPriorityEnum.MEDIUM.value,
            project_id=project.id,
            assignee_id=normal_user.id,
        )
        db.add(task)

        db.commit()
        logger.info("Đã seed dữ liệu mẫu thành công!")
    else:
        logger.info("Database đã có dữ liệu, bỏ qua bước seeding.")
