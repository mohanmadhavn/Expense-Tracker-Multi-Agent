from sqlalchemy import text
from datetime import date

from app.database.connection import SessionLocal


def add_expense(
    user_id: int,
    amount: float,
    category: str,
    description: str,
    expense_date: str,
):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                INSERT INTO expenses
                (user_id, amount, category, description, expense_date)
                VALUES
                (:user_id, :amount, :category, :description, :expense_date)
                RETURNING expense_id
                """
            ),
            {
                "user_id": user_id,
                "amount": amount,
                "category": category,
                "description": description,
                "expense_date": expense_date,
            },
        ).fetchone()

        db.commit()

        return {
            "expense_id": result.expense_id,
            "amount": amount,
            "category": category,
            "description": description,
            "expense_date": expense_date,
            "status": "added",
        }

    finally:
        db.close()


def get_recent_expenses(user_id: int, limit: int = 10):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT expense_id, amount, category, description,
                       expense_date, created_at
                FROM expenses
                WHERE user_id = :user_id
                ORDER BY expense_date DESC
                LIMIT :limit
                """
            ),
            {"user_id": user_id, "limit": limit},
        ).fetchall()

        return [
            {
                "expense_id": row.expense_id,
                "amount": float(row.amount),
                "category": row.category,
                "description": row.description,
                "expense_date": row.expense_date,
                "created_at": row.created_at,
            }
            for row in result
        ]

    finally:
        db.close()


def get_expenses_by_category(user_id: int, category: str):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT expense_id, amount, category, description,
                       expense_date, created_at
                FROM expenses
                WHERE user_id = :user_id
                  AND LOWER(category) = LOWER(:category)
                ORDER BY expense_date DESC
                """
            ),
            {"user_id": user_id, "category": category},
        ).fetchall()

        return [
            {
                "expense_id": row.expense_id,
                "amount": float(row.amount),
                "category": row.category,
                "description": row.description,
                "expense_date": row.expense_date,
                "created_at": row.created_at,
            }
            for row in result
        ]

    finally:
        db.close()


def get_monthly_summary(user_id: int, month: int, year: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT category,
                       COUNT(*) as count,
                       SUM(amount) as total
                FROM expenses
                WHERE user_id = :user_id
                  AND EXTRACT(MONTH FROM expense_date) = :month
                  AND EXTRACT(YEAR FROM expense_date) = :year
                GROUP BY category
                ORDER BY total DESC
                """
            ),
            {"user_id": user_id, "month": month, "year": year},
        ).fetchall()

        categories = [
            {
                "category": row.category,
                "count": row.count,
                "total": float(row.total),
            }
            for row in result
        ]

        grand_total = sum(c["total"] for c in categories)

        return {
            "month": month,
            "year": year,
            "categories": categories,
            "grand_total": grand_total,
        }

    finally:
        db.close()
