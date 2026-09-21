function ExpenseList({ expenses }) {
  if (!expenses || expenses.length === 0) {
    return <p className="empty">No expenses found. Add your first expense above.</p>;
  }

  return (
    <div className="expense-list">
      <h3>Recent Expenses</h3>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Category</th>
            <th>Description</th>
            <th>Amount</th>
          </tr>
        </thead>
        <tbody>
          {expenses.map((exp) => (
            <tr key={exp.expense_id}>
              <td>{exp.expense_date}</td>
              <td><span className={`badge badge-${exp.category}`}>{exp.category}</span></td>
              <td>{exp.description}</td>
              <td className="amount">Rs.{exp.amount.toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default ExpenseList;
