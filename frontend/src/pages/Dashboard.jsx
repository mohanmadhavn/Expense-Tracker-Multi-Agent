import { useEffect, useState } from "react";
import { getExpenses, getMonthlySummary, getBudgetStatus } from "../services/api";
import ExpenseForm from "../components/ExpenseForm";
import ExpenseList from "../components/ExpenseList";
import BudgetOverview from "../components/BudgetOverview";
import Chat from "../components/Chat";

function Dashboard({ onLogout }) {
  const [expenses, setExpenses] = useState([]);
  const [summary, setSummary] = useState(null);
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [activeTab, setActiveTab] = useState("expenses");

  const now = new Date();
  const month = now.getMonth() + 1;
  const year = now.getFullYear();

  const loadData = async () => {
    try {
      const expData = await getExpenses();
      setExpenses(expData.expenses || []);
    } catch (err) {
      console.error(err);
    }

    try {
      const sumData = await getMonthlySummary(month, year);
      setSummary(sumData);
    } catch (err) {
      console.error(err);
    }

    try {
      const budData = await getBudgetStatus(month, year);
      setBudgetStatus(budData);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>EP Tracker</h1>
        <button className="logout-btn" onClick={onLogout}>Logout</button>
      </header>

      <nav className="tabs">
        <button className={activeTab === "expenses" ? "active" : ""} onClick={() => setActiveTab("expenses")}>
          Expenses
        </button>
        <button className={activeTab === "budgets" ? "active" : ""} onClick={() => setActiveTab("budgets")}>
          Budgets
        </button>
        <button className={activeTab === "chat" ? "active" : ""} onClick={() => setActiveTab("chat")}>
          AI Assistant
        </button>
      </nav>

      <main className="dashboard-content">
        {activeTab === "expenses" && (
          <div>
            {summary && (
              <div className="summary-card">
                <h2>This Month's Summary</h2>
                <p className="grand-total">Total Spent: Rs.{summary.grand_total?.toFixed(2) || "0.00"}</p>
                <div className="category-chips">
                  {summary.categories?.map((cat) => (
                    <span key={cat.category} className="chip">
                      {cat.category}: Rs.{cat.total.toFixed(2)}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <ExpenseForm onAdded={loadData} />
            <ExpenseList expenses={expenses} />
          </div>
        )}

        {activeTab === "budgets" && (
          <BudgetOverview
            budgetStatus={budgetStatus}
            month={month}
            year={year}
            onUpdated={loadData}
          />
        )}

        {activeTab === "chat" && <Chat />}
      </main>
    </div>
  );
}

export default Dashboard;
