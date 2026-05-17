import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import FlagIcon from "../components/FlagIcon";
import GeoNav from "../components/GeoNav";
import ZoomableImage from "../components/ZoomableImage";
import RecognizeModal from "../components/RecognizeModal";
import MatrixView from "../components/MatrixView";

const BASE = "http://localhost:8001";
const CONDITIONS = ["UNC", "XF", "VF", "F", "VG", "G", "AG"];

function PhotoBox({ label, url, inputRef, onChange, uploading }) {
  const { t } = useTranslation();
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
              <div>{t("collection.addPhoto")}</div>
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

const ITEM_TYPES_DEF = [
  { key: "collection", icon: "🏛", label: "Kolekcija",      color: "#16a34a", bg: "#f0fdf4", border: "#86efac" },
  { key: "trade",      icon: "🔄", label: "Apmaiņa",         color: "#92400e", bg: "#fffbeb", border: "#fcd34d" },
  { key: "wishlist",   icon: "⭐", label: "Vēlmju saraksts", color: "#5b21b6", bg: "#f5f3ff", border: "#c4b5fd" },
];

function DetailModal({ item, onClose, onDelete }) {
  const { t } = useTranslation();
  const [editing, setEditing] = useState(false);
  const [adding, setAdding] = useState(null);
  const [form, setForm] = useState({
    condition: item.condition || "",
    notes: item.notes || "",
    quantity: item.quantity || 1,
    purchase_price: item.purchase_price ?? "",
  });

  const { data: priceData } = useQuery({
    queryKey: ["avg-price", item.catalog_item?.id],
    queryFn: () => api.get(`/catalog/items/${item.catalog_item.id}/avg_price`).then(r => r.data),
    enabled: !!item.catalog_item?.id,
  });

  // All items linked to same catalog item (for type status display)
  const { data: sameItems = [] } = useQuery({
    queryKey: ["collection-for-catalog", item.catalog_item?.id],
    queryFn: () => api.get("/collection", { params: { catalog_item_id: item.catalog_item.id } }).then(r => r.data),
    enabled: !!item.catalog_item?.id,
    retry: false,
  });
  const byType = {};
  for (const si of sameItems) byType[si.item_type] = si;
  const [obverseUrl, setObverseUrl] = useState(item.user_image ? BASE + item.user_image : null);
  const [reverseUrl, setReverseUrl] = useState(item.user_image_reverse ? BASE + item.user_image_reverse : null);
  const [uploadingObverse, setUploadingObverse] = useState(false);
  const [uploadingReverse, setUploadingReverse] = useState(false);
  const obverseRef = useRef();
  const reverseRef = useRef();
  const qc = useQueryClient();

  const isTwoSided = ["coins", "medals", "banknotes"].includes(item.section);

  async function uploadPhoto(file, side, setUploading, setUrl) {
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post(`/collection/${item.id}/image?side=${side}`, fd);
      setUrl(BASE + data.image_url);
      qc.invalidateQueries({ queryKey: ["collection"] });
    } finally {
      setUploading(false);
    }
  }

  const save = useMutation({
    mutationFn: () => api.patch(`/collection/${item.id}`, {
      ...form,
      purchase_price: form.purchase_price !== "" ? parseFloat(form.purchase_price) : null,
    }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["avg-price", item.catalog_item?.id] });
      setEditing(false);
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
      qc.invalidateQueries({ queryKey: ["collection-tree"] });
    } finally {
      setAdding(null);
    }
  }

  const ci = item.catalog_item;
  const name = ci?.name || item.custom_name || "Nezināms";
  const year = ci?.year || item.custom_year;
  const countryCode = item.country?.code;
  const country = item.country?.name_lv || item.custom_country;
  const countryDisplay = country ? `${flagEmoji(countryCode)} ${country}` : null;
  const period = item.period?.name;

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

  const catObUrl = ci?.image_url ? (ci.image_url.startsWith("http") ? ci.image_url : BASE + ci.image_url) : null;
  const catRevUrl = ci?.image_url_reverse ? (ci.image_url_reverse.startsWith("http") ? ci.image_url_reverse : BASE + ci.image_url_reverse) : null;

  // Prefer user-uploaded photo, fall back to catalog photo
  const showObUrl = obverseUrl || catObUrl;
  const showRevUrl = reverseUrl || catRevUrl;
  const hasAnyPhoto = showObUrl || showRevUrl;

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, width: "100%", maxWidth: 540,
        maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,.3)",
      }}>
        {/* Photos header */}
        {isTwoSided ? (
          <div style={{
            background: "#f1f5f9", borderRadius: "16px 16px 0 0",
            display: "flex", gap: 2, overflow: "hidden", minHeight: 160,
          }}>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
              {showObUrl
                ? <ZoomableImage src={showObUrl} alt="obverse" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>🪙</div><div style={{ fontSize: 11 }}>Averse</div></div>
              }
              {showObUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Averse</div>}
            </div>
            <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 8 }}>
              {showRevUrl
                ? <ZoomableImage src={showRevUrl} alt="reverse" style={{ maxHeight: 150, maxWidth: "100%", objectFit: "contain" }} />
                : <div style={{ color: "#94a3b8", textAlign: "center" }}><div style={{ fontSize: 32 }}>🪙</div><div style={{ fontSize: 11 }}>Reverse</div></div>
              }
              {showRevUrl && <div style={{ fontSize: 10, color: "#94a3b8", marginTop: 4 }}>Reverse</div>}
            </div>
          </div>
        ) : hasAnyPhoto ? (
          <ZoomableImage src={showObUrl} alt={name}
            style={{ width: "100%", maxHeight: 280, objectFit: "contain", background: "#f1f5f9", borderRadius: "16px 16px 0 0" }} />
        ) : (
          <div style={{ background: "#f1f5f9", borderRadius: "16px 16px 0 0", height: 100,
            display: "flex", alignItems: "center", justifyContent: "center", fontSize: 48 }}>
            {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"}
          </div>
        )}

        <div style={{ padding: 24 }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
            <div>
              <div style={{ display: "flex", gap: 6, marginBottom: 6, flexWrap: "wrap" }}>
                <div className="tag">
                  {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"} {t(`sections.${item.section}`)}
                </div>
                {ci?.admin_edited && (
                  <div style={{ fontSize: 11, background: "#fef3c7", color: "#92400e",
                    padding: "2px 8px", borderRadius: 20, fontWeight: 700 }}>
                    🔒 Admin
                  </div>
                )}
              </div>
              <h2 style={{ fontSize: 20, fontWeight: 800, lineHeight: 1.2 }}>{name}</h2>
              <div style={{ color: "#64748b", fontSize: 14, marginTop: 4 }}>
                {[countryDisplay, year].filter(Boolean).join(" · ")}
              </div>
            </div>
            <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 24, cursor: "pointer", color: "#94a3b8" }}>✕</button>
          </div>

          <table style={{ width: "100%", fontSize: 14, borderCollapse: "collapse", marginBottom: 16 }}>
            <tbody>
              {fields.map(([k, v]) => (
                <tr key={k} style={{ borderBottom: "1px solid #f1f5f9" }}>
                  <td style={{ padding: "7px 0", fontWeight: 600, color: "#64748b", width: "42%", verticalAlign: "top" }}>{k}</td>
                  <td style={{ padding: "7px 0" }}>{String(v)}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Collection status per type — only for catalog-linked items */}
          {item.catalog_item?.id && (
            <div style={{ display: "flex", flexDirection: "column", gap: 6, marginBottom: 12 }}>
              {ITEM_TYPES_DEF.map(({ key, icon, label, color, bg, border }) => {
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
                      {icon} {label}
                      {existing && <span style={{ marginLeft: 8, fontWeight: 600 }}>· {qty} gab.</span>}
                    </div>
                    <button
                      onClick={() => addOrIncrement(key)}
                      disabled={adding === key}
                      style={{
                        padding: "5px 14px", borderRadius: 8, border: "none", cursor: "pointer",
                        fontWeight: 700, fontSize: 12,
                        background: existing ? color : "#2563eb", color: "#fff",
                        opacity: adding === key ? 0.6 : 1, flexShrink: 0,
                      }}
                    >
                      {adding === key ? "..." : existing ? "+ 1" : "Pievienot"}
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          {editing ? (
            <div style={{ background: "#f8fafc", borderRadius: 10, padding: 16, marginBottom: 12 }}>
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 8 }}>{t("collection.photos")}</div>
                <div style={{ display: "flex", gap: 10 }}>
                  <PhotoBox
                    label={t("collection.obverse")}
                    url={obverseUrl}
                    inputRef={obverseRef}
                    uploading={uploadingObverse}
                    onChange={e => { const f = e.target.files[0]; if (f) uploadPhoto(f, "obverse", setUploadingObverse, setObverseUrl); }}
                  />
                  {isTwoSided && (
                    <PhotoBox
                      label={t("collection.reverse")}
                      url={reverseUrl}
                      inputRef={reverseRef}
                      uploading={uploadingReverse}
                      onChange={e => { const f = e.target.files[0]; if (f) uploadPhoto(f, "reverse", setUploadingReverse, setReverseUrl); }}
                    />
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
            onClick={() => { onDelete(item.id); onClose(); }}>
            {t("collection.delete")}
          </button>
        </div>
      </div>
    </div>
  );
}


const ITEM_TYPES = [
  { key: "collection", label: "🏛 Kolekcija",     color: "#2563eb", bg: "#eff6ff", border: "#bfdbfe" },
  { key: "trade",      label: "🔄 Apmaiņa",        color: "#92400e", bg: "#fffbeb", border: "#fcd34d" },
  { key: "wishlist",   label: "⭐ Vēlmju saraksts", color: "#5b21b6", bg: "#f5f3ff", border: "#c4b5fd" },
];

const SECTIONS_LIST = [
  { key: "coins",     icon: "🪙", label: "Monētas" },
  { key: "medals",    icon: "🏅", label: "Medaļas" },
  { key: "stamps",    icon: "📮", label: "Pastmarkas" },
  { key: "banknotes", icon: "💵", label: "Banknotes" },
];

function ManualAddModal({ onClose }) {
  const { t } = useTranslation();
  const qc = useQueryClient();
  const obverseRef = useRef();
  const reverseRef = useRef();
  const [step, setStep] = useState("section"); // "section" | "form"
  const [section, setSection] = useState("");
  const [addedType, setAddedType] = useState(null);
  const [adding, setAdding] = useState(null);
  const [obverseFile, setObverseFile] = useState(null);
  const [obversePreview, setObversePreview] = useState(null);
  const [reverseFile, setReverseFile] = useState(null);
  const [reversePreview, setReversePreview] = useState(null);
  const [form, setForm] = useState({
    name: "", year: "", country: "", denomination: "", material: "",
    condition: "", notes: "", purchase_price: "", coin_category: "circulation",
  });

  const isTwoSided = ["coins", "medals", "banknotes"].includes(section);
  const inp = { width: "100%", padding: "8px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 13 };

  function pickFile(e, setSrc, setFile) {
    const f = e.target.files[0];
    if (!f) return;
    setFile(f);
    setSrc(URL.createObjectURL(f));
  }

  async function uploadPhoto(itemId, file, side) {
    if (!file) return;
    const fd = new FormData();
    fd.append("file", file);
    await api.post(`/collection/${itemId}/image?side=${side}`, fd);
  }

  async function save(itemType) {
    setAdding(itemType);
    try {
      const payload = { section, coin_category: form.coin_category, item_type: itemType,
          custom_name: form.name, custom_year: form.year, custom_country: form.country,
          custom_denomination: form.denomination, custom_material: form.material,
          condition: form.condition, notes: form.notes,
          purchase_price: itemType !== "wishlist" && form.purchase_price ? parseFloat(form.purchase_price) : null };

      const { data: created } = await api.post("/collection", payload);
      await uploadPhoto(created.id, obverseFile, "obverse");
      if (isTwoSided) await uploadPhoto(created.id, reverseFile, "reverse");

      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["collection-tree"] });
      setAddedType(itemType);
    } catch (err) {
      alert(err.response?.data?.detail || "Kļūda");
    } finally {
      setAdding(null);
    }
  }

  return (
    <div onClick={onClose} style={{
      position: "fixed", inset: 0, background: "rgba(0,0,0,.55)",
      display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000, padding: 16,
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        background: "#fff", borderRadius: 16, width: "100%", maxWidth: 480,
        maxHeight: "90vh", overflowY: "auto", boxShadow: "0 20px 60px rgba(0,0,0,.3)", padding: 24,
      }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
          <h2 style={{ fontWeight: 800, fontSize: 18 }}>✏️ {t("recognize.manual")}</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 22, cursor: "pointer", color: "#94a3b8" }}>✕</button>
        </div>

        {step === "section" && (
          <div>
            <p style={{ color: "#64748b", fontSize: 14, marginBottom: 16 }}>Izvēlies sadaļu:</p>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {SECTIONS_LIST.map(s => (
                <button key={s.key} onClick={() => { setSection(s.key); setStep("form"); }}
                  style={{ padding: "14px 16px", borderRadius: 10, border: "2px solid #e2e8f0",
                    background: "#f8fafc", cursor: "pointer", fontWeight: 700, fontSize: 15,
                    textAlign: "left", display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: 24 }}>{s.icon}</span> {s.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === "form" && !addedType && (
          <div>
            {/* Coin category selector */}
            {section === "coins" && (
              <div style={{ marginBottom: 14 }}>
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
                    <button key={cat.key} onClick={() => setForm(f => ({ ...f, coin_category: cat.key }))}
                      style={{
                        padding: "10px 12px", borderRadius: 8, cursor: "pointer", fontWeight: 600, fontSize: 13,
                        textAlign: "left", display: "flex", alignItems: "center", gap: 8,
                        border: `2px solid ${form.coin_category === cat.key ? "#2563eb" : "#e2e8f0"}`,
                        background: form.coin_category === cat.key ? "#eff6ff" : "#f8fafc",
                        color: form.coin_category === cat.key ? "#1d4ed8" : "#374151",
                      }}>
                      <span>{cat.icon}</span> {cat.label}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Photos */}
            <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
              {[
                { label: isTwoSided ? t("collection.obverse") : t("collection.photos"),
                  preview: obversePreview, ref: obverseRef,
                  onChange: e => pickFile(e, setObversePreview, setObverseFile) },
                ...(isTwoSided ? [{
                  label: t("collection.reverse"),
                  preview: reversePreview, ref: reverseRef,
                  onChange: e => pickFile(e, setReversePreview, setReverseFile),
                }] : []),
              ].map((ph, i) => (
                <div key={i} style={{ flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 600, color: "#64748b", marginBottom: 4 }}>{ph.label}</div>
                  <div onClick={() => ph.ref.current.click()} style={{
                    border: "2px dashed #cbd5e1", borderRadius: 10, height: 110,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    cursor: "pointer", overflow: "hidden", background: "#f8fafc",
                  }}>
                    {ph.preview
                      ? <img src={ph.preview} alt="" style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      : <div style={{ textAlign: "center", color: "#94a3b8", fontSize: 12 }}>
                          <div style={{ fontSize: 24 }}>📷</div>
                          <div>{t("collection.addPhoto")}</div>
                        </div>
                    }
                  </div>
                  <input ref={ph.ref} type="file" accept="image/*" capture="environment"
                    onChange={ph.onChange} style={{ display: "none" }} />
                </div>
              ))}
            </div>

            <div style={{ marginBottom: 14 }}>
              {[
                [t("fields.name"), "name"],
                [t("fields.year"), "year"],
                [t("fields.country") + " (angliski)", "country"],
                [t("fields.denomination"), "denomination"],
                [t("fields.material"), "material"],
              ].map(([label, key]) => (
                <div key={key} style={{ marginBottom: 10 }}>
                  <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{label}</label>
                  <input value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} style={inp} />
                </div>
              ))}
              <div style={{ marginBottom: 10 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{t("fields.condition")}</label>
                <select value={form.condition} onChange={e => setForm(f => ({ ...f, condition: e.target.value }))} style={inp}>
                  <option value="">—</option>
                  {CONDITIONS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>
              <div style={{ marginBottom: 10 }}>
                <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 }}>{t("fields.notes")}</label>
                <textarea rows={2} value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))}
                  style={{ ...inp, resize: "vertical" }} />
              </div>
            </div>

            <div style={{ padding: "10px 12px", background: "#f8fafc", borderRadius: 8, border: "1px solid #e2e8f0", marginBottom: 14 }}>
              <label style={{ fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 4 }}>{t("fields.myPrice")} (€)</label>
              <input type="number" min="0" step="0.01" placeholder="0.00"
                value={form.purchase_price} onChange={e => setForm(f => ({ ...f, purchase_price: e.target.value }))}
                style={{ width: 130, padding: "6px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 14 }} />
              <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 3 }}>{t("catalog.priceHint")}</div>
            </div>

            <button className="btn btn-success" style={{ width: "100%", marginBottom: 6 }}
              onClick={() => save("collection")} disabled={!!adding}>
              {adding === "collection" ? "..." : `➕ ${t("recognize.addToCollection")}`}
            </button>
            <div style={{ display: "flex", gap: 6 }}>
              <button onClick={() => save("trade")} disabled={!!adding}
                style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                  border: "1.5px solid #f59e0b", background: "#fffbeb", color: "#92400e", fontWeight: 600 }}>
                {adding === "trade" ? "..." : `🔄 ${t("catalog.addTrade")}`}
              </button>
              <button onClick={() => save("wishlist")} disabled={!!adding}
                style={{ flex: 1, padding: "8px 10px", borderRadius: 8, cursor: "pointer", fontSize: 13,
                  border: "1.5px solid #8b5cf6", background: "#f5f3ff", color: "#5b21b6", fontWeight: 600 }}>
                {adding === "wishlist" ? "..." : `⭐ ${t("catalog.addWishlist")}`}
              </button>
            </div>
          </div>
        )}

        {addedType && (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <div style={{ fontSize: 40, marginBottom: 10 }}>
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
      </div>
    </div>
  );
}

export default function Collection() {
  const [itemType, setItemType] = useState("collection");
  const [geoFilter, setGeoFilter] = useState({});
  const [filterDenom, setFilterDenom] = useState("");
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [showManual, setShowManual] = useState(false);
  const [showRecognize, setShowRecognize] = useState(false);
  const [layout, setLayout] = useState("3");
  const nav = useNavigate();
  const { t } = useTranslation();
  const qc = useQueryClient();

  const params = { item_type: itemType };
  if (search) params.search = search;

  const { data: allItems = [], isLoading } = useQuery({
    queryKey: ["collection", params],
    queryFn: () => api.get("/collection", { params }).then(r => r.data),
  });

  const denomOptions = [...new Set(
    allItems
      .filter(i => !geoFilter.countryName || (i.country?.name_lv || i.custom_country || "") === geoFilter.countryName)
      .map(i => i.catalog_item?.denomination || i.custom_denomination || "")
      .filter(Boolean)
  )].sort();

  const items = allItems.filter(item => {
    const ci = item.catalog_item;
    const itemCountry = item.country?.name_lv || item.custom_country || "";
    const itemPeriod  = item.period?.name || ci?.period?.name || "";
    const itemDenomVal = ci?.denomination || item.custom_denomination || "";
    if (geoFilter.countryName && itemCountry !== geoFilter.countryName) return false;
    if (geoFilter.periodName  && itemPeriod  !== geoFilter.periodName)  return false;
    if (filterDenom && itemDenomVal !== filterDenom) return false;
    return true;
  });

  const remove = useMutation({
    mutationFn: id => api.delete(`/collection/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["collection"] });
      qc.invalidateQueries({ queryKey: ["collection-tree"] });
    },
  });

  function itemName(item) { return item.catalog_item?.name || item.custom_name || "?"; }
  function itemYear(item) { return item.catalog_item?.year || item.custom_year; }
  function itemDenom(item) { return item.catalog_item?.denomination || item.custom_denomination; }
  function itemCountry(item) {
    const name = item.country?.name_lv || item.custom_country;
    const code = item.country?.code;
    return name ? `${flagEmoji(code)} ${name}` : null;
  }
  function itemImage(item) {
    if (item.user_image) return BASE + item.user_image;
    const url = item.catalog_item?.image_url;
    if (url) return url.startsWith("http") ? url : BASE + url;
    return null;
  }

  const matrixItems = items.map(item => ({
    id: item.id,
    year: item.catalog_item?.year || item.custom_year || "",
    denomination: item.catalog_item?.denomination || item.custom_denomination || "",
    image_url: item.catalog_item?.image_url || null,
    name: item.catalog_item?.name || item.custom_name || "?",
    _original: item,
  }));
  const matrixUserPhotoMap = {};
  for (const item of items) {
    if (item.user_image) matrixUserPhotoMap[item.id] = BASE + item.user_image;
  }

  return (
    <div style={{ paddingTop: 24 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
        <h1 style={{ fontWeight: 800, fontSize: 24 }}>{t("collection.title")}</h1>
        <span style={{ color: "#94a3b8", fontSize: 14 }}>{allItems.length} {t("collection.items")}</span>
        <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
          <button className="btn btn-primary" onClick={() => nav("/")}>
            {t("collection.add")}
          </button>
          <button className="btn btn-outline" onClick={() => setShowRecognize(true)}>
            📷 {t("recognize.title")}
          </button>
          <button className="btn btn-outline" onClick={() => setShowManual(true)}>
            ✏️ {t("recognize.manual")}
          </button>
        </div>
      </div>

      {/* Type tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {ITEM_TYPES.map(tp => (
          <button key={tp.key} onClick={() => { setItemType(tp.key); setSelected(null); }}
            style={{
              padding: "8px 18px", borderRadius: 10, cursor: "pointer", fontWeight: 700, fontSize: 13,
              border: `2px solid ${itemType === tp.key ? tp.border : "#e2e8f0"}`,
              background: itemType === tp.key ? tp.bg : "#fff",
              color: itemType === tp.key ? tp.color : "#64748b",
              transition: "all .15s",
            }}>
            {tp.label}
          </button>
        ))}
      </div>

      <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
        <input placeholder={t("collection.search")} value={search} onChange={e => setSearch(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: 8, border: "1.5px solid #ddd", fontSize: 14, flex: 1, minWidth: 160 }} />
        <select value={filterDenom} onChange={e => setFilterDenom(e.target.value)}
          style={{ padding: "8px 10px", borderRadius: 8, border: "1.5px solid #ddd", fontSize: 14 }}>
          <option value="">Visi nomināli</option>
          {denomOptions.map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <div style={{ display: "flex", border: "1.5px solid #e2e8f0", borderRadius: 8, overflow: "hidden", flexShrink: 0 }}>
          {[["list","≡","Rindas"],["3","⊞","3 kolonnas"],["4","⊟","4 kolonnas"],["5","⋮⋮","5 kolonnas"],["matrix","⊠","Laikmeta tabula"]].map(([mode, icon, title], i, arr) => (
            <button key={mode} onClick={() => setLayout(mode)} title={title} style={{
              padding: "7px 13px", border: "none", cursor: "pointer", fontSize: 18, lineHeight: 1,
              background: layout === mode ? "#2563eb" : "#fff",
              color: layout === mode ? "#fff" : "#64748b",
              borderRight: i < arr.length - 1 ? "1.5px solid #e2e8f0" : "none",
            }}>{icon}</button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", gap: 20, alignItems: "flex-start" }}>
        <GeoNav filter={geoFilter} onSelect={f => { setGeoFilter(f); setSelected(null); }} title={t("collection.title")} />

        <div style={{ flex: 1, minWidth: 0 }}>
          {isLoading && <p style={{ color: "#888" }}>...</p>}

          {!isLoading && items.length === 0 && (
            <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8" }}>
              <div style={{ fontSize: 48, marginBottom: 12 }}>📭</div>
              <p>{allItems.length === 0 ? t("collection.empty") : t("collection.noResults")}</p>
            </div>
          )}

          {layout === "matrix" ? (
            <MatrixView
              items={matrixItems}
              userPhotoMap={matrixUserPhotoMap}
              onSelect={item => setSelected(item._original)}
            />
          ) : layout !== "list" ? (
            <div className={`grid-${layout}`}>
              {items.map(item => {
                const compact = layout === "4" || layout === "5";
                return (
                  <div key={item.id} className="card" onClick={() => setSelected(item)}
                    style={{ cursor: "pointer" }}
                    onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-2px)"; e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,.12)"; }}
                    onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}>
                    {itemImage(item)
                      ? <img src={itemImage(item)} alt={itemName(item)}
                          style={{ width: "100%", height: compact ? 90 : 130, objectFit: "contain", background: "#f8fafc", borderRadius: 8, marginBottom: 10 }} />
                      : <div style={{ width: "100%", height: compact ? 70 : 80, background: "#f8fafc", borderRadius: 8,
                          marginBottom: 10, display: "flex", alignItems: "center", justifyContent: "center", fontSize: compact ? 24 : 32 }}>
                          {{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"}
                        </div>
                    }
                    <strong style={{ display: "block", fontSize: compact ? 11 : 13, marginBottom: 2, lineHeight: 1.3 }}>{itemName(item)}</strong>
                    <div style={{ fontSize: 11, color: "#64748b", marginTop: 3 }}>
                      {[itemCountry(item), itemYear(item)].filter(Boolean).join(" · ")}
                    </div>
                    {itemDenom(item) && !compact && <div className="tag" style={{ marginTop: 6, fontSize: 11 }}>{itemDenom(item)}</div>}
                    {item.condition && (
                      <span style={{ fontSize: 11, fontWeight: 700, background: "#f0fdf4", color: "#16a34a",
                        padding: "2px 8px", borderRadius: 20, marginTop: 4, display: "inline-block" }}>
                        {item.condition}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {items.map(item => (
                <div key={item.id} onClick={() => setSelected(item)}
                  style={{ display: "flex", alignItems: "center", gap: 12, padding: "10px 14px",
                    background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10, cursor: "pointer" }}
                  onMouseEnter={e => { e.currentTarget.style.background = "#f8fafc"; }}
                  onMouseLeave={e => { e.currentTarget.style.background = "#fff"; }}>
                  <div style={{ width: 52, height: 52, flexShrink: 0, borderRadius: 8, overflow: "hidden",
                    background: "#f1f5f9", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    {itemImage(item)
                      ? <img src={itemImage(item)} alt={itemName(item)} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
                      : <span style={{ fontSize: 24 }}>{{ coins:"🪙", medals:"🏅", stamps:"📮", banknotes:"💵" }[item.section] || "📋"}</span>
                    }
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 600, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{itemName(item)}</div>
                    <div style={{ fontSize: 12, color: "#64748b", marginTop: 2 }}>
                      {[itemCountry(item), itemYear(item)].filter(Boolean).join(" · ")}
                    </div>
                  </div>
                  {itemDenom(item) && <div className="tag" style={{ fontSize: 11, flexShrink: 0 }}>{itemDenom(item)}</div>}
                  {item.condition && (
                    <span style={{ fontSize: 11, fontWeight: 700, background: "#f0fdf4", color: "#16a34a",
                      padding: "2px 8px", borderRadius: 20, flexShrink: 0 }}>
                      {item.condition}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {selected && (
        <DetailModal
          item={selected}
          onClose={() => setSelected(null)}
          onDelete={id => { remove.mutate(id); setSelected(null); }}
        />
      )}

      {showManual && (
        <ManualAddModal onClose={() => setShowManual(false)} />
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

