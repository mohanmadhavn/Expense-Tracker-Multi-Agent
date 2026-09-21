import { useState } from "react";
import { setBudget } from "../services/api";

const CATEGORIES = ["food", "transport", "shopping", "bills", "entertainment", "health", "education", "other"];

function BudgetOverview({ budgetStatus, month, year, onUpdated }) {
  const [category, setCategory] = useState("food");
  const [limit, setLimit] = useState("");
  const [error, setError] = useState("");

  const handleSetBudget = async (e) => {
    e.preventDefault();
    try {
      setError("");
      await setBudget({
        category,
        monthly_limit: parseFloat(limit),
        month,
        year,
      });
      setLimit("");
      onUpdated();
    } catch (err) {
      setError(err.message);
    }
  };

  const getAlertColor = (alert) => {
    if (alert === "OVER_BUDGET") return "#ef4444";
    if (alert === "WARNING") return "#f59e0b";
    return "#22c55e";
  };

  return (
    <div>
      <div className="expense-form-card">
        <h3>Set Budget</h3>
        <form onSubmit={handleSetBudget} className="expense-form">
          <select value={category} onChange={(e) => setCategory(e.target.value)}>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
            ))}
          </select>
          <input
            type="number"
            placeholder="Monthly Limit"
            value={limit}
            onChange={(e) => setLimit(e.target.value)}
            step="0.01"
            min="0"
            required
          />
          <button type="submit">Set Budget</button>
        </form>
        {error && <p className="error">{error}</p>}
      </div>

      <div className="budget-status">
        <h3>Budget Status - {month}/{year}</h3>
        {(!budgetStatus || !budgetStatus.budgets || budgetStatus.budgets.length === 0) ? (
          <p className="empty">No budgets set. Create your first budget above.</p>
        ) : (
          <div className="budget-cards">
            {budgetStatus.budgets.map((b) => (
              <div key={b.category} className="budget-card">
                <div className="budget-card-header">
                  <span className="budget-category">{b.category}</span>
                  <span className="budget-alert" style={{ color: getAlertColor(b.alert) }}>
                    {b.alert.replace("_", " ")}
                  </span>
                </div>
                <div className="budget-bar-container">
                  <div
                    className="budget-bar"
                    style={{
                      width: `${Math.min(b.percentage, 100)}%`,
                      backgroundColor: getAlertColor(b.alert),
                    }}
                  />
                </div>
                <div className="budget-details">
                  <span>Spent: Rs.{b.spent.toFixed(2)}</span>
                  <span>Limit: Rs.{b.monthly_limit.toFixed(2)}</span>
                </div>
                <p className="budget-remaining">
                  {b.remaining >= 0
                    ? `Rs.${b.remaining.toFixed(2)} remaining`
                    : `Rs.${Math.abs(b.remaining).toFixed(2)} over budget`}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default BudgetOverview;
