from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.project import ProjectMemberRoleEnum


# --- ProjectMember Schemas ---
class ProjectMemberBase(BaseModel):
    role: ProjectMemberRoleEnum = ProjectMemberRoleEnum.MEMBER


class ProjectMemberCreate(ProjectMemberBase):
    user_id: int


class ProjectMemberUpdate(ProjectMemberBase):
    pass


class ProjectMemberResponse(ProjectMemberBase):
    project_id: int
    user_id: int
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
