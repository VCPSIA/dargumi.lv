import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import api from "../api";
import FlagIcon from "./FlagIcon";

const ROW = (active, indent, extra = {}) => ({
  padding: `5px 8px 5px ${indent}px`,
  cursor: "pointer",
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  borderRadius: 6,
  userSelect: "none",
  background: active ? undefined : "transparent",
  ...extra,
});

// Deduplicates periods by name, keeps first id per name
function deduplicatePeriods(periods) {
  const seen = new Map();
  for (const p of periods) {
    if (!seen.has(p.name)) seen.set(p.name, p);
  }
  return [...seen.values()];
}

// Single country row with expandable periods
function CountryRow({ country, filter, onSelect, section }) {
  const isOpen = filter.countryId === country.id;

  const params = { country_id: country.id };
  if (section) params.section = section;

  const { data: periods = [] } = useQuery({
    queryKey: ["geo-periods", country.id, section || "all"],
    queryFn: () => api.get("/catalog/periods", { params }).then(r => r.data),
    enabled: isOpen,
    staleTime: 5 * 60 * 1000,
  });

  const unique = deduplicatePeriods(periods);

  function toggleCountry() {
    if (isOpen) {
      onSelect({ countryId: null, countryCode: null, countryName: null, periodName: null });
    } else {
      onSelect({ countryId: country.id, countryCode: country.code, countryName: country.name_lv || country.name, periodName: null });
    }
  }

  function clickPeriod(period) {
    onSelect({
      countryId: country.id,
      countryCode: country.code,
      countryName: country.name_lv || country.name,
      periodId: period.id,
      periodName: period.name,
      periodYearStart: period.year_start,
      periodYearEnd: period.year_end,
    });
  }

  const countryActive = isOpen && !filter.periodName;

  return (
    <div>
      <div onClick={toggleCountry} style={ROW(countryActive, 28, {
        fontSize: 13, fontWeight: 600,
        background: countryActive ? "#f0fdf4" : "transparent",
        color: countryActive ? "#166534" : "#374151",
      })}>
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <FlagIcon code={country.code} />
          {country.name_lv || country.name}
        </span>
        <span style={{ fontSize: 10, color: "#94a3b8" }}>{isOpen ? "▼" : "▶"}</span>
      </div>

      {isOpen && unique.map(period => {
        const pActive = filter.countryId === country.id && filter.periodName === period.name;
        const years = period.year_start
          ? ` (${period.year_start}–${period.year_end ?? "..."})`
          : "";
        return (
          <div key={period.id} onClick={() => clickPeriod(period)}
            style={ROW(pActive, 40, {
              fontSize: 12,
              background: pActive ? "#ede9fe" : "transparent",
              color: pActive ? "#7c3aed" : "#475569",
              fontWeight: pActive ? 700 : 400,
              margin: "1px 0",
            })}
            onMouseEnter={e => { if (!pActive) e.currentTarget.style.background = "#f8fafc"; }}
            onMouseLeave={e => { if (!pActive) e.currentTarget.style.background = "transparent"; }}>
            <span style={{ lineHeight: 1.35 }}>{period.name}{years}</span>
          </div>
        );
      })}

      {isOpen && unique.length === 0 && (
        <div style={{ padding: "4px 8px 4px 40px", fontSize: 12, color: "#94a3b8", fontStyle: "italic" }}>
          Nav periodu
        </div>
      )}
    </div>
  );
}

// Continent row with lazy country loading
function ContinentRow({ continent, filter, onSelect, isExtinct = false, section }) {
  const isOpen = filter.openContinentId === continent.id;

  const { data: countries = [] } = useQuery({
    queryKey: ["geo-countries", continent.id, isExtinct],
    queryFn: () => api.get("/catalog/countries", {
      params: isExtinct
        ? { is_extinct: true }
        : { continent_id: continent.id, is_extinct: false }
    }).then(r => r.data),
    enabled: isOpen,
    staleTime: 5 * 60 * 1000,
  });

  function toggle() {
    onSelect({
      ...filter,
      openContinentId: isOpen ? null : continent.id,
      countryId: null,
      countryCode: null,
      countryName: null,
      periodName: null,
    });
  }

  const contActive = isOpen && !filter.countryId;

  return (
    <div>
      <div onClick={toggle} style={ROW(contActive, 8, {
        fontWeight: 700,
        fontSize: 14,
        background: contActive ? "#fef9c3" : "transparent",
        color: isExtinct ? (isOpen ? "#7f1d1d" : "#374151") : (isOpen ? "#854d0e" : "#374151"),
      })}>
        <span>{continent.icon || "🌍"} {continent.name_lv || continent.name}</span>
        <span style={{ fontSize: 10, color: "#94a3b8" }}>{isOpen ? "▼" : "▶"}</span>
      </div>

      {isOpen && countries.map(c => (
        <CountryRow key={c.id} country={c} filter={filter} section={section} onSelect={f => onSelect({ ...f, openContinentId: continent.id })} />
      ))}

      {isOpen && countries.length === 0 && (
        <div style={{ padding: "4px 8px 4px 24px", fontSize: 12, color: "#94a3b8", fontStyle: "italic" }}>
          Nav valstu
        </div>
      )}
    </div>
  );
}

// Main GeoNav component
export default function GeoNav({ filter, onSelect, title, section }) {
  const { t } = useTranslation();

  const { data: continents = [] } = useQuery({
    queryKey: ["geo-continents"],
    queryFn: () => api.get("/catalog/continents").then(r => r.data),
    staleTime: 10 * 60 * 1000,
  });

  const isExtinctOpen = filter.openContinentId === "extinct";

  const { data: extinctCountries = [] } = useQuery({
    queryKey: ["geo-extinct-countries"],
    queryFn: () => api.get("/catalog/countries", { params: { is_extinct: true } }).then(r => r.data),
    enabled: isExtinctOpen,
    staleTime: 5 * 60 * 1000,
  });

  function toggleExtinct() {
    onSelect({
      ...filter,
      openContinentId: isExtinctOpen ? null : "extinct",
      countryId: null,
      countryCode: null,
      countryName: null,
      periodName: null,
    });
  }

  return (
    <div style={{
      width: 230, flexShrink: 0,
      background: "#fff", borderRadius: 12,
      padding: "12px 8px",
      boxShadow: "0 1px 3px rgba(0,0,0,.1)",
      alignSelf: "flex-start",
      position: "sticky", top: 72,
      maxHeight: "calc(100vh - 96px)", overflowY: "auto",
    }}>
      <div style={{
        fontWeight: 700, fontSize: 11, color: "#94a3b8",
        marginBottom: 10, paddingLeft: 4,
        textTransform: "uppercase", letterSpacing: ".05em",
      }}>
        {title || t("nav.catalog")}
      </div>

      {/* Continents */}
      {continents.map(cont => (
        <ContinentRow
          key={cont.id}
          continent={cont}
          filter={filter}
          onSelect={onSelect}
          section={section}
        />
      ))}

      {/* Divider */}
      <div style={{ height: 1, background: "#e5e7eb", margin: "8px 4px" }} />

      {/* Izmirušās valstis */}
      <div onClick={toggleExtinct} style={ROW(isExtinctOpen && !filter.countryId, 8, {
        fontWeight: 700, fontSize: 14,
        background: isExtinctOpen && !filter.countryId ? "#fef2f2" : "transparent",
        color: isExtinctOpen ? "#7f1d1d" : "#374151",
      })}>
        <span>💀 Izmirušās valstis</span>
        <span style={{ fontSize: 10, color: "#94a3b8" }}>{isExtinctOpen ? "▼" : "▶"}</span>
      </div>

      {isExtinctOpen && extinctCountries.map(c => (
        <CountryRow
          key={c.id}
          country={c}
          filter={filter}
          section={section}
          onSelect={f => onSelect({ ...f, openContinentId: "extinct" })}
        />
      ))}

      {isExtinctOpen && extinctCountries.length === 0 && (
        <div style={{ padding: "4px 8px 4px 24px", fontSize: 12, color: "#94a3b8", fontStyle: "italic" }}>
          Nav ierakstu
        </div>
      )}
    </div>
  );
}
