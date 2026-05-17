import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const nav = useNavigate();
  const { t } = useTranslation();

  async function submit(e) {
    e.preventDefault();
    setError("");
    try {
      const { data } = await api.post("/auth/login", form);
      localStorage.setItem("token", data.access_token);
      nav("/");
    } catch (err) {
      setError(err.response?.data?.detail || t("recognize.error"));
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "60px auto" }}>
      <div className="card">
        <h2 style={{ marginBottom: 20, fontWeight: 800 }}>{t("auth.loginTitle")}</h2>
        <form onSubmit={submit}>
          <div className="form-group">
            <label>{t("auth.email")}</label>
            <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} required />
          </div>
          <div className="form-group">
            <label>{t("auth.password")}</label>
            <input type="password" value={form.password} onChange={e => setForm(f => ({ ...f, password: e.target.value }))} required />
          </div>
          {error && <p className="error">{error}</p>}
          <button type="submit" className="btn btn-primary" style={{ width: "100%", marginTop: 8 }}>{t("auth.loginBtn")}</button>
        </form>
        <p style={{ marginTop: 16, textAlign: "center", fontSize: 14 }}>
          {t("auth.noAccount")} <Link to="/register" style={{ color: "#2563eb" }}>{t("auth.registerLink")}</Link>
        </p>
      </div>
    </div>
  );
}
