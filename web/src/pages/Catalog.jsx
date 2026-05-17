import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import FlagIcon from "../components/FlagIcon";
import GeoNav from "../components/GeoNav";
import ZoomableImage from "../components/ZoomableImage";
import RecognizeModal from "../components/RecognizeModal";
import MatrixView from "../components/MatrixView";

const BASE = "http://localhost:8001";

const CAT_DEFS = [
  { key: "circulation",   icon: "💰", labelKey: "coinCategories.circulation" },
  { key: "commemorative", icon: "🏛️", labelKey: "coinCategories.commemorative" },
  { key: "collector",     icon: "⭐", labelKey: "coinCategories.collector" },
  { key: "tokens",        icon: "🎰", labelKey: "coinCategories.tokens" },
];

// ── Detail modal (info only) ───────────────────────────────────────────────────
function CatalogDetailModal({ item, countryName, countryCode, periodName, onClose }) {
  const { t } = useTranslation();

  const { data: priceData } = useQuery({
    queryKey: ["avg-price", item.id],
    queryFn: () => api.get(`/catalog/items/${item.id}/avg_price`).then(r => r.data),
  });

  // User photo for display
  const { data: userItems = [] } = useQuery({
    queryKey: ["collection-for-catalog", item.id],
    queryFn: () => api.get("/collection", { params: { catalog_item_id: item.id } }).then(r => r.data),
    retry: false,
  });
  const userItem = userItems[0];
  const userObUrl = userItem?.user_image ? BASE + userItem.user_image : null;
  const userRevUrl = userItem?.user_image_reverse ? BASE + userItem.user_image_reverse : null;

  const countryDisplay = countryName ? `${flagEmoji(countryCode)} ${countryName}` : null;

  const fields = [
    [t("fields.name"), item.name],
    [t("fields.year"), item.year],
    [t("fields.country"), countryDisplay],
    [t("fields.period"), periodName],
    [t("fields.denomination"), item.denomination],
    [t("fields.material"), item.material],
    [t("fields.diameter"), item.diameter_mm && `${item.diameter_mm} mm`],
    [t("fields.weight"), item.weight_g && `${item.weight_g} g`],
    [t("fields.mint"), item.mint],
    [t("fields.mintage"), item.mintage],
    [t("fields.catalogNo"), item.catalog_number],
    [t("fields.obverse"), item.obverse_description],
    [t("fields.reverse"), item.reverse_description],
    [t("fields.description"), item.description],
    [t("fields.perforation"), item.perforation],
    [t("fields.color"), item.color],
    [t("fields.category"),
      ({ circulation: t("coinCategories.circulation"), commemorative: t("coinCategories.commemorative"),
         collector: t("coinCategories.collector"), tokens: t("coinCategories.tokens") })[item.coin_category] || null],
    [t("fields.avgPrice"),
      priceData?.avg_price != null
        ? `€${priceData.avg_price.toFixed(2)} (${priceData.count} ${t("fields.collectors")})`
        : null],
  ].filter(([, v]) => v && v !== "unknown");

  const isTwoSided = ["coins", "medals", "banknotes"].includes(item.section);
  const catObUrl = item.image_url       ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url) : null;
  const catRevUrl = item.image_url_reverse ? (item.image_url_reverse.startsWith("http") ? item.image_url_reverse : BASE + item.image_url_reverse) : null;
  const obUrl = userObUrl || catObUrl;
  const revUrl = userRevUrl || catRevUrl;

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, width: "100%", maxWidth: 540,
        maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,.3)",
      }}>
        <div style={{ background: "#f1f5f9", borderRadius: "16px 16px 0 0", display: "flex", gap: 2, overflow: "hidden",
          minHeight: isTwoSided ? 160 : (obUrl ? undefined : 100) }}>
          {isTwoSided ? (
            <>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
                {obUrl ? <ZoomableImage src={obUrl} alt="ob" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>🪙</div><div style={{ fontSize: 11 }}>Averse</div></div>}
                {obUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Averse</div>}
              </div>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
                {revUrl ? <ZoomableImage src={revUrl} alt="rev" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>🪙</div><div style={{ fontSize: 11 }}>Reverse</div></div>}
                {revUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Reverse</div>}
              </div>
            </>
          ) : obUrl ? (
            <ZoomableImage src={obUrl} alt={item.name} style={{ width: "100%", maxHeight: 280, objectFit: "contain" }} />
          ) : (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 48, height: 100 }}>
              {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📷"}
            </div>
          )}
        </div>

        <div style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div className="tag" style={{ marginBottom: 6 }}>
                {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section]} {t(`sections.${item.section}`)}
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.2 }}>{item.name}</h2>
              <div style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>
                {[countryDisplay, item.year].filter(Boolean).join(" · ")}
              </div>
            </div>
            <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "#94a3b8" }}>✕</button>
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


// ── Main Catalog page ──────────────────────────────────────────────────────────
export default function Catalog() {
  const { t } = useTranslation();
  const nav = useNavigate();
  const [geoFilter, setGeoFilter] = useState({});  // { openContinentId, countryId, countryCode, countryName, periodName }
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [layout, setLayout] = useState("3");
  const [showRecognize, setShowRecognize] = useState(false);

  const hasCountry = !!geoFilter.countryId;
  const hasPeriod  = !!geoFilter.periodName;

  const params = {};
  if (hasCountry) params.country_id = geoFilter.countryId;
  if (search) params.search = search;

  const { data: allItems = [], isLoading } = useQuery({
    queryKey: ["catalog-items", params],
    queryFn: () => api.get("/catalog/items", { params }).then(r => r.data),
    enabled: hasCountry || !!search,
  });

  // Client-side filter by period name if selected
  const items = hasPeriod
    ? allItems.filter(item => {
        // item doesn't directly have period name — need to match via period_id
        // We rely on the fact that when a period is selected, we show items from that country
        // and filter by period name would require period info on item
        // Since catalog items don't include period name, we skip period filtering here
        // and show all items for the country (period nav is just for navigation UX)
        return true;
      })
    : allItems;

  // User's collection items — for photos and ownership badges
  const { data: userCollItems = [] } = useQuery({
    queryKey: ["collection"],
    queryFn: () => api.get("/collection", { params: { } }).then(r => r.data),
    retry: 1,
  });
  const userPhotoMap = {};
  const ownedMap = {}; // catalog_item_id → { collection: qty, trade: qty, wishlist: qty }
  for (const ci of userCollItems) {
    const catId = ci.catalog_item?.id;
    if (!catId) continue;
    if (ci.user_image || ci.user_image_reverse)
      userPhotoMap[catId] = ci.user_image ? BASE + ci.user_image : BASE + ci.user_image_reverse;
    if (!ownedMap[catId]) ownedMap[catId] = {};
    ownedMap[catId][ci.item_type] = (ownedMap[catId][ci.item_type] || 0) + (ci.quantity || 1);
  }

  function handleGeoSelect(f) {
    setGeoFilter(f);
    setSelected(null);
  }

  const totalDisplay = items.length;

  return (
    <div style={{ paddingTop: 24 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
        <h1 style={{ fontWeight: 800, fontSize: 24 }}>📚 {t("nav.catalog")}</h1>
        {hasCountry && <span style={{ color: "#94a3b8", fontSize: 14 }}>{totalDisplay} {t("collection.items")}</span>}
        <button className="btn btn-outline" style={{ marginLeft: "auto", padding: "8px 14px", fontSize: 14 }}
          onClick={() => setShowRecognize(true)}>
          📷 {t("recognize.title")}
        </button>
      </div>

      {/* Search + layout toggle */}
      <div style={{ marginBottom: 20, display: "flex", gap: 10, alignItems: "center" }}>
        <input placeholder={t("collection.search")} value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1.5px solid #ddd", fontSize: 14, flex: 1, maxWidth: 400 }} />
        <div style={{ display: "flex", border: "1.5px solid #e2e8f0", borderRadius: 8, overflow: "hidden", flexShrink: 0 }}>
          {[["list","≡","Rindas"],["3","⊞","3 kolonnas"],["4","⊟","4 kolonnas"],["5","⋮⋮","5 kolonnas"],["matrix","⊠","Laikmeta tabula"]].map(([mode, icon, title], i, arr) => (
            <button key={mode} onClick={() => setLayout(mode)} title={title} style={{
              padding: "7px 11px", border: "none", cursor: "pointer", fontSize: mode === "list" ? 18 : 14, lineHeight: 1,
              fontWeight: 700,
              background: layout === mode ? "#2563eb" : "#fff",
              color: layout === mode ? "#fff" : "#64748b",
              borderRight: i < arr.length - 1 ? "1.5px solid #e2e8f0" : "none",
            }}>{icon}</button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        <GeoNav filter={geoFilter} onSelect={handleGeoSelect} title={t("nav.catalog")} />

        <div style={{ flex: 1, minWidth: 0 }}>

          {/* ── Breadcrumb ── */}
          {hasCountry && (
            <div style={{ fontSize: 13, color: "#64748b", marginBottom: 16, display: "flex", alignItems: "center", gap: 6, flexWrap: "wrap" }}>
              {geoFilter.countryName && <span>{flagEmoji(geoFilter.countryCode)} <strong>{geoFilter.countryName}</strong></span>}
              {geoFilter.periodName && <><span>›</span><span style={{ fontWeight: 600, color: "#7c3aed" }}>{geoFilter.periodName}</span></>}
            </div>
          )}

          {/* ── Placeholder ── */}
          {!hasCountry && !search && (
            <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>📚</div>
              <p style={{ fontSize: 16 }}>Izvēlies kontinentu → valsti → periodu</p>
            </div>
          )}

          {/* ── Items grid ── */}
          {(hasCountry || search) && isLoading && <p style={{ color: "#888" }}>...</p>}

          {(hasCountry || search) && !isLoading && items.length === 0 && (
            <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>📭</div>
              <p>{t("collection.noResults")}</p>
            </div>
          )}

          {(hasCountry || search) && !isLoading && items.length > 0 && (
            <>

              {layout === "matrix" ? (
                <MatrixView
                  items={items}
                  userPhotoMap={userPhotoMap}
                  onSelect={setSelected}
                />
              ) : layout !== "list" ? (
                <div className={`grid-${layout}`}>
                  {items.map(item => {
                    const compact = layout === "4" || layout === "5";
                    const catImg = item.image_url ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url) : null;
                    const imgSrc = catImg || userPhotoMap[item.id] || null;
                    const owned = ownedMap[item.id];
                    return (
                    <div key={item.id} className="card" onClick={() => setSelected(item)}
                      style={{ cursor: "pointer", position: "relative" }}
                      onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,.12)"; }}
                      onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}>
                      {owned?.collection && (
                        <div style={{ position: "absolute", top: 6, right: 6, background: "#16a34a", color: "#fff",
                          borderRadius: 20, fontSize: 10, fontWeight: 700, padding: "2px 7px", zIndex: 1 }}>
                          ✓ {owned.collection > 1 ? `${owned.collection}×` : ""}
                        </div>
                      )}
                      {imgSrc
                        ? <img src={imgSrc} alt={item.name} style={{ width: "100%", height: compact ? 90 : 130, objectFit: "contain", background: "#f8fafc", borderRadius: 8, marginBottom: 8 }} />
                        : <div style={{ width: "100%", height: compact ? 70 : 80, background: "#f8fafc", borderRadius: 8,
                            marginBottom: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: compact ? 24 : 32 }}>
                            {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"}
                          </div>
                      }
                      <strong style={{ display: "block", fontSize: compact ? 11 : 13, marginBottom: 2, lineHeight: 1.3 }}>{item.name}</strong>
                      <div style={{ fontSize: 11, color: "#64748b", marginTop: 2 }}>
                        {[geoFilter.countryName ? `${flagEmoji(geoFilter.countryCode)} ${geoFilter.countryName}` : null, item.year].filter(Boolean).join(" · ")}
                      </div>
                      {item.denomination && !compact && <div className="tag" style={{ marginTop: 6, fontSize: 11 }}>{item.denomination}</div>}
                    </div>
                    );
                  })}
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                  {items.map(item => {
                    const catImg = item.image_url ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url) : null;
                    const imgSrc = catImg || userPhotoMap[item.id] || null;
                    const owned = ownedMap[item.id];
                    return (
                      <div key={item.id} onClick={() => setSelected(item)}
                        style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px",
                          background: owned?.collection ? "#f0fdf4" : "#fff",
                          border: `1px solid ${owned?.collection ? "#86efac" : "#e2e8f0"}`,
                          borderRadius: 10, cursor: "pointer" }}
                        onMouseEnter={e => { e.currentTarget.style.opacity = "0.85"; }}
                        onMouseLeave={e => { e.currentTarget.style.opacity = "1"; }}>
                        <div style={{ width: 52, height: 52, flexShrink: 0, borderRadius: 8, overflow: "hidden",
                          background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center" }}>
                          {imgSrc
                            ? <img src={imgSrc} alt={item.name} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                            : <span style={{ fontSize: 24 }}>{{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"}</span>
                          }
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{item.name}</div>
                          <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
                            {[geoFilter.countryName ? `${flagEmoji(geoFilter.countryCode)} ${geoFilter.countryName}` : null, item.year].filter(Boolean).join(" · ")}
                          </div>
                        </div>
                        {item.denomination && <div className="tag" style={{ fontSize: 11, flexShrink: 0 }}>{item.denomination}</div>}
                        {owned?.collection && (
                          <span style={{ fontSize: 11, fontWeight: 700, background: "#f0fdf4", color: "#16a34a",
                            padding: "2px 8px", borderRadius: 20, flexShrink: 0 }}>
                            ✓{owned.collection > 1 ? ` ${owned.collection}×` : ""}
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {selected && (
        <CatalogDetailModal
          item={selected}
          countryName={geoFilter.countryName || null}
          countryCode={geoFilter.countryCode || null}
          periodName={geoFilter.periodName || null}
          onClose={() => setSelected(null)}
        />
      )}

      {showRecognize && (
        <RecognizeModal
          defaultSection={null}
          onClose={() => setShowRecognize(false)}
        />
      )}
    </div>
  );
}

