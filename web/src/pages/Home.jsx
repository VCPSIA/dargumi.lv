import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";

export default function Home() {
  const nav = useNavigate();
  const { t } = useTranslation();

  const SECTIONS = [
    { type: "coins",     icon: "🪙", label: t("sections.coins"),     color: "#fef3c7" },
    { type: "medals",    icon: "🏅", label: t("sections.medals"),    color: "#dcfce7" },
    { type: "stamps",    icon: "📮", label: t("sections.stamps"),    color: "#ede9fe" },
    { type: "banknotes", icon: "💵", label: t("sections.banknotes"), color: "#d1fae5" },
  ];

  return (
    <div style={{ paddingTop: 48 }}>
      <h1 style={{ textAlign: "center", fontSize: 32, fontWeight: 800, marginBottom: 8 }}>
        {t("home.welcome")}
      </h1>
      <p style={{ textAlign: "center", color: "#666", marginBottom: 40, fontSize: 16 }}>
        {t("home.subtitle")}
      </p>
      <div className="grid-3" style={{ maxWidth: 640, margin: "0 auto" }}>
        {SECTIONS.map((s) => (
          <div
            key={s.type}
            className="section-card"
            style={{ background: s.color }}
            onClick={() => nav("/catalog", { state: { section: s.type } })}
          >
            <div className="icon">{s.icon}</div>
            <h2>{s.label}</h2>
          </div>
        ))}
      </div>
    </div>
  );
}
