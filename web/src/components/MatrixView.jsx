import { useState } from "react";
import { denomVal } from "../utils/denomSort";

const BASE = "http://localhost:8001";

function shortDenom(d) {
  if (!d) return d;
  const s = String(d);
  const m = s.match(/[\d.,]+/);
  if (!m) return s;
  const n = m[0];
  const low = s.toLowerCase();
  if (low.includes("santīm") || low.includes("santim")) return `${n}s`;
  if (low.includes("lats") || low.includes("lati") || /\blat\b/.test(low)) return `${n}Ls`;
  if (low.includes("eiro cent") || low.includes("euro cent")) return `${n}¢`;
  if (low.includes("eiro") || low.includes("euro")) return `${n}€`;
  if (low.includes("cent") || /\bct\b/.test(low)) return `${n}ct`;
  return s;
}

function getImgSrc(item, userPhotoMap) {
  const userImg = userPhotoMap && userPhotoMap[item.id];
  const catImg = item.image_url
    ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url)
    : null;
  return userImg || catImg || null;
}

const addBtn = {
  display: "inline-flex", alignItems: "center", justifyContent: "center",
  borderRadius: 6, cursor: "pointer", fontWeight: 700, border: "1.5px dashed #cbd5e1",
  color: "#94a3b8", background: "transparent", transition: "all .12s",
};

/**
 * MatrixView — year × denomination grid
 * Rindas = gadi (vecākie augšā, jaunākie apakšā)
 * Kolonnas = nominālvērtības (mazākās kreisajā, lielākās labajā)
 */
export default function MatrixView({ items, userPhotoMap = {}, onSelect, onEmpty, onAddYear, onAddDenom }) {
  const [hoveredId, setHoveredId] = useState(null);
  const [hoveredItem, setHoveredItem] = useState(null);
  const [tooltipPos, setTooltipPos] = useState(null);
  const [yearAsc, setYearAsc] = useState(true);

  const isAdmin = !!(onAddYear || onAddDenom);

  const matrixItems = items.filter(i => i.year && i.denomination);

  const years = [...new Set(matrixItems.map(i => i.year))].sort(
    (a, b) => yearAsc
      ? (parseInt(a) || 0) - (parseInt(b) || 0)
      : (parseInt(b) || 0) - (parseInt(a) || 0)
  );

  // Deduplikācija pēc shortDenom — "1 santīms" un "1 santīmi" → viena kolonna
  const denomShortMap = new Map(); // shortDenom → pirmā pilnā virkne (denomVal kārtošanai)
  for (const item of matrixItems) {
    const s = shortDenom(item.denomination);
    if (s && !denomShortMap.has(s)) denomShortMap.set(s, item.denomination);
  }
  const denoms = [...denomShortMap.keys()].sort(
    (a, b) => denomVal(denomShortMap.get(a)) - denomVal(denomShortMap.get(b))
  );

  // cellMap atslēga: gads__shortDenom
  const cellMap = {};
  for (const item of matrixItems) {
    const key = `${item.year}__${shortDenom(item.denomination)}`;
    const existing = cellMap[key];
    if (!existing || (!existing.image_url && item.image_url)) {
      cellMap[key] = item;
    }
  }

  if (years.length === 0 || denoms.length === 0) {
    return (
      <div style={{ textAlign: "center", paddingTop: 48, color: "#94a3b8" }}>
        <div style={{ fontSize: 36, marginBottom: 10 }}>📊</div>
        <div style={{ fontSize: 14, marginBottom: 16 }}>
          {isAdmin
            ? "Matrica tukša — nav ierakstu ar gadiem un nominālvērtībām."
            : "Nav datu matricas skatam.\nNepieciešami ieraksti ar gadiem un nominālvērtībām."}
        </div>
        {isAdmin && (
          <button onClick={onAddYear}
            style={{ padding: "8px 20px", borderRadius: 8, border: "1.5px solid #93c5fd",
              background: "#eff6ff", color: "#1e40af", fontWeight: 700, cursor: "pointer", fontSize: 13 }}>
            + Pievienot pirmo ierakstu
          </button>
        )}
      </div>
    );
  }

  const th = {
    padding: "7px 8px", background: "#f1f5f9",
    borderBottom: "2px solid #e2e8f0", fontWeight: 600,
    fontSize: 12, color: "#374151", whiteSpace: "nowrap", textAlign: "center",
  };

  return (
    <>
      {hoveredItem && tooltipPos && (() => {
        const imgSrc = getImgSrc(hoveredItem, userPhotoMap);
        if (!imgSrc) return null;
        return (
          <div style={{
            position: "fixed",
            left: tooltipPos.x, top: tooltipPos.y - 10,
            transform: "translateX(-50%) translateY(-100%)",
            background: "#fff", border: "1.5px solid #e2e8f0",
            borderRadius: 12, padding: 8, zIndex: 9999,
            boxShadow: "0 8px 30px rgba(0,0,0,.2)",
            pointerEvents: "none",
          }}>
            <img src={imgSrc} alt={hoveredItem.name}
              style={{ width: 100, height: 100, objectFit: "contain", display: "block" }} />
            <div style={{ fontSize: 11, color: "#64748b", textAlign: "center", marginTop: 5, maxWidth: 100, lineHeight: 1.3 }}>
              {hoveredItem.name}
            </div>
            {hoveredItem.avg_price != null && (
              <div style={{ fontSize: 11, color: "#7c3aed", fontWeight: 700, textAlign: "center", marginTop: 3 }}>
                ~€{hoveredItem.avg_price.toFixed(2)}
              </div>
            )}
          </div>
        );
      })()}

      <div style={{ overflowX: "auto", border: "1px solid #e2e8f0", borderRadius: 12, background: "#fff" }}>
        <table style={{ borderCollapse: "collapse", fontSize: 11, width: "100%" }}>
          <thead>
            <tr>
              <th style={{
                ...th, borderRight: "2px solid #e2e8f0",
                position: "sticky", left: 0, zIndex: 3,
                fontSize: 10, color: "#94a3b8",
              }}>
                <div
                  onClick={() => setYearAsc(v => !v)}
                  title={yearAsc ? "Mainīt: jaunākie augšā" : "Mainīt: vecākie augšā"}
                  style={{ cursor: "pointer", userSelect: "none", display: "inline-flex", alignItems: "center", gap: 3 }}
                >
                  <span>Gads</span>
                  <span style={{ fontSize: 12 }}>{yearAsc ? "↓" : "↑"}</span>
                </div>
                <div>Nom. →</div>
              </th>

              {denoms.map(d => (
                <th key={d} style={{ ...th, borderRight: "1px solid #e2e8f0", minWidth: 44 }} title={denomShortMap.get(d) || d}>
                  {d}
                </th>
              ))}

              {onAddDenom && (
                <th style={{ ...th, borderRight: "none", minWidth: 44 }}>
                  <div
                    onClick={onAddDenom}
                    title="Pievienot jaunu nominālu"
                    style={{ ...addBtn, width: 28, height: 28, fontSize: 17 }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "#818cf8"; e.currentTarget.style.color = "#4f46e5"; e.currentTarget.style.background = "#eef2ff"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#cbd5e1"; e.currentTarget.style.color = "#94a3b8"; e.currentTarget.style.background = "transparent"; }}
                  >+</div>
                </th>
              )}
            </tr>
          </thead>

          <tbody>
            {years.map((year, yi) => {
              const rowBg = yi % 2 === 0 ? "#fff" : "#fafafa";
              return (
                <tr key={year}>
                  <td style={{
                    padding: "5px 8px", fontWeight: 700, color: "#374151", fontSize: 11,
                    borderRight: "2px solid #e2e8f0", borderBottom: "1px solid #f1f5f9",
                    background: "#f8fafc", position: "sticky", left: 0, zIndex: 1, whiteSpace: "nowrap",
                  }}>
                    {year}
                  </td>

                  {denoms.map(d => {
                    const item = cellMap[`${year}__${d}`];
                    const isHov = !!item && hoveredId === item.id;

                    if (!item) {
                      return (
                        <td key={d} style={{
                          borderBottom: "1px solid #f1f5f9", borderRight: "1px solid #f1f5f9",
                          background: rowBg, textAlign: "center", padding: "5px 6px",
                        }}>
                          {onEmpty && (
                            <div
                              onClick={() => onEmpty(year, d)}
                              title={`Pievienot: ${d} · ${year}`}
                              style={{ ...addBtn, width: 24, height: 24, fontSize: 15 }}
                              onMouseEnter={e => { e.currentTarget.style.borderColor = "#93c5fd"; e.currentTarget.style.color = "#3b82f6"; e.currentTarget.style.background = "#eff6ff"; }}
                              onMouseLeave={e => { e.currentTarget.style.borderColor = "#cbd5e1"; e.currentTarget.style.color = "#94a3b8"; e.currentTarget.style.background = "transparent"; }}
                            >+</div>
                          )}
                        </td>
                      );
                    }

                    return (
                      <td key={d} style={{
                        padding: "5px 6px",
                        borderBottom: "1px solid #f1f5f9",
                        borderRight: "1px solid #f1f5f9",
                        textAlign: "center",
                        background: isHov ? "#eff6ff" : rowBg,
                      }}>
                        <div
                          onClick={() => onSelect(item)}
                          onMouseEnter={(e) => {
                            setHoveredId(item.id);
                            setHoveredItem(item);
                            const r = e.currentTarget.getBoundingClientRect();
                            setTooltipPos({ x: r.left + r.width / 2, y: r.top });
                          }}
                          onMouseLeave={() => { setHoveredId(null); setHoveredItem(null); setTooltipPos(null); }}
                          style={{
                            display: "inline-block", padding: "3px 7px", borderRadius: 5,
                            cursor: "pointer", fontWeight: 600, fontSize: 11,
                            background: isHov ? "#dbeafe" : "#dcfce7",
                            border: `1.5px solid ${isHov ? "#93c5fd" : "#86efac"}`,
                            color: isHov ? "#1e40af" : "#166534",
                            whiteSpace: "nowrap", transition: "all .1s",
                          }}
                        >{d}</div>
                      </td>
                    );
                  })}

                  {onAddDenom && <td style={{ borderBottom: "1px solid #f1f5f9", background: rowBg }} />}
                </tr>
              );
            })}

            {onAddYear && (
              <tr>
                <td style={{
                  padding: "6px 10px", background: "#f8fafc",
                  borderRight: "2px solid #e2e8f0", position: "sticky", left: 0, zIndex: 1,
                }}>
                  <div
                    onClick={onAddYear}
                    title="Pievienot jaunu gadu"
                    style={{ ...addBtn, padding: "4px 12px", fontSize: 12, gap: 5 }}
                    onMouseEnter={e => { e.currentTarget.style.borderColor = "#818cf8"; e.currentTarget.style.color = "#4f46e5"; e.currentTarget.style.background = "#eef2ff"; }}
                    onMouseLeave={e => { e.currentTarget.style.borderColor = "#cbd5e1"; e.currentTarget.style.color = "#94a3b8"; e.currentTarget.style.background = "transparent"; }}
                  >+ gads</div>
                </td>
                {denoms.map(d => <td key={d} style={{ borderRight: "1px solid #f1f5f9", background: "#fafafa" }} />)}
                {onAddDenom && <td style={{ background: "#fafafa" }} />}
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </>
  );
}
