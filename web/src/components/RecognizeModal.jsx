import { useState, useRef, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import api from "../api";

const TWO_SIDED = ["coins", "medals", "banknotes"];
const CONDITIONS = ["UNC", "XF", "VF", "F", "VG", "G", "AG"];
const SECTIONS_LIST = [
  { key: "coins",     icon: "🪙", label: "Monētas" },
  { key: "medals",    icon: "🏅", label: "Medaļas" },
  { key: "stamps",    icon: "📮", label: "Pastmarkas" },
  { key: "banknotes", icon: "💵", label: "Banknotes" },
];

function UploadBox({ label, preview, fileRef, onChange }) {
  const { t } = useTranslation();
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontWeight: 600, fontSize: 13, color: "#555", marginBottom: 6 }}>{label}</div>
      <div onClick={() => fileRef.current.click()} style={{
        border: "2px dashed #cbd5e1", borderRadius: 12, minHeight: 130,
        display: "flex", alignItems: "center", justifyContent: "center",
        cursor: "pointer", overflow: "hidden", background: "#f8fafc",
      }}>
        {preview
          ? <img src={preview} alt={label} style={{ maxHeight: 160, maxWidth: "100%", borderRadius: 8 }} />
          : <div style={{ textAlign: "center", color: "#94a3b8", padding: 16 }}>
              <div style={{ fontSize: 32 }}>📷</div>
              <div style={{ fontSize: 13 }}>{t("recognize.upload")}</div>
            </div>
        }
      </div>
      <input ref={fileRef} type="file" accept="image/*" capture="environment" onChange={onChange} style={{ display: "none" }} />
    </div>
  );
}

export default function RecognizeModal({ defaultSection, onClose }) {
  const { t } = useTranslation();
  const qc = useQueryClient();

  const [section, setSection] = useState(defaultSection || null);
  const isTwoSided = TWO_SIDED.includes(section);

  const obverseRef = useRef();
  const reverseRef = useRef();
  const [obverseFile, setObverseFile]     = useState(null);
  const [obversePreview, setObversePreview] = useState(null);
  const [reverseFile, setReverseFile]     = useState(null);
  const [reversePreview, setReversePreview] = useState(null);

  const [loading, setLoading]     = useState(false);
  const [elapsed, setElapsed]     = useState(0);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState("");
  const [addedType, setAddedType] = useState(null);
  const [adding, setAdding]       = useState(null);
  const [purchasePrice, setPurchasePrice] = useState("");
  const [coinCategory, setCoinCategory] = useState("circulation");
  const [manualMode, setManualMode] = useState(false);
  const [manual, setManual] = useState({
    custom_name: "", custom_year: "", custom_country: "",
    custom_denomination: "", custom_material: "", notes: "", condition: "",
  });

  useEffect(() => {
    if (!loading) { setElapsed(0); return; }
    const timer = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => clearInterval(timer);
  }, [loading]);

  function onObverse(e) {
    const f = e.target.files[0]; if (!f) return;
    setObverseFile(f); setObversePreview(URL.createObjectURL(f));
    setResult(null); setAddedType(null); setError(""); setManualMode(false);
  }
  function onReverse(e) {
    const f = e.target.files[0]; if (!f) return;
    setReverseFile(f); setReversePreview(URL.createObjectURL(f));
    setResult(null); setAddedType(null); setError("");
  }

  async function recognize() {
    if (!obverseFile) return;
    setLoading(true); setError(""); setResult(null);
    try {
      const fd = new FormData();
      fd.append("obverse", obverseFile);
      if (isTwoSided && reverseFile) fd.append("reverse", reverseFile);
      const { data } = await api.post(`/recognize?section=${section}`, fd);
      setResult(data);
      setCoinCategory(data.coin_category || "circulation");
      if (!data.recognized) setManualMode(true);
    } catch (err) {
      if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setError("Pieprasījums aizņēma pārāk ilgi. Mēģini vēlreiz vai izmanto mazāku attēlu.");
      } else if (err.response?.status === 401) {
        setError("Sesija beigusies — lūdzu ielogojies vēlreiz.");
      } else if (!err.response) {
        setError(t("recognize.cannotConnect"));
      } else {
        setError(`${t("recognize.error")}: ${err.response?.data?.detail || err.message}`);
      }
      setManualMode(true);
    } finally {
      setLoading(false);
    }
  }

  async function uploadFile(itemId, file, side) {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    await api.post(`/collection/${itemId}/image?side=${side}`, fd);
  }

  async function saveItem(itemType) {
    setAdding(itemType); setError("");
    const coinCat = coinCategory;
    const price = purchasePrice && itemType !== "wishlist" ? parseFloat(purchasePrice) : null;
    let catalogItemId = null;
    try {
      const { data: catItem } = await api.post("/catalog/from-recognition", {
        section, name: result.name, year: result.year, country: result.country,
        denomination: result.denomination, material: result.material,
        diameter_mm: result.diameter_mm, weight_g: result.weight_g,
        mint: result.mint, mintage: result.mintage, description: result.description,
        obverse_description: result.obverse_description, reverse_description: result.reverse_description,
        catalog_number: result.catalog_number, perforation: result.perforation,
        color: result.color, coin_category: coinCat,
      });
      catalogItemId = catItem.id;
    } catch {}
    try {
      const collPayload = catalogItemId
        ? { section, catalog_item_id: catalogItemId, coin_category: coinCat, item_type: itemType, purchase_price: price }
        : {
            section, coin_category: coinCat, item_type: itemType, purchase_price: price,
            custom_name: result.name, custom_year: result.year, custom_country: result.country,
            custom_denomination: result.denomination, custom_material: result.material,
            custom_description: [
              result.description,
              result.obverse_description && `Priekšpuse: ${result.obverse_description}`,
              result.reverse_description && `Aizmugure: ${result.reverse_description}`,
            ].filter(Boolean).join("\n\n"),
          };
      const { data: created } = await api.post("/collection", collPayload);
      await uploadFile(created.id, obverseFile, "obverse");
      if (isTwoSided && reverseFile) await uploadFile(created.id, reverseFile, "reverse");
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["collection-tree"] });
      setAddedType(itemType);
    } catch (err) {
      setError(err.response?.data?.detail || t("recognize.error"));
    } finally {
      setAdding(null);
    }
  }

  async function addManual(itemType) {
    setAdding(itemType);
    const price = purchasePrice && itemType !== "wishlist" ? parseFloat(purchasePrice) : null;
    let catalogItemId = null;
    try {
      const { data: catItem } = await api.post("/catalog/from-recognition", {
        section, name: manual.custom_name, year: manual.custom_year, country: manual.custom_country,
        denomination: manual.custom_denomination, material: manual.custom_material, coin_category: "circulation",
      });
      catalogItemId = catItem.id;
    } catch {}
    try {
      const collPayload = catalogItemId
        ? { section, catalog_item_id: catalogItemId, coin_category: "circulation",
            item_type: itemType, purchase_price: price, condition: manual.condition, notes: manual.notes }
        : { section, item_type: itemType, purchase_price: price, ...manual };
      const { data: created } = await api.post("/collection", collPayload);
      await uploadFile(created.id, obverseFile, "obverse");
      if (isTwoSided && reverseFile) await uploadFile(created.id, reverseFile, "reverse");
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["collection-tree"] });
      setAddedType(itemType);
    } catch (err) {
      setError(err.response?.data?.detail || t("recognize.error"));
    } finally {
      setAdding(null);
    }
  }

  const inp = { width: "100%", padding: "8px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 13 };

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, width: "100%", maxWidth: 520,
        maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,.3)", padding: 24,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontWeight: 800, fontSize: 18 }}>📷 {t("recognize.title")}</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer", color: "#94a3b8" }}>✕</button>
        </div>

        {/* Section picker */}
        {!section && (
          <div>
            <p style={{ color: "#64748b", fontSize: 14, marginBottom: 12 }}>Izvēlies sadaļu:</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {SECTIONS_LIST.map(s => (
                <button key={s.key} onClick={() => setSection(s.key)} style={{
                  padding: "14px 16px", borderRadius: 10, border: "2px solid #e2e8f0",
                  background: "#f8fafc", cursor: "pointer", fontWeight: 700, fontSize: 15,
                  textAlign: "left", display: "flex", alignItems: "center", gap: 10,
                }}>
                  <span style={{ fontSize: 24 }}>{s.icon}</span>
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {section && (
          <>
            {/* Section badge + change link */}
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <span style={{ fontSize: 13, fontWeight: 700, color: "#64748b" }}>
                {SECTIONS_LIST.find(s => s.key === section)?.icon} {t(`sections.${section}`)}
              </span>
              {!defaultSection && (
                <button onClick={() => {
                  setSection(null); setResult(null); setManualMode(false); setError("");
                  setObverseFile(null); setObversePreview(null); setReverseFile(null); setReversePreview(null);
                }} style={{ fontSize: 12, color: "#2563eb", background: "none", border: "none", cursor: "pointer" }}>
                  mainīt
                </button>
              )}
            </div>

            {/* Upload */}
            <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
              <UploadBox
                label={isTwoSided ? t("recognize.obverseLabel") : t("recognize.stampLabel")}
                preview={obversePreview} fileRef={obverseRef} onChange={onObverse}
              />
              {isTwoSided && (
                <UploadBox
                  label={t("recognize.reverseLabel")}
                  preview={reversePreview} fileRef={reverseRef} onChange={onReverse}
                />
              )}
            </div>

            {/* Recognize / Manual buttons */}
            {loading ? (
              <div style={{ textAlign: "center", padding: "16px 0" }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>⏳</div>
                <div style={{ fontWeight: 600 }}>{t("recognize.analyzing")}</div>
                <div style={{ fontSize: 13, color: "#94a3b8" }}>{elapsed}s — {t("recognize.hint")}</div>
              </div>
            ) : (
              <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
                <button className="btn btn-primary" style={{ flex: 1 }} onClick={recognize} disabled={!obverseFile}>
                  {t("recognize.recognize")}
                </button>
                <button className="btn btn-outline" style={{ flex: 1 }} onClick={() => { setManualMode(true); setResult(null); }}>
                  {t("recognize.manual")}
                </button>
              </div>
            )}

            {error && (
              <div style={{ marginBottom: 12, background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: 12 }}>
                <strong style={{ color: "#dc2626" }}>{t("recognize.error")}:</strong>
                <p style={{ color: "#dc2626", fontSize: 14, marginTop: 4 }}>{error}</p>
              </div>
            )}

            {/* AI result */}
            {result && (
              <div style={{ background: "#f8fafc", borderRadius: 10, padding: 14, marginBottom: 12 }}>
                <div style={{ fontWeight: 700, marginBottom: 10 }}>
                  {result.recognized ? t("recognize.recognized") : t("recognize.notRecognized")}
                </div>
                {result.recognized ? (
                  <table style={{ width: "100%", fontSize: 13, borderCollapse: "collapse" }}>
                    <tbody>
                      {[
                        [t("fields.name"), result.name],
                        [t("fields.year"), result.year],
                        [t("fields.country"), result.country],
                        [t("fields.denomination"), result.denomination],
                        [t("fields.material"), result.material],
                        [t("fields.catalogNo"), result.catalog_number],
                        [t("fields.description"), result.description],
                      ].filter(([, v]) => v && v !== "unknown").map(([k, v]) => (
                        <tr key={k} style={{ borderBottom: "1px solid #e2e8f0" }}>
                          <td style={{ padding: "5px 0", fontWeight: 600, color: "#64748b", width: "40%", verticalAlign: "top" }}>{k}</td>
                          <td style={{ padding: "5px 0" }}>{v}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  <p style={{ color: "#64748b", fontSize: 13 }}>{result.notes || "AI nevarēja atpazīt priekšmetu."}</p>
                )}

                {/* Coin category override — shown for coins section */}
                {section === "coins" && (
                  <div style={{ marginTop: 12, borderTop: "1px solid #e2e8f0", paddingTop: 12 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#64748b", marginBottom: 8, textTransform: "uppercase", letterSpacing: .4 }}>
                      Kategorija
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                      {[
                        { key: "circulation",   icon: "💰", label: "Apgrozījuma" },
                        { key: "commemorative", icon: "🏛️", label: "Piemiņas" },
                        { key: "collector",     icon: "⭐", label: "Kolekcijas" },
                        { key: "tokens",        icon: "🎰", label: "Žetoni" },
                      ].map(cat => (
                        <button key={cat.key} onClick={() => setCoinCategory(cat.key)} style={{
                          padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 12,
                          textAlign: "left", display: "flex", alignItems: "center", gap: 6,
                          border: `2px solid ${coinCategory === cat.key ? "#2563eb" : "#e2e8f0"}`,
                          background: coinCategory === cat.key ? "#eff6ff" : "#fff",
                          color: coinCategory === cat.key ? "#1d4ed8" : "#374151",
                        }}>
                          {cat.icon} {cat.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Add to collection after recognition — only when recognized */}
            {result && result.recognized && !addedType && (
              <AddButtons purchasePrice={purchasePrice} onPriceChange={setPurchasePrice}
                adding={adding} onSave={saveItem} t={t} />
            )}

            {/* Success */}
            {addedType && (
              <div style={{ textAlign: "center", padding: "16px 0" }}>
                <div style={{ fontSize: 36, marginBottom: 8 }}>
                  {addedType === "collection" ? "✅" : addedType === "trade" ? "🔄" : "⭐"}
                </div>
                <p style={{ fontWeight: 700, color: "#16a34a", fontSize: 16, marginBottom: 16 }}>
                  {addedType === "collection" ? t("recognize.added")
                    : addedType === "trade" ? t("catalog.addedTrade")
                    : t("catalog.addedWishlist")}
                </p>
                <button className="btn btn-outline" onClick={onClose}>{t("collection.close")}</button>
              </div>
            )}

            {/* Manual form */}
            {manualMode && !addedType && (
              <div style={{ marginTop: 12, borderTop: "1px solid #e2e8f0", paddingTop: 16 }}>
                <h3 style={{ fontWeight: 700, marginBottom: 12, fontSize: 15 }}>{t("recognize.manual")}</h3>
                {[
                  [t("fields.name"),        "custom_name"],
                  [t("fields.year"),        "custom_year"],
                  [t("fields.country"),     "custom_country"],
                  [t("fields.denomination"),"custom_denomination"],
                  [t("fields.material"),    "custom_material"],
                ].map(([label, key]) => (
                  <div key={key} style={{ marginBottom: 10 }}>
                    <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{label}</label>
                    <input value={manual[key]} onChange={e => setManual(m => ({ ...m, [key]: e.target.value }))} style={inp} />
                  </div>
                ))}
                <div style={{ marginBottom: 10 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{t("fields.condition")}</label>
                  <select value={manual.condition} onChange={e => setManual(m => ({ ...m, condition: e.target.value }))} style={inp}>
                    <option value="">—</option>
                    {CONDITIONS.map(c => <option key={c}>{c}</option>)}
                  </select>
                </div>
                <div style={{ marginBottom: 14 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{t("fields.notes")}</label>
                  <input value={manual.notes} onChange={e => setManual(m => ({ ...m, notes: e.target.value }))} style={inp} />
                </div>
                <AddButtons purchasePrice={purchasePrice} onPriceChange={setPurchasePrice}
                  adding={adding} onSave={addManual} t={t} />
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function AddButtons({ purchasePrice, onPriceChange, adding, onSave, t }) {
  return (
    <div>
      <div style={{ marginBottom: 10, padding: "10px 12px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
        <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 4 }}>
          {t("fields.myPrice")} (€)
        </label>
        <input type="number" min="0" step="0.01" placeholder="0.00"
          value={purchasePrice} onChange={e => onPriceChange(e.target.value)}
          style={{ width: 120, padding: "6px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 14 }} />
      </div>
      <button className="btn btn-success" style={{ width: "100%", marginBottom: 6 }}
        onClick={() => onSave("collection")} disabled={!!adding}>
        {adding === "collection" ? "..." : `➕ ${t("recognize.addToCollection")}`}
      </button>
      <div style={{ display: "flex", gap: 6 }}>
        <button onClick={() => onSave("trade")} disabled={!!adding} style={{
          flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
          border: "1.5px solid #f59e0b", background: "#fffbeb", color: "#92400e", fontWeight: 600,
        }}>
          {adding === "trade" ? "..." : `🔄 ${t("catalog.addTrade")}`}
        </button>
        <button onClick={() => onSave("wishlist")} disabled={!!adding} style={{
          flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
          border: "1.5px solid #8b5cf6", background: "#f5f3ff", color: "#5b21b6", fontWeight: 600,
        }}>
          {adding === "wishlist" ? "..." : `⭐ ${t("catalog.addWishlist")}`}
        </button>
      </div>
    </div>
  );
}
