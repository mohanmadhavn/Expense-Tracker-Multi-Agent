from sqlalchemy import text

from app.database.connection import SessionLocal


def set_budget(user_id: int, category: str, monthly_limit: float, month: int, year: int):
    db = SessionLocal()

    try:
        existing = db.execute(
            text(
                """
                SELECT budget_id FROM budgets
                WHERE user_id = :user_id
                  AND LOWER(category) = LOWER(:category)
                  AND month = :month
                  AND year = :year
                """
            ),
            {
                "user_id": user_id,
                "category": category,
                "month": month,
                "year": year,
            },
        ).fetchone()

        if existing:
            db.execute(
                text(
                    """
                    UPDATE budgets
                    SET monthly_limit = :monthly_limit
                    WHERE budget_id = :budget_id
                    """
                ),
                {"monthly_limit": monthly_limit, "budget_id": existing.budget_id},
            )
            db.commit()

            return {
                "budget_id": existing.budget_id,
                "category": category,
                "monthly_limit": monthly_limit,
                "month": month,
                "year": year,
                "status": "updated",
            }

        result = db.execute(
            text(
                """
                INSERT INTO budgets
                (user_id, category, monthly_limit, month, year)
                VALUES
                (:user_id, :category, :monthly_limit, :month, :year)
                RETURNING budget_id
                """
            ),
            {
                "user_id": user_id,
                "category": category,
                "monthly_limit": monthly_limit,
                "month": month,
                "year": year,
            },
        ).fetchone()

        db.commit()

        return {
            "budget_id": result.budget_id,
            "category": category,
            "monthly_limit": monthly_limit,
            "month": month,
            "year": year,
            "status": "created",
        }

    finally:
        db.close()


def get_budgets(user_id: int, month: int, year: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT budget_id, category, monthly_limit
                FROM budgets
                WHERE user_id = :user_id
                  AND month = :month
                  AND year = :year
                ORDER BY category
                """
            ),
            {"user_id": user_id, "month": month, "year": year},
        ).fetchall()

        return [
            {
                "budget_id": row.budget_id,
                "category": row.category,
                "monthly_limit": float(row.monthly_limit),
            }
            for row in result
        ]

    finally:
        db.close()


def check_budget_status(user_id: int, month: int, year: int):
    db = SessionLocal()

    try:
        result = db.execute(
            text(
                """
                SELECT
                    b.category,
                    b.monthly_limit,
                    COALESCE(SUM(e.amount), 0) AS spent
                FROM budgets b
                LEFT JOIN expenses e
                    ON e.user_id = b.user_id
                   AND LOWER(e.category) = LOWER(b.category)
                   AND EXTRACT(MONTH FROM e.expense_date) = b.month
                   AND EXTRACT(YEAR FROM e.expense_date) = b.year
                WHERE b.user_id = :user_id
                  AND b.month = :month
                  AND b.year = :year
                GROUP BY b.category, b.monthly_limit
                ORDER BY b.category
                """
            ),
            {"user_id": user_id, "month": month, "year": year},
        ).fetchall()

        statuses = []
        for row in result:
            spent = float(row.spent)
            limit = float(row.monthly_limit)
            remaining = limit - spent
            percentage = (spent / limit * 100) if limit > 0 else 0

            if percentage >= 100:
                alert = "OVER_BUDGET"
            elif percentage >= 80:
                alert = "WARNING"
            else:
                alert = "ON_TRACK"

            statuses.append(
                {
                    "category": row.category,
                    "monthly_limit": limit,
                    "spent": spent,
                    "remaining": remaining,
                    "percentage": round(percentage, 1),
                    "alert": alert,
                }
            )

        return {"month": month, "year": year, "budgets": statuses}

    finally:
        db.close()
