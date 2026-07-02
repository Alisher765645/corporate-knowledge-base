import { Routes, Route, Link } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import LoginPage from "./pages/LoginPage";
import AdminPage from "./pages/AdminPage";

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <Link to="/">Поиск</Link>
        <Link to="/login">Вход администратора</Link>
      </nav>
      <Routes>
        <Route path="/" element={<SearchPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin" element={<AdminPage />} />
      </Routes>
    </div>
  );
}
