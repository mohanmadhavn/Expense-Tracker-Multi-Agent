from sqlalchemy import text

from app.database.connection import SessionLocal


def save_audit_log(
    user_id: int,
    agent_name: str,
    action: str,
    resource_type: str,
    resource_id: int,
    status: str,
    details: str,
):
    db = SessionLocal()

    try:
        db.execute(
            text(
                """
                INSERT INTO audit_logs
                (user_id, agent_name, action, resource_type,
                 resource_id, status, details)
                VALUES
                (:user_id, :agent_name, :action, :resource_type,
                 :resource_id, :status, :details)
                """
            ),
            {
                "user_id": user_id,
                "agent_name": agent_name,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "status": status,
                "details": details,
            },
        )
        db.commit()

    finally:
        db.close()
