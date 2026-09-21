import { useState } from "react";
import { addExpense } from "../services/api";

const CATEGORIES = ["food", "transport", "shopping", "bills", "entertainment", "health", "education", "other"];

function ExpenseForm({ onAdded }) {
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("food");
  const [description, setDescription] = useState("");
  const [expenseDate, setExpenseDate] = useState(new Date().toISOString().split("T")[0]);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError("");
      await addExpense({
        amount: parseFloat(amount),
        category,
        description,
        expense_date: expenseDate,
      });
      setAmount("");
      setDescription("");
      onAdded();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="expense-form-card">
      <h3>Add Expense</h3>
      <form onSubmit={handleSubmit} className="expense-form">
        <input
          type="number"
          placeholder="Amount"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          step="0.01"
          min="0"
          required
        />
        <select value={category} onChange={(e) => setCategory(e.target.value)}>
          {CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>{cat.charAt(0).toUpperCase() + cat.slice(1)}</option>
          ))}
        </select>
        <input
          type="text"
          placeholder="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
        <input
          type="date"
          value={expenseDate}
          onChange={(e) => setExpenseDate(e.target.value)}
          required
        />
        <button type="submit">Add</button>
      </form>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default ExpenseForm;
