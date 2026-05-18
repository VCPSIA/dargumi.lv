import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import api from "../api";

const SECTIONS = [
  { type: "coins",     icon: "🪙" },
  { type: "medals",    icon: "🏅" },
  { type: "stamps",    icon: "📮" },
  { type: "banknotes", icon: "💵" },
];

export default function Sidebar() {
  const { t } = useTranslation();
  const token = localStorage.getItem("token");

  const { data: me } = useQuery({
    queryKey: ["me"],
    queryFn: () => api.get("/auth/me").then(r => r.data),
    enabled: !!token,
    staleTime: 5 * 60 * 1000,
  });

  if (!token) {
    return (
      <aside style={{
        width: 220, minHeight: "calc(100vh - 56px)",
        background: "#fff", borderRight: "1px solid #e5e7eb",
        padding: "12px 0", position: "sticky", top: 56,
        flexShrink: 0, alignSelf: "flex-start",
      }}>
        <NavItem to="/catalog" icon="📚" label={t("nav.catalog")} />
        <Divider />
        <NavItem to="/login"    icon="🔑" label={t("nav.login")} />
        <NavItem to="/register" icon="✏️"  label={t("nav.register")} />
      </aside>
    );
  }

  return (
    <aside style={{
      width: 220,
      minHeight: "calc(100vh - 56px)",
      background: "#fff",
      borderRight: "1px solid #e5e7eb",
      padding: "12px 0",
      position: "sticky",
      top: 56,
      flexShrink: 0,
      alignSelf: "flex-start",
    }}>
      <NavItem to="/" icon="🏠" label={t("nav.home")} end />

      <SectionLabel>{t("nav.sections")}</SectionLabel>

      {SECTIONS.map(s => (
        <NavItem key={s.type} to={`/section/${s.type}`} icon={s.icon} label={t(`sections.${s.type}`)} />
      ))}

      <Divider />

      <NavItem to="/catalog" icon="📚" label={t("nav.catalog")} />
      <NavItem to="/collection" icon="⭐" label={t("nav.myCollection")} />

      {me?.is_admin && (
        <>
          <Divider />
          <NavItem to="/admin" icon="🔧" label="Admin" admin />
        </>
      )}
    </aside>
  );
}

function NavItem({ to, icon, label, end, admin }) {
  return (
    <NavLink to={to} end={end} style={({ isActive }) => ({
      display: "flex",
      alignItems: "center",
      gap: 10,
      padding: "9px 16px",
      fontWeight: isActive ? 700 : 500,
      fontSize: 14,
      color: isActive ? "#2563eb" : admin ? "#d97706" : "#374151",
      background: isActive ? "#eff6ff" : "transparent",
      borderRight: isActive ? "3px solid #2563eb" : "3px solid transparent",
      transition: "background .1s, color .1s",
      textDecoration: "none",
    })}>
      <span style={{ fontSize: 18, lineHeight: 1 }}>{icon}</span>
      {label}
    </NavLink>
  );
}

function SectionLabel({ children }) {
  return (
    <div style={{
      padding: "12px 16px 4px",
      fontSize: 11,
      fontWeight: 700,
      color: "#9ca3af",
      textTransform: "uppercase",
      letterSpacing: "0.08em",
    }}>
      {children}
    </div>
  );
}

function Divider() {
  return <div style={{ height: 1, background: "#e5e7eb", margin: "8px 0" }} />;
}
