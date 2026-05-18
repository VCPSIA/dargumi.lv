import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import GeoNav from "../components/GeoNav";
import ZoomableImage from "../components/ZoomableImage";

const BASE = "http://localhost:8001";

const ICONS = { coins: "🪙", medals: "🏅", stamps: "📮", banknotes: "💵" };


function ItemDetailModal({ item, countryName, countryCode, periodName, onClose }) {
  const { t } = useTranslation();

  const isTwoSided = ["coins", "medals", "banknotes"].includes(item.section);
  const obUrl = item.image_url
    ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url)
    : null;
  const revUrl = item.image_url_reverse
    ? (item.image_url_reverse.startsWith("http") ? item.image_url_reverse : BASE + item.image_url_reverse)
    : null;

  const fields = [
    [t("fields.year"),         item.year],
    [t("fields.country"),      countryName ? `${flagEmoji(countryCode)} ${countryName}` : null],
    [t("fields.period"),       periodName],
    [t("fields.denomination"), item.denomination],
    [t("fields.material"),     item.material],
    [t("fields.diameter"),     item.diameter_mm && `${item.diameter_mm} mm`],
    [t("fields.weight"),       item.weight_g    && `${item.weight_g} g`],
    [t("fields.mint"),         item.mint],
    [t("fields.mintage"),      item.mintage],
    [t("fields.catalogNo"),    item.catalog_number],
    [t("fields.obverse"),      item.obverse_description],
    [t("fields.reverse"),      item.reverse_description],
    [t("fields.description"),  item.description],
    [t("fields.perforation"),  item.perforation],
    [t("fields.color"),        item.color],
  ].filter(([, v]) => v && v !== "unknown");

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, width: "100%", maxWidth: 480,
        maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,.3)",
      }}>
        {/* Photo area */}
        <div style={{ background: "#f1f5f9", borderRadius: "16px 16px 0 0",
          display: "flex", gap: 2, overflow: "hidden",
          minHeight: isTwoSided ? 160 : (obUrl ? undefined : 100) }}>
          {isTwoSided ? (
            <>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
                {obUrl
                  ? <ZoomableImage src={obUrl} alt="ob" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>{ICONS[item.section]}</div><div style={{ fontSize: 11 }}>Averse</div></div>
                }
                {obUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Averse</div>}
              </div>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
                {revUrl
                  ? <ZoomableImage src={revUrl} alt="rev" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>{ICONS[item.section]}</div><div style={{ fontSize: 11 }}>Reverse</div></div>
                }
                {revUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Reverse</div>}
              </div>
            </>
          ) : obUrl ? (
            <ZoomableImage src={obUrl} alt={item.name} style={{ width: "100%", maxHeight: 260, objectFit: "contain" }} />
          ) : (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 48, height: 100 }}>
              {ICONS[item.section]}
            </div>
          )}
        </div>

        <div style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <h2 style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.2, flex: 1 }}>{item.name}</h2>
            <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "#94a3b8", marginLeft: 12 }}>✕</button>
          </div>

          <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse" }}>
            <tbody>
              {fields.map(([k, v]) => (
                <tr key={k} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "7px 0", fontWeight: 600, color: "#64748b", width: "42%", verticalAlign: "top" }}>{k}</td>
                  <td style={{ padding: "7px 0" }}>{String(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default function Section() {
  const { type } = useParams();
  const nav = useNavigate();
  const { t } = useTranslation();

  const [geoFilter, setGeoFilter] = useState({});
  const [selected, setSelected] = useState(null);

  const hasCountry = !!geoFilter.countryId;
  const hasPeriod  = !!geoFilter.periodId;

  const params = { section: type };
  if (geoFilter.periodId) params.period_id = geoFilter.periodId;
  else if (geoFilter.countryId) params.country_id = geoFilter.countryId;
  if (geoFilter.coinCategory && type === "coins") params.coin_category = geoFilter.coinCategory;

  const { data: items = [], isLoading } = useQuery({
    queryKey: ["section-items", type, params],
    queryFn: () => api.get("/catalog/items", { params }).then(r => r.data),
    enabled: hasCountry,
  });

  function handleGeoSelect(f) {
    setGeoFilter(f);
    setSelected(null);
  }

  return (
    <div style={{ paddingTop: 24 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
        <button onClick={() => nav("/")} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer" }}>←</button>
        <h1 style={{ fontWeight: 800, fontSize: 24 }}>{ICONS[type]} {t(`sections.${type}`)}</h1>
        {hasCountry && (
          <span style={{ color: "#94a3b8", fontSize: 14 }}>{items.length} {t("collection.items")}</span>
        )}
        <button className="btn btn-primary" style={{ marginLeft: "auto" }}
          onClick={() => nav(`/recognize/${type}`)}>
          📷 {t("section.recognize")}
        </button>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        {/* Left: Geo navigation */}
        <GeoNav filter={geoFilter} onSelect={handleGeoSelect} title={t(`sections.${type}`)} section={type} />

        {/* Right: Content */}
        <div style={{ flex: 1, minWidth: 0 }}>

          {/* Breadcrumb */}
          {hasCountry && (
            <div style={{ fontSize: 13, color: "#64748b", marginBottom: 16, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
              <span>{flagEmoji(geoFilter.countryCode)} <strong>{geoFilter.countryName}</strong></span>
              {geoFilter.periodName && (
                <><span>›</span><span style={{ fontWeight: 600, color: "#7c3aed" }}>{geoFilter.periodName}</span></>
              )}
            </div>
          )}

          {/* Placeholder */}
          {!hasCountry && (
            <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>{ICONS[type]}</div>
              <p style={{ fontSize: 16 }}>Izvēlies kontinentu → valsti → periodu</p>
            </div>
          )}

          {/* Loading */}
          {hasCountry && isLoading && (
            <p style={{ color: "#888", paddingTop: 40 }}>...</p>
          )}

          {/* Empty */}
          {hasCountry && !isLoading && items.length === 0 && (
            <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>📭</div>
              <p>{t("collection.noResults")}</p>
            </div>
          )}

          {/* Items grid */}
          {hasCountry && !isLoading && items.length > 0 && (
            <div className="grid-3">
              {items.map(item => {
                const imgSrc = item.image_url
                  ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url)
                  : null;
                return (
                  <div key={item.id} className="card" onClick={() => setSelected(item)}
                    style={{ cursor: "pointer" }}
                    onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,.12)"; }}
                    onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}>
                    {imgSrc
                      ? <img src={imgSrc} alt={item.name}
                          style={{ width: "100%", height: 130, objectFit: "contain", background: "#f8fafc", borderRadius: 8, marginBottom: 8 }} />
                      : <div style={{ width: "100%", height: 80, background: "#f8fafc", borderRadius: 8,
                          marginBottom: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 32 }}>
                          {ICONS[type]}
                        </div>
                    }
                    <strong style={{ display: "block", fontSize: 13, marginBottom: 2, lineHeight: 1.3 }}>{item.name}</strong>
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>
                      {[geoFilter.countryName ? `${flagEmoji(geoFilter.countryCode)} ${geoFilter.countryName}` : null, item.year]
                        .filter(Boolean).join(" · ")}
                    </div>
                    {item.denomination && <div className="tag" style={{ marginTop: 6, fontSize: 11 }}>{item.denomination}</div>}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Detail modal */}
      {selected && (
        <ItemDetailModal
          item={selected}
          countryName={geoFilter.countryName || null}
          countryCode={geoFilter.countryCode || null}
          periodName={geoFilter.periodName || null}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}

