from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date

from app.auth.dependencies import get_current_user
from app.tools.expense_tools import (
    add_expense,
    get_recent_expenses,
    get_expenses_by_category,
    get_monthly_summary,
)
from app.tools.audit_tools import save_audit_log

router = APIRouter(prefix="/expenses", tags=["Expenses"])


class AddExpenseRequest(BaseModel):
    amount: float
    category: str
    description: str
    expense_date: str


@router.post("")
def create_expense(
    request: AddExpenseRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    result = add_expense(
        user_id=user_id,
        amount=request.amount,
        category=request.category,
        description=request.description,
        expense_date=request.expense_date,
    )

    save_audit_log(
        user_id=user_id,
        agent_name="API",
        action="ADD_EXPENSE",
        resource_type="EXPENSE",
        resource_id=result["expense_id"],
        status="SUCCESS",
        details=f"Added expense: {request.category} - {request.amount}",
    )

    return result


@router.get("")
def list_expenses(current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    expenses = get_recent_expenses(user_id=user_id, limit=20)
    return {"expenses": expenses}


@router.get("/category/{category}")
def expenses_by_category(
    category: str,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    expenses = get_expenses_by_category(user_id=user_id, category=category)
    return {"category": category, "expenses": expenses}


@router.get("/summary/{month}/{year}")
def monthly_summary(
    month: int,
    year: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    summary = get_monthly_summary(user_id=user_id, month=month, year=year)
    return summary
