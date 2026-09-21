from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.routes import router as auth_router
from app.expenses.routes import router as expense_router
from app.budgets.routes import router as budget_router
from app.chat.routes import router as chat_router

app = FastAPI(title="EP Tracker - Multi-Agent Finance System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(expense_router)
app.include_router(budget_router)
app.include_router(chat_router)


@app.get("/")
def home():
    return {"message": "EP Tracker Multi-Agent System is running"}
