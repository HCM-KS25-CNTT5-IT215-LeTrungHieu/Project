from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectMemberRoleEnum


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


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
