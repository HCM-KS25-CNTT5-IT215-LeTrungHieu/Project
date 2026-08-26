import bcrypt

from app.db.database import SessionLocal, engine
from app.models.base import Base
from app.models.project import Project, ProjectMember, ProjectMemberRoleEnum
from app.models.task import Task, TaskPriorityEnum, TaskStatusEnum
from app.models.user import RoleEnum, User


def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def seed():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Check if we already have data
    if db.query(User).first():
        print("Database already seeded.")
        db.close()
        return

    print("Seeding Users...")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        full_name="System Admin",
        role=RoleEnum.ADMIN.value,
    )
    user1 = User(
        email="user1@example.com",
        password_hash=get_password_hash("user123"),
        full_name="John Doe",
        role=RoleEnum.USER.value,
    )
    db.add_all([admin, user1])
    db.commit()
    db.refresh(admin)
    db.refresh(user1)

    print("Seeding Projects...")
    project1 = Project(
        name="Alpha Project",
        description="This is the first project.",
        owner_id=admin.id,
    )
    db.add(project1)
    db.commit()
    db.refresh(project1)

    print("Seeding Project Members...")
    member1 = ProjectMember(
        project_id=project1.id,
        user_id=user1.id,
        role=ProjectMemberRoleEnum.MEMBER.value,
    )
    db.add(member1)
    db.commit()

    print("Seeding Tasks...")
    task1 = Task(
        project_id=project1.id,
        title="Setup Repository",
        description="Initialize the git repo and push initial code.",
        assignee_id=admin.id,
        status=TaskStatusEnum.DONE.value,
        priority=TaskPriorityEnum.HIGH.value,
    )
    task2 = Task(
        project_id=project1.id,
        title="Implement Login",
        description="Create login API endpoint.",
        assignee_id=user1.id,
        status=TaskStatusEnum.IN_PROGRESS.value,
        priority=TaskPriorityEnum.MEDIUM.value,
    )
    db.add_all([task1, task2])
    db.commit()

    print("Seed completed successfully!")
    db.close()


if __name__ == "__main__":
    seed()
