import { useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import ZoomableImage from "../components/ZoomableImage";

const BASE = "http://localhost:8001";

function parsePurity(material) {
  if (!material) return null;
  const dec = material.match(/\b0\.(\d{2,4})\b/);
  if (dec) { const v = parseFloat(dec[0]); if (v > 0 && v <= 1) return v; }
  const m = material.match(/\b(\d{3,4})\b/);
  if (m) { const n = parseInt(m[1]); if (n >= 100 && n <= 9999) return n / 1000; }
  return null;
}

export default function CatalogItemPage() {
  const { id } = useParams();
  const { state } = useLocation();
  const nav = useNavigate();
  const { t } = useTranslation();
  const qc = useQueryClient();
  const token = localStorage.getItem("token");

  const { data: fetchedItem } = useQuery({
    queryKey: ["catalog-item-page", id],
    queryFn: () => api.get(`/catalog/items/${id}`).then(r => r.data),
    enabled: !state?.item,
  });
  const item = state?.item || fetchedItem;

  const { data: periods = [] } = useQuery({
    queryKey: ["all-periods"],
    queryFn: () => api.get("/catalog/periods").then(r => r.data),
    enabled: !state?.periodName && !!item,
  });
  const { data: countries = [] } = useQuery({
    queryKey: ["all-countries"],
    queryFn: () => api.get("/catalog/countries").then(r => r.data),
    enabled: !state?.countryName && !!item,
  });

  const period = periods.find(p => p.id === item?.period_id);
  const country = countries.find(c => c.id === period?.country_id);
  const countryName = state?.countryName || country?.name_lv || null;
  const countryCode = state?.countryCode || country?.code || null;
  const periodName = state?.periodName || period?.name || null;

  const { data: priceData } = useQuery({
    queryKey: ["avg-price", item?.id],
    queryFn: () => api.get(`/catalog/items/${item.id}/avg_price`).then(r => r.data),
    enabled: !!item,
  });

  const materialLower = (item?.material || "").toLowerCase();
  const metalType = materialLower.includes("gold") ? "gold"
    : materialLower.includes("silver") ? "silver"
    : null;
  const metalPurity = parsePurity(item?.material || "");
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
    if (!data || !item?.weight_g) return null;
    const weight = parseFloat(item.weight_g);
    if (!weight || isNaN(weight)) return null;
    const OZ_TO_G = 31.1035;
    const purity = metalPurity ?? 1;
    const valueUSD = weight * purity * (data.price_usd_oz / OZ_TO_G);
    const valueEUR = valueUSD / data.eur_usd_rate;
    return `$${valueUSD.toFixed(2)}  /  €${valueEUR.toFixed(2)}`;
  }

  const { data: userItems = [], refetch: refetchUserItems } = useQuery({
    queryKey: ["collection-for-catalog", item?.id],
    queryFn: () => api.get("/collection", { params: { catalog_item_id: item.id } }).then(r => r.data),
    enabled: !!token && !!item,
    retry: false,
  });
  const userItem = userItems.find(i => i.item_type === "collection");

  const addMutation = useMutation({
    mutationFn: () => api.post("/collection", {
      catalog_item_id: item.id,
      section: item.section,
      coin_category: item.coin_category || "circulation",
      item_type: "collection",
    }),
    onSuccess: () => {
      refetchUserItems();
      qc.invalidateQueries({ queryKey: ["collection"] });
    },
  });

  if (!item) {
    return (
      <div style={{ maxWidth: 640, margin: "40px auto", padding: "0 24px", textAlign: "center", color: "#94a3b8" }}>
        Ielādē...
      </div>
    );
  }

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
    [t("fields.designer"), item.designer],
    [t("fields.engraver"), item.engraver],
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
  const catObUrl = item.image_url ? (item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url) : null;
  const catRevUrl = item.image_url_reverse ? (item.image_url_reverse.startsWith("http") ? item.image_url_reverse : BASE + item.image_url_reverse) : null;
  const obUrl = userObUrl || catObUrl;
  const revUrl = userRevUrl || catRevUrl;

  const sectionIcons = { coins: "🪙", medals: "🏅", stamps: "📮", banknotes: "💵" };

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
        <div style={{ background: "#f1f5f9", display: "flex", gap: 2, overflow: "hidden",
          minHeight: isTwoSided ? 200 : (obUrl ? undefined : 120) }}>
          {isTwoSided ? (
            <>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 12 }}>
                {obUrl
                  ? <ZoomableImage src={obUrl} alt="ob" style={{ maxHeight: 200, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 40 }}>🪙</div><div style={{ fontSize: 11 }}>Averse</div></div>}
                {obUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Averse</div>}
              </div>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 12 }}>
                {revUrl
                  ? <ZoomableImage src={revUrl} alt="rev" style={{ maxHeight: 200, maxWidth: "100%", objectFit: "contain" }} />
                  : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 40 }}>🪙</div><div style={{ fontSize: 11 }}>Reverse</div></div>}
                {revUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Reverse</div>}
              </div>
            </>
          ) : obUrl ? (
            <ZoomableImage src={obUrl} alt={item.name} style={{ width: "100%", maxHeight: 320, objectFit: "contain" }} />
          ) : (
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 56, height: 120 }}>
              {sectionIcons[item.section] || "📷"}
            </div>
          )}
        </div>

        <div style={{ padding: 24 }}>
          <div className="tag" style={{ marginBottom: 8 }}>
            {sectionIcons[item.section]} {t(`sections.${item.section}`)}
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 800, lineHeight: 1.3, marginBottom: 4 }}>{item.name}</h1>
          <div style={{ color: "#64748b", fontSize: 14, marginBottom: 20 }}>
            {[countryDisplay, item.year].filter(Boolean).join(" · ")}
          </div>

          <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse" }}>
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
                      ({item.weight_g} g{metalPurity ? ` × ${(metalPurity * 1000).toFixed(0)}/1000` : ""} × {metalType === "gold" ? t("fields.goldPrice") : t("fields.silverPrice")})
                    </span>
                  </td>
                </tr>
              )}
            </tbody>
          </table>

          <div style={{ marginTop: 20 }}>
            {!token ? (
              <button onClick={() => nav("/login")} style={{
                width: "100%", padding: "11px 0", borderRadius: 10, border: "none",
                background: "#f1f5f9", color: "#374151", fontWeight: 700, fontSize: 15, cursor: "pointer",
              }}>
                🔑 Ieiet, lai pievienotu kolekcijai
              </button>
            ) : userItem ? (
              <div style={{
                display: "flex", alignItems: "center", gap: 8,
                background: "#f0fdf4", border: "1.5px solid #86efac",
                borderRadius: 10, padding: "10px 16px", fontSize: 14,
                color: "#16a34a", fontWeight: 600,
              }}>
                <span style={{ fontSize: 18 }}>✓</span>
                <span>Ir manā kolekcijā</span>
              </div>
            ) : (
              <button onClick={() => addMutation.mutate()} disabled={addMutation.isPending} style={{
                width: "100%", padding: "11px 0", borderRadius: 10, border: "none",
                background: addMutation.isPending ? "#94a3b8" : "#2563eb",
                color: "#fff", fontWeight: 700, fontSize: 15,
                cursor: addMutation.isPending ? "not-allowed" : "pointer",
              }}>
                {addMutation.isPending ? "..." : "➕ Pievienot manai kolekcijai"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
