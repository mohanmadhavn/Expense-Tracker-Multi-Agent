import { useState } from "react";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";

function App() {
  const [page, setPage] = useState(() => {
    const token = localStorage.getItem("access_token");
    return token ? "dashboard" : "login";
  });

  if (page === "dashboard") {
    return <Dashboard onLogout={() => { localStorage.removeItem("access_token"); setPage("login"); }} />;
  }

  if (page === "register") {
    return <Register onSwitch={() => setPage("login")} />;
  }

  return <Login onSwitch={() => setPage("register")} onSuccess={() => setPage("dashboard")} />;
}

export default App;
