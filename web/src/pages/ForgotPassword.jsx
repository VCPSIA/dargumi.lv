import { useState } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const { t } = useTranslation();

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", { email });
      setSent(true);
    } catch {
      setError(t("auth.generalError"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: "60px auto" }}>
      <div className="card">
        <h2 style={{ marginBottom: 8, fontWeight: 800 }}>{t("auth.forgotPasswordTitle")}</h2>

        {sent ? (
          <div>
            <div style={{
              background: "#f0fdf4", border: "1.5px solid #86efac",
              borderRadius: 10, padding: "14px 16px", marginBottom: 20,
              color: "#166534", fontSize: 14, lineHeight: 1.6,
            }}>
              ✅ {t("auth.sentSuccess")}<br />
              <strong>{t("auth.sentExpiry")}</strong>
            </div>
            <Link to="/login" style={{ color: "#2563eb", fontSize: 14 }}>{t("auth.backToLogin")}</Link>
          </div>
        ) : (
          <>
            <p style={{ color: "#64748b", fontSize: 14, marginBottom: 20 }}>
              {t("auth.forgotPasswordDesc")}
            </p>
            <form onSubmit={submit}>
              <div className="form-group">
                <label>{t("auth.email")}</label>
                <input
                  type="email" value={email} required autoFocus
                  onChange={e => setEmail(e.target.value)}
                />
              </div>
              {error && <p className="error">{error}</p>}
              <button type="submit" className="btn btn-primary"
                style={{ width: "100%", marginTop: 8 }}
                disabled={loading}>
                {loading ? "..." : t("auth.sendLink")}
              </button>
            </form>
            <p style={{ marginTop: 16, textAlign: "center", fontSize: 14 }}>
              <Link to="/login" style={{ color: "#2563eb" }}>{t("auth.backToLogin")}</Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
