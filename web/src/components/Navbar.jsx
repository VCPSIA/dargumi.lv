import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import api from "../api";

const LANGS = [
  { code: "lv", label: "LV" },
  { code: "en", label: "EN" },
  { code: "ru", label: "RU" },
  { code: "de", label: "DE" },
];

export default function Navbar() {
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const token = localStorage.getItem("token");

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/auth/me").then(r => r.data),
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  });

  function logout() {
    localStorage.removeItem("token");
    navigate("/");
  }

  function changeLang(code) {
    i18n.changeLanguage(code);
    localStorage.setItem("lang", code);
  }

  return (
    <nav style={{
      background: "#1e3a8a", color: "#fff", padding: "0 24px",
      display: "flex", alignItems: "center", height: 56, gap: 16,
      position: "sticky", top: 0, zIndex: 100,
    }}>
      <Link to="/" style={{ fontWeight: 800, fontSize: 20, letterSpacing: -0.5 }}>
        🏛 {t("nav.title")}
      </Link>
      <div style={{ flex: 1 }} />

      {/* Language switcher */}
      <div style={{ display: "flex", gap: 4 }}>
        {LANGS.map(l => (
          <button key={l.code} onClick={() => changeLang(l.code)} style={{
            background: i18n.language === l.code ? "rgba(255,255,255,.25)" : "transparent",
            border: "1px solid rgba(255,255,255,.3)",
            color: "#fff", borderRadius: 6, padding: "3px 8px",
            fontSize: 12, fontWeight: 700, cursor: "pointer",
          }}>
            {l.label}
          </button>
        ))}
      </div>

      {token ? (
        <>
          {me?.name && (
            <span style={{ color: "#93c5fd", fontSize: 14 }}>👤 {me.name}</span>
          )}
          <button onClick={logout} style={{
            background: "transparent", border: "1.5px solid #93c5fd",
            color: "#93c5fd", borderRadius: 8, padding: "6px 14px", fontWeight: 600,
          }}>{t("nav.logout")}</button>
        </>
      ) : (
        <>
          <Link to="/login" style={{ color: "#93c5fd", fontWeight: 600 }}>{t("nav.login")}</Link>
          <Link to="/register" style={{
            background: "#2563eb", color: "#fff", borderRadius: 8,
            padding: "6px 14px", fontWeight: 600,
          }}>{t("nav.register")}</Link>
        </>
      )}
    </nav>
  );
}
