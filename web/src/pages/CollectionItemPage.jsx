import { useState, useRef } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import ZoomableImage from "../components/ZoomableImage";

const BASE = "http://localhost:8001";
const CONDITIONS = ["UNC", "XF", "VF", "F", "VG", "G", "AG"];

function parsePurity(material) {
  if (!material) return null;
  const dec = material.match(/\b0\.(\d{2,4})\b/);
  if (dec) { const v = parseFloat(dec[0]); if (v > 0 && v <= 1) return v; }
  const m = material.match(/\b(\d{3,4})\b/);
  if (m) { const n = parseInt(m[1]); if (n >= 100 && n <= 9999) return n / 1000; }
  return null;
}

const ITEM_TYPES_DEF = [
  { key: "collection", icon: "🏛", color: "#16a34a", bg: "#f0fdf4", border: "#86efac" },
  { key: "trade",      icon: "🔄", color: "#92400e", bg: "#fffbeb", border: "#fcd34d" },
  { key: "wishlist",   icon: "⭐", color: "#5b21b6", bg: "#f5f3ff", border: "#c4b5fd" },
];

function PhotoBox({ label, url, inputRef, onChange, uploading }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 4 }}>{label}</div>
      <div onClick={() => inputRef.current.click()} style={{
        border: "2px dashed #cbd5e1", borderRadius: 10, height: 120, overflow: "hidden",
        display: "flex", alignItems: "center", justifyContent: "center",
        cursor: "pointer", background: "#f8fafc", position: "relative",
      }}>
        {url
          ? <img src={url} alt={label} style={{ width: "100%", height: "100%", objectFit: "contain", background: "#f1f5f9" }} />
          : <div style={{ textAlign: "center", color: "#94a3b8", fontSize: 12 }}>
              <div style={{ fontSize: 24 }}>📷</div>
              <div>Pievienot foto</div>
            </div>
        }
        {uploading && (
          <div style={{ position: "absolute", inset: 0, background: "rgba(255,255,255,.7)",
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20 }}>⏳</div>
        )}
      </div>
      <input ref={inputRef} type="file" accept="image/*" capture="environment"
        onChange={onChange} style={{ display: "none" }} />
    </div>
  );
}

export default function CollectionItemPage() {
  const { id } = useParams();
  const { state } = useLocation();
  const nav = useNavigate();
  const { t } = useTranslation();
  const qc = useQueryClient();

  const { data: fetchedItem } = useQuery({
    queryKey: ["collection-item-page", id],
    queryFn: () => api.get(`/collection/${id}`).then(r => r.data),
    enabled: !state?.item,
  });
  const item = state?.item || fetchedItem;

  const [editing, setEditing] = useState(false);
  const [adding, setAdding] = useState(null);
  const [form, setForm] = useState(null);

  if (item && !form) {
    setForm({
      condition: item.condition || "",
      notes: item.notes || "",
      quantity: item.quantity || 1,
      purchase_price: item.purchase_price ?? "",
    });
  }

  const { data: priceData } = useQuery({
    queryKey: ["avg-price", item?.catalog_item?.id],
    queryFn: () => api.get(`/catalog/items/${item.catalog_item.id}/avg_price`).then(r => r.data),
    enabled: !!item?.catalog_item?.id,
  });

  const ci = item?.catalog_item;
  const materialLower = (ci?.material || item?.custom_material || "").toLowerCase();
  const metalType = materialLower.includes("gold") ? "gold"
    : materialLower.includes("silver") ? "silver"
    : null;
  const metalPurity = parsePurity(ci?.material || item?.custom_material || "");
  const { data: metalPrice } = useQuery({
    queryKey: ["metal-price", metalType],
    queryFn: () => api.get(`/catalog/metal-price?metal=${metalType}`).then(r => r.data),
    enabled: !!metalType,
    staleTime: 5 * 60 * 1000,
  });
  const [metalUnit, setMetalUnit] = useState("oz");
  const [metalCurrency, setMetalCurrency] = useState("USD");

  function formatMetalPrice(data) {
    if (!data) return "...";
    const OZ_TO_G = 31.1035;
    let price = data.price_usd_oz;
    if (metalUnit === "g") price = price / OZ_TO_G;
    if (metalCurrency === "EUR") price = price / data.eur_usd_rate;
    const sym = metalCurrency === "EUR" ? "€" : "$";
    const unit = metalUnit === "g" ? "g" : "oz";
    return `${sym}${price.toFixed(metalUnit === "g" ? 3 : 2)}/${unit}`;
  }

  function formatMinValue(data) {
    if (!data || !ci?.weight_g) return null;
    const weight = parseFloat(ci.weight_g);
    if (!weight || isNaN(weight)) return null;
    const OZ_TO_G = 31.1035;
    const purity = metalPurity ?? 1;
    const valueUSD = weight * purity * (data.price_usd_oz / OZ_TO_G);
    const valueEUR = valueUSD / data.eur_usd_rate;
    return `$${valueUSD.toFixed(2)}  /  €${valueEUR.toFixed(2)}`;
  }

  const { data: sameItems = [] } = useQuery({
    queryKey: ["collection-for-catalog", item?.catalog_item?.id],
    queryFn: () => api.get("/collection", { params: { catalog_item_id: item.catalog_item.id } }).then(r => r.data),
    enabled: !!item?.catalog_item?.id,
    retry: false,
  });
  const byType = {};
  for (const si of sameItems) byType[si.item_type] = si;

  const [obverseUrl, setObverseUrl] = useState(null);
  const [reverseUrl, setReverseUrl] = useState(null);
  const [uploadingObverse, setUploadingObverse] = useState(false);
  const [uploadingReverse, setUploadingReverse] = useState(false);
  const obverseRef = useRef();
  const reverseRef = useRef();

  // Set URLs from item once loaded
  if (item && obverseUrl === null && item.user_image) setObverseUrl(BASE + item.user_image);
  if (item && reverseUrl === null && item.user_image_reverse) setReverseUrl(BASE + item.user_image_reverse);

  async function uploadPhoto(file, side, setUploading, setUrl) {
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post(`/collection/${item.id}/image?side=${side}`, fd);
      setUrl(BASE + data.image_url);
      qc.invalidateQueries({ queryKey: ["collection"] });
    } finally { setUploading(false); }
  }

  const save = useMutation({
    mutationFn: () => api.patch(`/collection/${item.id}`, {
      ...form,
      purchase_price: form.purchase_price !== "" ? parseFloat(form.purchase_price) : null,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["avg-price", item?.catalog_item?.id] });
      setEditing(false);
    },
  });

  const remove = useMutation({
    mutationFn: () => api.delete(`/collection/${item.id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collection"] });
      nav(-1);
    },
  });

  async function addOrIncrement(itemType) {
    if (!item.catalog_item?.id) return;
    setAdding(itemType);
    try {
      const existing = byType[itemType];
      if (existing) {
        await api.patch(`/collection/${existing.id}`, { quantity: (existing.quantity || 1) + 1 });
      } else {
        await api.post("/collection", {
          section: item.section,
          catalog_item_id: item.catalog_item.id,
          coin_category: item.coin_category || "circulation",
          item_type: itemType,
        });
      }
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["collection-for-catalog", item.catalog_item.id] });
    } finally { setAdding(null); }
  }

  if (!item || !form) {
    return (
      <div style={{ maxWidth: 640, margin: "40px auto", padding: "0 24px", textAlign: "center", color: "#94a3b8" }}>
        Ielādē...
      </div>
    );
  }

  const name = ci?.name || item.custom_name || "Nezināms";
  const year = ci?.year || item.custom_year;
  const countryCode = item.country?.code;
  const country = item.country?.name_lv || item.custom_country;
  const countryDisplay = country ? `${flagEmoji(countryCode)} ${country}` : null;
  const period = item.period?.name;
  const isTwoSided = ["coins", "medals", "banknotes"].includes(item.section);
  const sectionIcons = { coins: "🪙", medals: "🏅", stamps: "📮", banknotes: "💵" };

  const catObUrl = ci?.image_url ? (ci.image_url.startsWith("http") ? ci.image_url : BASE + ci.image_url) : null;
  const catRevUrl = ci?.image_url_reverse ? (ci.image_url_reverse.startsWith("http") ? ci.image_url_reverse : BASE + ci.image_url_reverse) : null;
  const showObUrl = obverseUrl || catObUrl;
  const showRevUrl = reverseUrl || catRevUrl;
  const hasAnyPhoto = showObUrl || showRevUrl;

  const fields = [
    [t("fields.name"), name],
    [t("fields.year"), year],
    [t("fields.country"), countryDisplay],
    [t("fields.period"), period],
    [t("fields.denomination"), ci?.denomination || item.custom_denomination],
    [t("fields.material"), ci?.material || item.custom_material],
    [t("fields.diameter"), ci?.diameter_mm && `${ci.diameter_mm} mm`],
    [t("fields.weight"), ci?.weight_g && `${ci.weight_g} g`],
    [t("fields.mint"), ci?.mint],
    [t("fields.mintage"), ci?.mintage],
    [t("fields.catalogNo"), ci?.catalog_number],
    [t("fields.description"), ci?.description || item.custom_description],
    [t("fields.condition"), item.condition],
    [t("fields.quantity"), item.quantity > 1 ? item.quantity : null],
    [t("fields.notes"), item.notes],
    [t("fields.myPrice"), item.purchase_price != null ? `€${Number(item.purchase_price).toFixed(2)}` : null],
    [t("fields.avgPrice"), priceData?.avg_price != null
      ? `€${priceData.avg_price.toFixed(2)} (${priceData.count} ${t("fields.collectors")})`
      : null],
  ].filter(([, v]) => v && v !== "unknown");

  return (
    <div style={{ maxWidth: 640, margin: "0 auto", padding: "0 0 48px" }}>
      <button onClick={() => nav(-1)} style={{
        background: "none", border: "none", cursor: "pointer",
        display: "flex", alignItems: "center", gap: 6,
        color: "#2563eb", fontWeight: 600, fontSize: 14,
        padding: "16px 0 12px",
      }}>
        ← Atpakaļ
      </button>

      <div style={{ background: "#fff", borderRadius: 16, boxShadow: "0 2px 16px rgba(0,0,0,.08)", overflow: "hidden" }}>
        {/* Foto */}
        {isTwoSided ? (
          <div style={{ background: "#f1f5f9", display: "flex", gap: 2, minHeight: 200 }}>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 12 }}>
              {showObUrl
                ? <ZoomableImage src={showObUrl} alt="obverse" style={{ maxHeight: 200, maxWidth: "100%", objectFit: "contain" }} />
                : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 40 }}>🪙</div><div style={{ fontSize: 11 }}>Averse</div></div>}
              {showObUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Averse</div>}
            </div>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 12 }}>
              {showRevUrl
                ? <ZoomableImage src={showRevUrl} alt="reverse" style={{ maxHeight: 200, maxWidth: "100%", objectFit: "contain" }} />
                : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 40 }}>🪙</div><div style={{ fontSize: 11 }}>Reverse</div></div>}
              {showRevUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Reverse</div>}
            </div>
          </div>
        ) : hasAnyPhoto ? (
          <ZoomableImage src={showObUrl} alt={name}
            style={{ width: "100%", maxHeight: 320, objectFit: "contain", background: "#f1f5f9" }} />
        ) : (
          <div style={{ background: "#f1f5f9", height: 120, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 56 }}>
            {sectionIcons[item.section] || "📋"}
          </div>
        )}

        <div style={{ padding: 24 }}>
          <div style={{ display: "flex", gap: 6, marginBottom: 8, flexWrap: "wrap" }}>
            <div className="tag">{sectionIcons[item.section]} {t(`sections.${item.section}`)}</div>
            {ci?.admin_edited && (
              <div style={{ fontSize: 11, background: "#fef3c7", color: "#92400e", padding: "2px 8px", borderRadius: 20, fontWeight: 700 }}>
                🔒 Admin
              </div>
            )}
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 800, lineHeight: 1.3, marginBottom: 4 }}>{name}</h1>
          <div style={{ color: "#64748b", fontSize: 14, marginBottom: 20 }}>
            {[countryDisplay, year].filter(Boolean).join(" · ")}
          </div>

          <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse", marginBottom: 16 }}>
            <tbody>
              {fields.map(([k, v]) => (
                <tr key={k} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "8px 0", fontWeight: 600, color: "#64748b", width: "42%", verticalAlign: "top" }}>{k}</td>
                  <td style={{ padding: "8px 0", whiteSpace: "pre-wrap" }}>{String(v)}</td>
                </tr>
              ))}
              {metalType && (
                <tr style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "8px 0", fontWeight: 600, color: "#64748b", width: "42%", verticalAlign: "middle" }}>
                    {metalType === "gold" ? t("fields.goldPrice") : t("fields.silverPrice")}
                  </td>
                  <td style={{ padding: "8px 0" }}>
                    <span style={{ marginRight: 8 }}>{formatMetalPrice(metalPrice)}</span>
                    <span style={{ display: "inline-flex", gap: 3 }}>
                      {["oz", "g"].map(u => (
                        <button key={u} onClick={() => setMetalUnit(u)} style={{
                          padding: "1px 7px", fontSize: 11, borderRadius: 6, cursor: "pointer",
                          border: "1.5px solid #cbd5e1",
                          background: metalUnit === u ? "#1e40af" : "#f8fafc",
                          color: metalUnit === u ? "#fff" : "#475569", fontWeight: 600,
                        }}>{u}</button>
                      ))}
                      {["USD", "EUR"].map(c => (
                        <button key={c} onClick={() => setMetalCurrency(c)} style={{
                          padding: "1px 7px", fontSize: 11, borderRadius: 6, cursor: "pointer",
                          border: "1.5px solid #cbd5e1",
                          background: metalCurrency === c ? "#1e40af" : "#f8fafc",
                          color: metalCurrency === c ? "#fff" : "#475569", fontWeight: 600,
                        }}>{c}</button>
                      ))}
                    </span>
                  </td>
                </tr>
              )}
              {metalType && formatMinValue(metalPrice) && (
                <tr style={{ borderBottom: "1px solid #f1f5f9", background: metalType === "gold" ? "#fffbeb" : "#f8faff" }}>
                  <td style={{ padding: "8px 0", fontWeight: 600, color: "#64748b", width: "42%", verticalAlign: "middle" }}>
                    {t("fields.metalMinValue")}
                  </td>
                  <td style={{ padding: "8px 0", fontWeight: 700,
                    color: metalType === "gold" ? "#92400e" : "#1e40af" }}>
                    {formatMinValue(metalPrice)}
                    <span style={{ marginLeft: 8, fontSize: 11, fontWeight: 400, color: "#94a3b8" }}>
                      ({ci.weight_g} g{metalPurity ? ` × ${(metalPurity * 1000).toFixed(0)}/1000` : ""} × {metalType === "gold" ? t("fields.goldPrice") : t("fields.silverPrice")})
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          {/* Kolekcijas tipa statusi */}
          {ci?.id && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 16 }}>
              {ITEM_TYPES_DEF.map(({ key, icon, color, bg, border }) => {
                const existing = byType[key];
                const qty = existing?.quantity || 1;
                return (
                  <div key={key} style={{
                    display: "flex", alignItems: "center", gap: 10,
                    padding: "9px 12px", borderRadius: 10,
                    background: existing ? bg : "#f8fafc",
                    border: `1.5px solid ${existing ? border : "#e2e8f0"}`,
                  }}>
                    <div style={{ flex: 1, fontWeight: 700, fontSize: 13, color: existing ? color : "#94a3b8" }}>
                      {icon} {t(`itemTypes.${key}`)}
                      {existing && <span style={{ marginLeft: 8, fontWeight: 600 }}>· {qty} gab.</span>}
                    </div>
                    <button onClick={() => addOrIncrement(key)} disabled={adding === key} style={{
                      padding: "5px 14px", borderRadius: 8, border: "none", cursor: "pointer",
                      fontWeight: 700, fontSize: 12,
                      background: existing ? color : "#2563eb", color: "#fff",
                      opacity: adding === key ? 0.6 : 1, flexShrink: 0,
                    }}>
                      {adding === key ? "..." : existing ? "+ 1" : t("collection2.addItem")}
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {/* Rediģēšanas forma */}
          {editing ? (
            <div style={{ background: "#f8fafc", borderRadius: 10, padding: 16, marginBottom: 12 }}>
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>{t("collection.photos")}</div>
                <div style={{ display: "flex", gap: 10 }}>
                  <PhotoBox label={t("collection.obverse")} url={obverseUrl} inputRef={obverseRef}
                    uploading={uploadingObverse}
                    onChange={e => { const f = e.target.files[0]; if (f) uploadPhoto(f, "obverse", setUploadingObverse, setObverseUrl); }} />
                  {isTwoSided && (
                    <PhotoBox label={t("collection.reverse")} url={reverseUrl} inputRef={reverseRef}
                      uploading={uploadingReverse}
                      onChange={e => { const f = e.target.files[0]; if (f) uploadPhoto(f, "reverse", setUploadingReverse, setReverseUrl); }} />
                  )}
                </div>
              </div>
              <div className="form-group">
                <label>{t("collection.condition")}</label>
                <select value={form.condition} onChange={e => setForm(f => ({ ...f, condition: e.target.value }))}>
                  <option value="">—</option>
                  {CONDITIONS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div className="form-group">
                <label>{t("fields.myPrice")} (€)</label>
                <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                  <input type="number" min={0} step="0.01" placeholder="0.00"
                    value={form.purchase_price}
                    onChange={e => setForm(f => ({ ...f, purchase_price: e.target.value }))}
                    style={{ width: 120 }} />
                  {priceData?.avg_price != null && (
                    <span style={{ fontSize: 12, color: "#64748b" }}>
                      {t("fields.avgPrice")}: <strong>€{priceData.avg_price.toFixed(2)}</strong>
                    </span>
                  )}
                </div>
              </div>
              <div className="form-group">
                <label>{t("collection.quantity")}</label>
                <input type="number" min={1} value={form.quantity}
                  onChange={e => setForm(f => ({ ...f, quantity: +e.target.value }))} />
              </div>
              <div className="form-group">
                <label>{t("collection.notes")}</label>
                <textarea rows={3} value={form.notes}
                  onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                  style={{ width: "100%", padding: "8px 12px", borderRadius: 8, border: "1.5px solid #ddd", fontSize: 14 }} />
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <button className="btn btn-primary" onClick={() => save.mutate()} style={{ flex: 1 }}>{t("collection.save")}</button>
                <button className="btn btn-outline" onClick={() => setEditing(false)} style={{ flex: 1 }}>{t("collection.close")}</button>
              </div>
            </div>
          ) : (
            <button className="btn btn-outline" style={{ width: "100%", marginBottom: 8 }} onClick={() => setEditing(true)}>
              {t("collection.edit")}
            </button>
          )}

          <button className="btn btn-danger" style={{ width: "100%" }}
            onClick={() => { if (window.confirm("Dzēst priekšmetu?")) remove.mutate(); }}>
            {t("collection.delete")}
          </button>
        </div>
      </div>
    </div>
  );
}
