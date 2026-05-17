import { useState, useRef, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";

const TWO_SIDED = ["coins", "medals", "banknotes"];

function ImageUploadBox({ label, preview, fileRef, onChange }) {
  const { t } = useTranslation();
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontWeight: 600, fontSize: 13, color: "#555", marginBottom: 6 }}>{label}</div>
      <div
        onClick={() => fileRef.current.click()}
        style={{
          border: "2px dashed #cbd5e1", borderRadius: 12,
          minHeight: 160, display: "flex", alignItems: "center", justifyContent: "center",
          cursor: "pointer", overflow: "hidden", background: "#f8fafc",
        }}
      >
        {preview
          ? <img src={preview} alt={label} style={{ maxHeight: 200, maxWidth: "100%", borderRadius: 8 }} />
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

function LoadingSpinner({ seconds }) {
  const { t } = useTranslation();
  return (
    <div style={{ textAlign: "center", padding: "24px 0" }}>
      <div style={{ fontSize: 36, marginBottom: 12, animation: "spin 1s linear infinite", display: "inline-block" }}>⏳</div>
      <div style={{ fontWeight: 600, marginBottom: 4 }}>{t("recognize.analyzing")}</div>
      <div style={{ fontSize: 13, color: "#94a3b8" }}>{seconds}s — {t("recognize.hint")}</div>
    </div>
  );
}

export default function Recognize() {
  const { type } = useParams();
  const nav = useNavigate();
  const { t } = useTranslation();
  const isTwoSided = TWO_SIDED.includes(type);

  const obverseRef = useRef();
  const reverseRef = useRef();

  const [obverseFile, setObverseFile] = useState(null);
  const [obversePreview, setObversePreview] = useState(null);
  const [reverseFile, setReverseFile] = useState(null);
  const [reversePreview, setReversePreview] = useState(null);

  const [loading, setLoading] = useState(false);
  const [elapsed, setElapsed] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [addedType, setAddedType] = useState(null); // "collection" | "trade" | "wishlist"
  const [adding, setAdding] = useState(null);
  const [purchasePrice, setPurchasePrice] = useState("");
  const [manualMode, setManualMode] = useState(false);
  const [manual, setManual] = useState({
    custom_name: "", custom_year: "", custom_country: "",
    custom_denomination: "", custom_material: "", notes: "", condition: "",
  });

  useEffect(() => {
    if (!loading) { setElapsed(0); return; }
    const t = setInterval(() => setElapsed(s => s + 1), 1000);
    return () => clearInterval(t);
  }, [loading]);

  function onObverse(e) {
    const f = e.target.files[0];
    if (!f) return;
    setObverseFile(f); setObversePreview(URL.createObjectURL(f));
    setResult(null); setAddedType(null); setError(""); setManualMode(false);
  }

  function onReverse(e) {
    const f = e.target.files[0];
    if (!f) return;
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
      const { data } = await api.post(`/recognize?section=${type}`, fd);
      setResult(data);
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
    setAdding(itemType);
    setError("");
    const coinCat = result?.coin_category || "circulation";
    const price = purchasePrice && itemType !== "wishlist" ? parseFloat(purchasePrice) : null;

    let catalogItemId = null;
    try {
      const catPayload = {
        section: type,
        name: result.name,
        year: result.year,
        country: result.country,
        denomination: result.denomination,
        material: result.material,
        diameter_mm: result.diameter_mm,
        weight_g: result.weight_g,
        mint: result.mint,
        mintage: result.mintage,
        description: result.description,
        obverse_description: result.obverse_description,
        reverse_description: result.reverse_description,
        catalog_number: result.catalog_number,
        perforation: result.perforation,
        color: result.color,
        coin_category: coinCat,
      };
      const { data: catItem } = await api.post("/catalog/from-recognition", catPayload);
      catalogItemId = catItem.id;
    } catch {
      // Country or period not found — save as custom
    }

    try {
      const collPayload = catalogItemId
        ? { section: type, catalog_item_id: catalogItemId, coin_category: coinCat, item_type: itemType, purchase_price: price }
        : {
            section: type, coin_category: coinCat, item_type: itemType, purchase_price: price,
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
        section: type,
        name: manual.custom_name,
        year: manual.custom_year,
        country: manual.custom_country,
        denomination: manual.custom_denomination,
        material: manual.custom_material,
        coin_category: "circulation",
      });
      catalogItemId = catItem.id;
    } catch {
      // Country/period not found — save as custom
    }

    try {
      const collPayload = catalogItemId
        ? { section: type, catalog_item_id: catalogItemId, coin_category: "circulation",
            item_type: itemType, purchase_price: price, condition: manual.condition, notes: manual.notes }
        : { section: type, item_type: itemType, purchase_price: price, ...manual };

      const { data: created } = await api.post("/collection", collPayload);
      await uploadFile(created.id, obverseFile, "obverse");
      if (isTwoSided && reverseFile) await uploadFile(created.id, reverseFile, "reverse");
      setAddedType(itemType);
    } catch (err) {
      setError(err.response?.data?.detail || t("recognize.error"));
    } finally {
      setAdding(null);
    }
  }

  return (
    <div style={{ paddingTop: 24, maxWidth: 640, margin: "0 auto" }}>
<div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 24 }}>
        <button onClick={() => nav(-1)} style={{ background: "none", border: "none", fontSize: 22 }}>←</button>
        <h1 style={{ fontWeight: 800, fontSize: 22 }}>📷 {t("recognize.title")} — {t(`sections.${type}`)}</h1>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        {isTwoSided ? (
          <>
            <div style={{ fontSize: 13, color: "#64748b", marginBottom: 12 }}>
              {t("recognize.obverseLabel")} + {t("recognize.reverseLabel")}
            </div>
            <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
              <ImageUploadBox label={t("recognize.obverseLabel")} preview={obversePreview} fileRef={obverseRef} onChange={onObverse} />
              <ImageUploadBox label={t("recognize.reverseLabel")} preview={reversePreview} fileRef={reverseRef} onChange={onReverse} />
            </div>
          </>
        ) : (
          <div style={{ marginBottom: 16 }}>
            <ImageUploadBox label={t("recognize.stampLabel")} preview={obversePreview} fileRef={obverseRef} onChange={onObverse} />
          </div>
        )}

        {loading ? (
          <LoadingSpinner seconds={elapsed} />
        ) : (
          <div style={{ display: "flex", gap: 8 }}>
            <button
              className="btn btn-primary"
              style={{ flex: 1 }}
              onClick={recognize}
              disabled={!obverseFile}
            >
              {t("recognize.recognize")}
            </button>
            <button
              className="btn btn-outline"
              style={{ flex: 1 }}
              onClick={() => { setManualMode(true); setResult(null); }}
            >
              {t("recognize.manual")}
            </button>
          </div>
        )}

        {isTwoSided && !reverseFile && obverseFile && !loading && (
          <p style={{ fontSize: 12, color: "#94a3b8", marginTop: 6, textAlign: "center" }}>
            {t("recognize.canRecognizeWithout")}
          </p>
        )}
        {error && (
          <div style={{ marginTop: 12, background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: 12 }}>
            <strong style={{ color: "#dc2626" }}>{t("recognize.error")}:</strong>
            <p style={{ color: "#dc2626", fontSize: 14, marginTop: 4 }}>{error}</p>
          </div>
        )}
      </div>

      {result && (
        <div className="card" style={{ marginBottom: 20 }}>
          <h3 style={{ marginBottom: 12, fontWeight: 700 }}>
            {result.recognized ? t("recognize.recognized") : t("recognize.notRecognized")}
          </h3>
          {result.recognized ? (
            <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse" }}>
              <tbody>
                {[
                  [t("fields.name"), result.name],
                  [t("fields.year"), result.year],
                  [t("fields.country"), result.country],
                  [t("fields.denomination"), result.denomination],
                  [t("fields.material"), result.material],
                  [t("fields.diameter"), result.diameter_mm && `${result.diameter_mm} mm`],
                  [t("fields.weight"), result.weight_g && `${result.weight_g} g`],
                  [t("fields.mint"), result.mint],
                  [t("fields.mintage"), result.mintage],
                  [t("fields.obverse"), result.obverse_description],
                  [t("fields.reverse"), result.reverse_description],
                  [t("fields.catalogNo"), result.catalog_number],
                  [t("fields.description"), result.description],
                  [t("fields.category"), result.coin_category === "circulation" ? t("coinCategories.circulation")
                    : result.coin_category === "commemorative" ? t("coinCategories.commemorative")
                    : result.coin_category === "collector" ? t("coinCategories.collector")
                    : result.coin_category],
                  [t("fields.notes"), result.notes],
                ].filter(([, v]) => v && v !== "unknown").map(([k, v]) => (
                  <tr key={k} style={{ borderBottom: "1px solid #f1f5f9" }}>
                    <td style={{ padding: "6px 0", fontWeight: 600, color: "#64748b", width: "40%", verticalAlign: "top" }}>{k}</td>
                    <td style={{ padding: "6px 0" }}>{v}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p style={{ color: "#64748b" }}>{result.notes || "AI nevarēja atpazīt priekšmetu."}</p>
          )}
          {addedType ? (
            <div style={{ textAlign: "center", marginTop: 16 }}>
              <div style={{ fontSize: 28 }}>
                {addedType === "collection" ? "✅" : addedType === "trade" ? "🔄" : "⭐"}
              </div>
              <p style={{ color: "#16a34a", fontWeight: 700 }}>
                {addedType === "collection" ? t("recognize.added")
                  : addedType === "trade" ? t("catalog.addedTrade")
                  : t("catalog.addedWishlist")}
              </p>
            </div>
          ) : (
            <div style={{ marginTop: 16 }}>
              <div style={{ marginBottom: 10, padding: "10px 12px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 4 }}>
                  {t("fields.myPrice")} (€)
                </label>
                <input type="number" min="0" step="0.01" placeholder="0.00"
                  value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)}
                  style={{ width: 120, padding: "6px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 14 }} />
                <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 3 }}>{t("catalog.priceHint")}</div>
              </div>
              <button className="btn btn-success" style={{ width: "100%", marginBottom: 6 }}
                onClick={() => saveItem("collection")} disabled={!!adding}>
                {adding === "collection" ? "..." : `➕ ${t("recognize.addToCollection")}`}
              </button>
              <div style={{ display: "flex", gap: 6 }}>
                <button onClick={() => saveItem("trade")} disabled={!!adding}
                  style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                    border: "1.5px solid #f59e0b", background: "#fffbeb", color: "#92400e", fontWeight: 600 }}>
                  {adding === "trade" ? "..." : `🔄 ${t("catalog.addTrade")}`}
                </button>
                <button onClick={() => saveItem("wishlist")} disabled={!!adding}
                  style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                    border: "1.5px solid #8b5cf6", background: "#f5f3ff", color: "#5b21b6", fontWeight: 600 }}>
                  {adding === "wishlist" ? "..." : `⭐ ${t("catalog.addWishlist")}`}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {manualMode && (
        <div className="card">
          <h3 style={{ marginBottom: 14, fontWeight: 700 }}>{t("recognize.manual")}</h3>
          <div className="form-group">
            <label>{t("fields.name")}</label>
            <input value={manual.custom_name} onChange={e => setManual(m => ({ ...m, custom_name: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.year")} <span style={{ fontSize: 11, color: "#94a3b8" }}>({t("recognize.yearHint")})</span></label>
            <input value={manual.custom_year} placeholder={t("recognize.yearPlaceholder")} onChange={e => setManual(m => ({ ...m, custom_year: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.country")} <span style={{ fontSize: 11, color: "#94a3b8" }}>({t("recognize.countryHint")})</span></label>
            <input value={manual.custom_country} placeholder={t("recognize.countryPlaceholder")} onChange={e => setManual(m => ({ ...m, custom_country: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.denomination")}</label>
            <input value={manual.custom_denomination} onChange={e => setManual(m => ({ ...m, custom_denomination: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.material")}</label>
            <input value={manual.custom_material} onChange={e => setManual(m => ({ ...m, custom_material: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.condition")}</label>
            <input value={manual.condition} placeholder={t("recognize.conditionPlaceholder")} onChange={e => setManual(m => ({ ...m, condition: e.target.value }))} />
          </div>
          <div className="form-group">
            <label>{t("fields.notes")}</label>
            <input value={manual.notes} onChange={e => setManual(m => ({ ...m, notes: e.target.value }))} />
          </div>
          {addedType ? (
            <div style={{ textAlign: "center", marginTop: 8 }}>
              <div style={{ fontSize: 24 }}>
                {addedType === "collection" ? "✅" : addedType === "trade" ? "🔄" : "⭐"}
              </div>
              <p style={{ color: "#16a34a", fontWeight: 700 }}>
                {addedType === "collection" ? t("recognize.added")
                  : addedType === "trade" ? t("catalog.addedTrade")
                  : t("catalog.addedWishlist")}
              </p>
            </div>
          ) : (
            <div>
              <div style={{ marginBottom: 10, padding: "10px 12px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0" }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 4 }}>
                  {t("fields.myPrice")} (€)
                </label>
                <input type="number" min="0" step="0.01" placeholder="0.00"
                  value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)}
                  style={{ width: 120, padding: "6px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 14 }} />
              </div>
              <button className="btn btn-success" style={{ width: "100%", marginBottom: 6 }}
                onClick={() => addManual("collection")} disabled={!!adding}>
                {adding === "collection" ? "..." : `➕ ${t("recognize.addToCollection")}`}
              </button>
              <div style={{ display: "flex", gap: 6 }}>
                <button onClick={() => addManual("trade")} disabled={!!adding}
                  style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                    border: "1.5px solid #f59e0b", background: "#fffbeb", color: "#92400e", fontWeight: 600 }}>
                  {adding === "trade" ? "..." : `🔄 ${t("catalog.addTrade")}`}
                </button>
                <button onClick={() => addManual("wishlist")} disabled={!!adding}
                  style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                    border: "1.5px solid #8b5cf6", background: "#f5f3ff", color: "#5b21b6", fontWeight: 600 }}>
                  {adding === "wishlist" ? "..." : `⭐ ${t("catalog.addWishlist")}`}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
