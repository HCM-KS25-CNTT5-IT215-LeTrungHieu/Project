from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func

from app.db.database import SessionLocal

from app.models.activity_log import ActivityLog

class ActivityLogService:
    @staticmethod
    def log_action(project_id: int, user_id: int, action: str, details: str | None = None) -> None:
        with SessionLocal() as db:
            log = ActivityLog(
                project_id=project_id,
                user_id=user_id,
                action=action,
                details=details,
            )
            db.add(log)
            db.commit()

    @staticmethod
    def get_project_logs(db: Session, project_id: int, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        stmt = select(ActivityLog).where(ActivityLog.project_id == project_id)
        
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = db.scalar(count_stmt)

        stmt = stmt.order_by(desc(ActivityLog.created_at)).limit(limit).offset(offset)
        logs = list(db.scalars(stmt).all())

        return {"items": logs, "total": total}
