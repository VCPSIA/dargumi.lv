import { useState } from "react";
import { useNavigate, useSearchParams, Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";

export default function ResetPassword() {
  const [params] = useSearchParams();
  const token = params.get("token") || "";
  const [form, setForm] = useState({ password: "", confirm: "" });
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const nav = useNavigate();
  const { t } = useTranslation();

  async function submit(e) {
    e.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError(t("auth.passwordsNoMatch"));
      return;
    }
    if (form.password.length < 6) {
      setError(t("auth.passwordTooShort"));
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/reset-password", { token, password: form.password });
      setDone(true);
      setTimeout(() => nav("/login"), 2500);
    } catch (err) {
      setError(err.response?.data?.detail || t("auth.resetError"));
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div style={{ maxWidth: 400, margin: "60px auto" }}>
        <div className="card">
          <p className="error">{t("auth.linkInvalid")}</p>
          <Link to="/login" style={{ color: "#2563eb", fontSize: 14 }}>{t("auth.backToLogin")}</Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 400, margin: "60px auto" }}>
      <div className="card">
        <h2 style={{ marginBottom: 8, fontWeight: 800 }}>{t("auth.newPasswordTitle")}</h2>

        {done ? (
          <div style={{
            background: "#f0fdf4", border: "1.5px solid #86efac",
            borderRadius: 10, padding: "14px 16px", color: "#166534", fontSize: 14,
          }}>
            ✅ {t("auth.resetSuccess")}
          </div>
        ) : (
          <form onSubmit={submit}>
            <div className="form-group">
              <label>{t("auth.newPasswordLabel")}</label>
              <input
                type="password" value={form.password} required autoFocus minLength={6}
                onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
              />
            </div>
            <div className="form-group">
              <label>{t("auth.repeatPassword")}</label>
              <input
                type="password" value={form.confirm} required minLength={6}
                onChange={e => setForm(f => ({ ...f, confirm: e.target.value }))}
              />
            </div>
            {error && <p className="error">{error}</p>}
            <button type="submit" className="btn btn-primary"
              style={{ width: "100%", marginTop: 8 }}
              disabled={loading}>
              {loading ? "..." : t("auth.savePassword")}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
