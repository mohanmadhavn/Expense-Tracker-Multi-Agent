from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth.dependencies import get_current_user
from app.agents.coordinator_agent import coordinator_agent
from app.agents.expense_agent import expense_agent
from app.agents.budget_agent import budget_agent
from app.agents.insights_agent import insights_agent
from app.tools.memory_tools import save_memory, get_memory
from app.tools.audit_tools import save_audit_log
from app.tools.input_tools import validate_message
from app.tools.pii_tools import redact_pii

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: str


@router.post("")
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    valid, message = validate_message(request.message)

    if not valid:
        raise HTTPException(status_code=400, detail=message)

    message = redact_pii(message)
    user_id = current_user["user_id"]

    save_memory(
        user_id=user_id,
        session_id=request.session_id,
        role="user",
        message=message,
    )

    memory = get_memory(user_id=user_id, session_id=request.session_id)

    selected_agent = coordinator_agent(message)

    if selected_agent == "EXPENSE":
        response = expense_agent(user_message=message, user_id=user_id)

        save_memory(
            user_id=user_id,
            session_id=request.session_id,
            role="assistant",
            message=response,
        )
        save_audit_log(
            user_id=user_id,
            agent_name="EXPENSE",
            action="MANAGE_EXPENSE",
            resource_type="EXPENSE",
            resource_id=0,
            status="SUCCESS",
            details="User interacted with expense agent",
        )

        return {
            "agent": "EXPENSE",
            "response": response,
            "memory_messages": len(memory),
        }

    elif selected_agent == "BUDGET":
        response = budget_agent(user_message=message, user_id=user_id)

        save_memory(
            user_id=user_id,
            session_id=request.session_id,
            role="assistant",
            message=response,
        )
        save_audit_log(
            user_id=user_id,
            agent_name="BUDGET",
            action="MANAGE_BUDGET",
            resource_type="BUDGET",
            resource_id=0,
            status="SUCCESS",
            details="User interacted with budget agent",
        )

        return {
            "agent": "BUDGET",
            "response": response,
            "memory_messages": len(memory),
        }

    elif selected_agent == "INSIGHTS":
        response = insights_agent(user_message=message)

        save_memory(
            user_id=user_id,
            session_id=request.session_id,
            role="assistant",
            message=response,
        )
        save_audit_log(
            user_id=user_id,
            agent_name="INSIGHTS",
            action="ASK_INSIGHTS",
            resource_type="FAQ",
            resource_id=0,
            status="SUCCESS",
            details="User asked a financial insights question",
        )

        return {
            "agent": "INSIGHTS",
            "response": response,
            "memory_messages": len(memory),
        }

    else:
        return {
            "agent": "UNKNOWN",
            "response": "I'm not sure how to help with that. Try asking about expenses, budgets, or financial tips.",
            "memory_messages": len(memory),
        }
