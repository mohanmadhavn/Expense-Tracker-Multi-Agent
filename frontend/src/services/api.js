const API_URL = "http://127.0.0.1:8000";

function getHeaders() {
  const token = localStorage.getItem("access_token");
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

export async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Login failed");
  return data;
}

export async function register(name, email, password) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Registration failed");
  return data;
}

export async function getExpenses() {
  const response = await fetch(`${API_URL}/expenses`, {
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to fetch expenses");
  return data;
}

export async function addExpense(expense) {
  const response = await fetch(`${API_URL}/expenses`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(expense),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to add expense");
  return data;
}

export async function getMonthlySummary(month, year) {
  const response = await fetch(`${API_URL}/expenses/summary/${month}/${year}`, {
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to fetch summary");
  return data;
}

export async function getBudgetStatus(month, year) {
  const response = await fetch(`${API_URL}/budgets/status/${month}/${year}`, {
    headers: getHeaders(),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to fetch budget status");
  return data;
}

export async function setBudget(budget) {
  const response = await fetch(`${API_URL}/budgets`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(budget),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Failed to set budget");
  return data;
}

export async function sendChat(message, sessionId) {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ message, session_id: sessionId }),
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.detail || "Chat failed");
  return data;
}
