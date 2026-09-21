from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.tools.budget_tools import set_budget, get_budgets, check_budget_status
from app.tools.audit_tools import save_audit_log

router = APIRouter(prefix="/budgets", tags=["Budgets"])


class SetBudgetRequest(BaseModel):
    category: str
    monthly_limit: float
    month: int
    year: int


@router.post("")
def create_budget(
    request: SetBudgetRequest,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]

    result = set_budget(
        user_id=user_id,
        category=request.category,
        monthly_limit=request.monthly_limit,
        month=request.month,
        year=request.year,
    )

    save_audit_log(
        user_id=user_id,
        agent_name="API",
        action="SET_BUDGET",
        resource_type="BUDGET",
        resource_id=result["budget_id"],
        status="SUCCESS",
        details=f"Set budget: {request.category} - {request.monthly_limit}",
    )

    return result


@router.get("/{month}/{year}")
def list_budgets(
    month: int,
    year: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    budgets = get_budgets(user_id=user_id, month=month, year=year)
    return {"month": month, "year": year, "budgets": budgets}


@router.get("/status/{month}/{year}")
def budget_status(
    month: int,
    year: int,
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user["user_id"]
    status = check_budget_status(user_id=user_id, month=month, year=year)
    return status
