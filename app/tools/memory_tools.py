from sqlalchemy import text

from app.database.connection import SessionLocal


def save_memory(user_id: int, session_id: str, role: str, message: str):
    db = SessionLocal()

    try:
        db.execute(
            text(
                """
                INSERT INTO conversation_memory
                (user_id, session_id, role, message)
                VALUES
                (:user_id, :session_id, :role, :message)
                """
            ),
            {
                "user_id": user_id,
                "session_id": session_id,
                "role": role,
                "message": message,
            },
        )
        db.commit()

    finally:
        db.close()


def get_memory(user_id: int, session_id: str, limit: int = 10):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT role, message
                FROM conversation_memory
                WHERE user_id = :user_id
                  AND session_id = :session_id
                ORDER BY created_at DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "session_id": session_id, "limit": limit},
        ).fetchall()

        return [
            {"role": row.role, "message": row.message} for row in reversed(result)
        ]

    finally:
        db.close()
