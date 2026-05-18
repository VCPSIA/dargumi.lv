import { useState, useRef } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../api";
import { flagEmoji } from "../utils/flag";
import MatrixView from "../components/MatrixView";

const BASE = "http://localhost:8001";

const SECTIONS = [
  { type: "coins",     label: "Monētas",    icon: "🪙" },
  { type: "medals",    label: "Medaļas",    icon: "🏅" },
  { type: "stamps",    label: "Pastmarkas", icon: "📮" },
  { type: "banknotes", label: "Banknotes",  icon: "💵" },
];
const COIN_CATS = [
  { value: "circulation",   label: "💰 Apgrozības" },
  { value: "commemorative", label: "🏛️ Piemiņas" },
  { value: "collector",     label: "⭐ Kolekcionēšanas" },
];
const COIN_CAT_LABELS = { circulation: "💰 Apgrozības", commemorative: "🏛️ Piemiņas", collector: "⭐ Kolekcionēšanas" };

// ── shared styles ──────────────────────────────────────────────────────────────
const inp = { width: "100%", padding: "7px 10px", borderRadius: 7, border: "1.5px solid #e2e8f0", fontSize: 13, boxSizing: "border-box" };
const lbl = { fontSize: 12, fontWeight: 600, color: "#64748b", display: "block", marginBottom: 3 };
const card = { background: "#fff", borderRadius: 12, padding: 20, border: "1px solid #e2e8f0", marginBottom: 16 };

function FG({ label, children }) {
  return <div style={{ marginBottom: 10 }}><label style={lbl}>{label}</label>{children}</div>;
}
function Inp({ label, value, onChange, type = "text", placeholder = "" }) {
  return <FG label={label}><input type={type} value={value} onChange={onChange} placeholder={placeholder} style={inp} /></FG>;
}
function Sel({ label, value, onChange, options, placeholder }) {
  return (
    <FG label={label}>
      <select value={value} onChange={onChange} style={inp}>
        {placeholder && <option value="">{placeholder}</option>}
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </FG>
  );
}
function TA({ label, value, onChange, rows = 3 }) {
  return (
    <FG label={label}>
      <textarea rows={rows} value={value} onChange={onChange} style={{ ...inp, resize: "vertical" }} />
    </FG>
  );
}
function Msg({ ok, err }) {
  if (ok) return <div style={{ color: "#16a34a", fontWeight: 700, marginTop: 8 }}>✅ {ok}</div>;
  if (err) return <div style={{ color: "#dc2626", fontWeight: 600, marginTop: 8 }}>⚠️ {err}</div>;
  return null;
}

// ── Cascade selector: continent → country → section → period ──────────────────
function CascadeSelector({ value, onChange, showSection = true, showCoinCat = false }) {
  const { continentId = "", countryId = "", section = "", coinCat = "", periodId = "" } = value;

  const { data: continents = [] } = useQuery({
    queryKey: ["continents"],
    queryFn: () => api.get("/catalog/continents").then(r => r.data),
  });
  const { data: countries = [] } = useQuery({
    queryKey: ["countries", continentId],
    queryFn: () => api.get("/catalog/countries", { params: { continent_id: continentId } }).then(r => r.data),
    enabled: !!continentId,
  });
  const { data: periods = [] } = useQuery({
    queryKey: ["periods", countryId, section],
    queryFn: () => api.get("/catalog/periods", { params: { country_id: countryId, section } }).then(r => r.data),
    enabled: !!countryId && !!section,
  });

  function set(key, val) {
    const next = { ...value, [key]: val };
    if (key === "continentId") { next.countryId = ""; next.periodId = ""; }
    if (key === "countryId")   { next.periodId = ""; }
    if (key === "section")     { next.periodId = ""; }
    onChange(next);
  }

  const isTwoSided = section === "coins" || section === "medals";

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 12px" }}>
      <Sel label="Kontinents" value={continentId} onChange={e => set("continentId", e.target.value)} placeholder="— izvēlēties —"
        options={continents.map(c => ({ value: c.id, label: c.name_lv || c.name }))} />
      <Sel label="Valsts" value={countryId} onChange={e => set("countryId", e.target.value)} placeholder="— izvēlēties —"
        options={countries.map(c => ({ value: c.id, label: `${flagEmoji(c.code)} ${c.name_lv || c.name}` }))} />
      {showSection && (
        <Sel label="Sadaļa" value={section} onChange={e => set("section", e.target.value)} placeholder="— izvēlēties —"
          options={SECTIONS.map(s => ({ value: s.type, label: `${s.icon} ${s.label}` }))} />
      )}
      {showCoinCat && isTwoSided && (
        <Sel label="Kategorija" value={coinCat} onChange={e => set("coinCat", e.target.value)} placeholder="— izvēlēties —"
          options={COIN_CATS.map(c => ({ value: c.value, label: c.label }))} />
      )}
      <Sel label="Periods" value={periodId} onChange={e => set("periodId", e.target.value)} placeholder="— izvēlēties —"
        options={periods.map(p => ({ value: p.id, label: p.name + (p.year_start ? ` (${p.year_start}–${p.year_end ?? "..."})` : "") }))} />
    </div>
  );
}

// ── Item fields form ───────────────────────────────────────────────────────────
function ItemFields({ form, setForm, section }) {
  const isTwoSided  = ["coins", "medals", "banknotes"].includes(section);
  const isStamp     = section === "stamps";
  const isCoinMedal = section === "coins" || section === "medals";
  const f = (label, key, opts = {}) => {
    if (opts.textarea) return <TA key={key} label={label} value={form[key] || ""} onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))} />;
    return <Inp key={key} label={label} value={form[key] || ""} onChange={e => setForm(p => ({ ...p, [key]: e.target.value }))} />;
  };

  return (
    <>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 12px" }}>
        {f("Nosaukums *", "name")}
        {f("Gads", "year")}
        {f("Nominālvērtība", "denomination")}
        {f("Materiāls", "material")}
        {isCoinMedal && f("Diametrs (mm)", "diameter_mm")}
        {isCoinMedal && f("Svars (g)", "weight_g")}
        {!isStamp && f(section === "banknotes" ? "Iespiestuve" : "Kaltuve", "mint")}
        {f("Tirāža", "mintage")}
        {isCoinMedal && f("Mākslinieks", "designer")}
        {isCoinMedal && f("Gravieris", "engraver")}
        {f("Kataloga Nr.", "catalog_number")}
        {isStamp && f("Perforācija", "perforation")}
        {isStamp && f("Krāsa", "color")}
      </div>
      {f("Apraksts", "description", { textarea: true })}
      {isTwoSided && f("Averse apraksts", "obverse_description", { textarea: true })}
      {isTwoSided && f("Reverse apraksts", "reverse_description", { textarea: true })}
    </>
  );
}

// ── Add Continent form ─────────────────────────────────────────────────────────
function AddContinentForm() {
  const qc = useQueryClient();
  const [form, setForm] = useState({ name: "", name_lv: "", code: "" });
  const [msg, setMsg] = useState(null);

  const mut = useMutation({
    mutationFn: () => api.post("/admin/continents", form),
    onSuccess: (r) => {
      setMsg({ ok: `Kontinents "${r.data.name_lv}" pievienots!` });
      setForm({ name: "", name_lv: "", code: "" });
      qc.invalidateQueries({ queryKey: ["continents"] });
    },
    onError: (e) => setMsg({ err: e.response?.data?.detail || "Kļūda" }),
  });

  return (
    <div style={card}>
      <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Pievienot kontinentu</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 120px", gap: "0 12px" }}>
        <Inp label="Nosaukums (EN)" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
        <Inp label="Nosaukums (LV)" value={form.name_lv} onChange={e => setForm(p => ({ ...p, name_lv: e.target.value }))} />
        <Inp label="Kods (EU, AS...)" value={form.code} onChange={e => setForm(p => ({ ...p, code: e.target.value.toUpperCase() }))} />
      </div>
      <button className="btn btn-primary" onClick={() => { setMsg(null); mut.mutate(); }}
        disabled={mut.isPending || !form.name || !form.name_lv || !form.code}>
        {mut.isPending ? "Saglabā..." : "Pievienot"}
      </button>
      <Msg ok={msg?.ok} err={msg?.err} />
    </div>
  );
}

// ── Add Country form ───────────────────────────────────────────────────────────
function AddCountryForm() {
  const qc = useQueryClient();
  const [form, setForm] = useState({ name: "", name_lv: "", code: "", continent_id: "", is_extinct: false });
  const [msg, setMsg] = useState(null);

  const { data: continents = [] } = useQuery({
    queryKey: ["continents"],
    queryFn: () => api.get("/catalog/continents").then(r => r.data),
  });

  const mut = useMutation({
    mutationFn: () => api.post("/admin/countries", { ...form, continent_id: Number(form.continent_id) }),
    onSuccess: (r) => {
      setMsg({ ok: `Valsts "${r.data.name_lv}" pievienota!` });
      setForm(p => ({ name: "", name_lv: "", code: "", continent_id: p.continent_id }));
      qc.invalidateQueries({ queryKey: ["countries"] });
    },
    onError: (e) => setMsg({ err: e.response?.data?.detail || "Kļūda" }),
  });

  return (
    <div style={card}>
      <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Pievienot valsti</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 80px", gap: "0 12px" }}>
        <Inp label="Nosaukums (EN)" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} />
        <Inp label="Nosaukums (LV)" value={form.name_lv} onChange={e => setForm(p => ({ ...p, name_lv: e.target.value }))} />
        <Inp label="ISO kods (LV)" value={form.code} onChange={e => setForm(p => ({ ...p, code: e.target.value.toUpperCase() }))} />
      </div>
      <Sel label="Kontinents" value={form.continent_id} onChange={e => setForm(p => ({ ...p, continent_id: e.target.value }))}
        placeholder="— izvēlēties —"
        options={continents.map(c => ({ value: c.id, label: c.name_lv || c.name }))} />
      <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12, cursor: "pointer", fontSize: 14 }}>
        <input type="checkbox" checked={form.is_extinct} onChange={e => setForm(p => ({ ...p, is_extinct: e.target.checked }))} />
        💀 Izmirusi valsts
      </label>
      <button className="btn btn-primary" onClick={() => { setMsg(null); mut.mutate(); }}
        disabled={mut.isPending || !form.name || !form.name_lv || !form.code || !form.continent_id}>
        {mut.isPending ? "Saglabā..." : "Pievienot"}
      </button>
      <Msg ok={msg?.ok} err={msg?.err} />
    </div>
  );
}

// ── Add Period form ────────────────────────────────────────────────────────────
function AddPeriodForm() {
  const qc = useQueryClient();
  const [form, setForm] = useState({ name: "", year_start: "", year_end: "", country_id: "", continent_id: "", section: "" });
  const [msg, setMsg] = useState(null);

  const { data: continents = [] } = useQuery({
    queryKey: ["continents"],
    queryFn: () => api.get("/catalog/continents").then(r => r.data),
  });
  const { data: countries = [] } = useQuery({
    queryKey: ["countries", form.continent_id],
    queryFn: () => api.get("/catalog/countries", { params: { continent_id: form.continent_id } }).then(r => r.data),
    enabled: !!form.continent_id,
  });

  const mut = useMutation({
    mutationFn: () => api.post("/admin/periods", {
      name: form.name,
      year_start: form.year_start ? Number(form.year_start) : null,
      year_end: form.year_end ? Number(form.year_end) : null,
      country_id: Number(form.country_id),
      section: form.section,
    }),
    onSuccess: (r) => {
      setMsg({ ok: `Periods "${r.data.name}" pievienots!` });
      setForm(p => ({ name: "", year_start: "", year_end: "", country_id: p.country_id, continent_id: p.continent_id, section: p.section }));
      qc.invalidateQueries({ queryKey: ["periods"] });
    },
    onError: (e) => setMsg({ err: e.response?.data?.detail || "Kļūda" }),
  });

  return (
    <div style={card}>
      <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Pievienot periodu</h3>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 12px" }}>
        <Sel label="Kontinents" value={form.continent_id} onChange={e => setForm(p => ({ ...p, continent_id: e.target.value, country_id: "" }))}
          placeholder="— izvēlēties —" options={continents.map(c => ({ value: c.id, label: c.name_lv || c.name }))} />
        <Sel label="Valsts" value={form.country_id} onChange={e => setForm(p => ({ ...p, country_id: e.target.value }))}
          placeholder="— izvēlēties —" options={countries.map(c => ({ value: c.id, label: `${flagEmoji(c.code)} ${c.name_lv || c.name}` }))} />
        <Sel label="Sadaļa" value={form.section} onChange={e => setForm(p => ({ ...p, section: e.target.value }))}
          placeholder="— izvēlēties —" options={SECTIONS.map(s => ({ value: s.type, label: `${s.icon} ${s.label}` }))} />
        <Inp label="Perioda nosaukums" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
          placeholder="piem. Otrā republika" />
        <Inp label="Gads no" value={form.year_start} onChange={e => setForm(p => ({ ...p, year_start: e.target.value }))} type="number" />
        <Inp label="Gads līdz (tukšs = tagad)" value={form.year_end} onChange={e => setForm(p => ({ ...p, year_end: e.target.value }))} type="number" />
      </div>
      <button className="btn btn-primary" onClick={() => { setMsg(null); mut.mutate(); }}
        disabled={mut.isPending || !form.name || !form.country_id || !form.section}>
        {mut.isPending ? "Saglabā..." : "Pievienot"}
      </button>
      <Msg ok={msg?.ok} err={msg?.err} />
    </div>
  );
}

// ── Add Item form ──────────────────────────────────────────────────────────────
function AddItemForm({ onDuplicate, prefill }) {
  const qc = useQueryClient();
  const [mode, setMode] = useState("photo"); // "photo" | "manual"
  const [cascade, setCascade] = useState({ continentId: "", countryId: "", section: "", coinCat: "circulation", periodId: "" });
  const [form, setForm] = useState({});

  // Apply prefill when coming from matrix "+" click
  const [lastPrefill, setLastPrefill] = useState(null);
  if (prefill && prefill !== lastPrefill) {
    setLastPrefill(prefill);
    if (prefill.cascade) setCascade(c => ({ ...c, ...prefill.cascade }));
    if (prefill.form) setForm(f => ({ ...f, ...prefill.form }));
    setMode("manual");
  }
  const [obFile, setObFile] = useState(null);
  const [revFile, setRevFile] = useState(null);
  const [recognizing, setRecognizing] = useState(false);
  const [recognized, setRecognized] = useState(false);
  const [msg, setMsg] = useState(null);
  const obRef = useRef();
  const revRef = useRef();

  const isTwoSided = cascade.section === "coins" || cascade.section === "medals";

  async function recognize() {
    if (!obFile) return;
    setRecognizing(true);
    setMsg(null);
    try {
      const fd = new FormData();
      fd.append("obverse", obFile);
      if (revFile && isTwoSided) fd.append("reverse", revFile);
      const { data } = await api.post(`/recognize?section=${cascade.section || "coins"}`, fd);

      if (!data.recognized) {
        setMsg({ err: data.notes || "AI nevarēja atpazīt priekšmetu." });
        return;
      }

      setForm({
        name: data.name || "",
        year: data.year || "",
        denomination: data.denomination || "",
        material: data.material || "",
        diameter_mm: data.diameter_mm || "",
        weight_g: data.weight_g || "",
        mint: data.mint || "",
        mintage: data.mintage || "",
        designer: data.designer || "",
        engraver: data.engraver || "",
        catalog_number: data.catalog_number || "",
        description: data.description || "",
        obverse_description: data.obverse_description || "",
        reverse_description: data.reverse_description || "",
        perforation: data.perforation || "",
        color: data.color || "",
      });

      const newCascade = { ...cascade };
      if (data.coin_category) newCascade.coinCat = data.coin_category;

      // Auto-fill country + period from recognition result
      if (data.country) {
        const countriesRes = await api.get("/catalog/countries");
        const q = data.country.toLowerCase();
        const found = countriesRes.data.find(c =>
          c.name.toLowerCase() === q ||
          c.name.toLowerCase().includes(q) ||
          q.includes(c.name.toLowerCase())
        );
        if (found) {
          newCascade.continentId = String(found.continent_id);
          newCascade.countryId = String(found.id);
          newCascade.periodId = "";

          const section = cascade.section;
          const yearInt = data.year ? parseInt(data.year) : null;
          const periodsRes = await api.get("/catalog/periods", { params: { country_id: found.id, section } });
          if (periodsRes.data.length > 0) {
            let period = null;
            if (yearInt) {
              period = periodsRes.data.find(p =>
                (!p.year_start || p.year_start <= yearInt) &&
                (!p.year_end || p.year_end >= yearInt)
              );
            }
            if (!period) period = periodsRes.data[periodsRes.data.length - 1];
            newCascade.periodId = String(period.id);
          }
        }
      }

      setCascade(newCascade);
      setRecognized(true);
    } catch {
      setMsg({ err: "Atpazīšana neizdevās" });
    } finally {
      setRecognizing(false);
    }
  }

  const mut = useMutation({
    mutationFn: () => api.post("/admin/catalog", {
      period_id: Number(cascade.periodId),
      section: cascade.section,
      coin_category: cascade.coinCat || "circulation",
      name: form.name || "Nezināms",
      year: form.year || null,
      denomination: form.denomination || null,
      material: form.material || null,
      diameter_mm: form.diameter_mm || null,
      weight_g: form.weight_g || null,
      mint: form.mint || null,
      mintage: form.mintage || null,
      designer: form.designer || null,
      engraver: form.engraver || null,
      catalog_number: form.catalog_number || null,
      description: form.description || null,
      obverse_description: form.obverse_description || null,
      reverse_description: form.reverse_description || null,
      perforation: form.perforation || null,
      color: form.color || null,
    }),
    onSuccess: async (r) => {
      // Upload photos if provided
      if (obFile) {
        const fd = new FormData(); fd.append("file", obFile);
        await api.post(`/admin/catalog/${r.data.id}/image?side=obverse`, fd).catch(() => {});
      }
      if (revFile && isTwoSided) {
        const fd = new FormData(); fd.append("file", revFile);
        await api.post(`/admin/catalog/${r.data.id}/image?side=reverse`, fd).catch(() => {});
      }
      setMsg({ ok: `"${r.data.name}" pievienots katalogam!` });
      setForm({});
      setObFile(null); setRevFile(null);
      setRecognized(false);
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-tree"] });
    },
    onError: (e) => {
      if (e.response?.status === 409) {
        const detail = e.response.data?.detail || "";
        const idMatch = detail.match(/ID:\s*(\d+)/);
        const dupId = idMatch ? Number(idMatch[1]) : null;
        setMsg({ dup: detail, dupId });
      } else {
        setMsg({ err: e.response?.data?.detail || "Kļūda" });
      }
    },
  });

  const canSave = cascade.periodId && cascade.section && (form.name || "").trim();

  const tabBtn = (m, label) => (
    <button onClick={() => { setMode(m); setMsg(null); }} style={{
      padding: "7px 18px", borderRadius: 8, fontWeight: 700, fontSize: 13, cursor: "pointer",
      background: mode === m ? "#2563eb" : "#f1f5f9",
      color: mode === m ? "#fff" : "#374151",
      border: mode === m ? "none" : "1.5px solid #e2e8f0",
    }}>{label}</button>
  );

  function FilePreview({ file, onClear }) {
    if (!file) return null;
    const url = URL.createObjectURL(file);
    return (
      <div style={{ position: "relative", display: "inline-block" }}>
        <img src={url} alt="" style={{ height: 100, borderRadius: 8, objectFit: "contain", background: "#f1f5f9" }} />
        <button onClick={onClear} style={{
          position: "absolute", top: -6, right: -6, width: 20, height: 20, borderRadius: "50%",
          background: "#ef4444", color: "#fff", border: "none", cursor: "pointer", fontSize: 12, lineHeight: "20px", textAlign: "center",
        }}>✕</button>
      </div>
    );
  }

  return (
    <div style={card}>
      <h3 style={{ fontWeight: 700, marginBottom: 16 }}>Pievienot ierakstu katalogam</h3>

      {/* Cascade */}
      <CascadeSelector value={cascade} onChange={setCascade} showSection showCoinCat />

      <hr style={{ border: "none", borderTop: "1px solid #f1f5f9", margin: "14px 0" }} />

      {/* Mode tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {tabBtn("photo", "📷 Foto atpazīšana")}
        {tabBtn("manual", "✏️ Manuāli")}
      </div>

      {mode === "photo" && (
        <>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-end", marginBottom: 12, flexWrap: "wrap" }}>
            <div>
              <div style={lbl}>Averse (priekšpuse) *</div>
              {obFile
                ? <FilePreview file={obFile} onClear={() => { setObFile(null); setRecognized(false); }} />
                : <button onClick={() => obRef.current.click()} style={{
                    padding: "8px 16px", borderRadius: 8, border: "2px dashed #cbd5e1",
                    background: "#f8fafc", color: "#64748b", cursor: "pointer", fontSize: 13,
                  }}>📷 Izvēlēties attēlu</button>
              }
              <input ref={obRef} type="file" accept="image/*" style={{ display: "none" }}
                onChange={e => { setObFile(e.target.files[0]); setRecognized(false); e.target.value = ""; }} />
            </div>
            {isTwoSided && (
              <div>
                <div style={lbl}>Reverse (aizmugure)</div>
                {revFile
                  ? <FilePreview file={revFile} onClear={() => setRevFile(null)} />
                  : <button onClick={() => revRef.current.click()} style={{
                      padding: "8px 16px", borderRadius: 8, border: "2px dashed #cbd5e1",
                      background: "#f8fafc", color: "#64748b", cursor: "pointer", fontSize: 13,
                    }}>📷 Izvēlēties attēlu</button>
                }
                <input ref={revRef} type="file" accept="image/*" style={{ display: "none" }}
                  onChange={e => { setRevFile(e.target.files[0]); e.target.value = ""; }} />
              </div>
            )}
            <button onClick={recognize} disabled={!obFile || recognizing || !cascade.section}
              style={{
                padding: "8px 20px", borderRadius: 8, fontWeight: 700, cursor: "pointer",
                background: obFile && cascade.section ? "#2563eb" : "#e2e8f0",
                color: obFile && cascade.section ? "#fff" : "#94a3b8",
                border: "none", fontSize: 13,
              }}>
              {recognizing ? "⏳ Atpazīst..." : "🔍 Atpazīt"}
            </button>
          </div>

          {recognized && (
            <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 8, padding: "8px 12px", marginBottom: 12, fontSize: 13, color: "#166534" }}>
              ✅ Atpazīšana veiksmīga — pārbaudiet un labojiet laukus zemāk, tad nospiediet "Saglabāt"
            </div>
          )}

          {(recognized || obFile) && (
            <ItemFields form={form} setForm={setForm} section={cascade.section} />
          )}
        </>
      )}

      {mode === "manual" && (
        <ItemFields form={form} setForm={setForm} section={cascade.section} />
      )}

      <Msg ok={msg?.ok} err={msg?.err} />
      {msg?.dup && (
        <div style={{ marginTop: 8, padding: "10px 14px", borderRadius: 8, background: "#fefce8", border: "1.5px solid #fbbf24" }}>
          <div style={{ fontWeight: 700, color: "#92400e", marginBottom: 6 }}>⚠️ Duplikāts</div>
          <div style={{ fontSize: 13, color: "#78350f", marginBottom: 8 }}>{msg.dup}</div>
          {msg.dupId && onDuplicate && (
            <button onClick={() => onDuplicate(msg.dupId)} style={{
              padding: "6px 14px", borderRadius: 7, border: "1.5px solid #d97706",
              background: "#fff7ed", color: "#92400e", cursor: "pointer", fontSize: 13, fontWeight: 600,
            }}>📋 Atvērt esošo ierakstu</button>
          )}
        </div>
      )}

      <button className="btn btn-primary" style={{ marginTop: 12, width: "100%" }}
        onClick={() => { setMsg(null); mut.mutate(); }}
        disabled={mut.isPending || !canSave}>
        {mut.isPending ? "Saglabā..." : "💾 Saglabāt katalogā"}
      </button>
    </div>
  );
}

// ── Structure tab helpers ──────────────────────────────────────────────────────
function ActionBtns({ onEdit, onDelete }) {
  return (
    <div style={{ marginLeft: "auto", display: "flex", gap: 4, flexShrink: 0 }}>
      <button onClick={e => { e.stopPropagation(); onEdit(); }} style={{
        padding: "3px 8px", borderRadius: 5, border: "1px solid #d1d5db",
        background: "#f9fafb", color: "#374151", cursor: "pointer", fontSize: 12,
      }}>✏️</button>
      <button onClick={e => { e.stopPropagation(); onDelete(); }} style={{
        padding: "3px 8px", borderRadius: 5, border: "1px solid #fca5a5",
        background: "#fff1f2", color: "#dc2626", cursor: "pointer", fontSize: 12,
      }}>🗑️</button>
    </div>
  );
}

function InlineEditForm({ fields, bgColor = "#f0f9ff", borderColor = "#bae6fd", indent = 12, onSave, onCancel }) {
  const [form, setForm] = useState(() => Object.fromEntries(fields.map(f => [f.key, f.value ?? ""])));
  const [saving, setSaving] = useState(false);
  const [err, setErr] = useState(null);

  async function save() {
    setSaving(true); setErr(null);
    try {
      const data = {};
      fields.forEach(f => {
        let val = (form[f.key] ?? "").toString().trim();
        if (f.transform) val = f.transform(val);
        data[f.key] = f.keepValue ? val : (val || (f.nullable ? null : undefined));
      });
      await onSave(data);
    } catch (e) {
      setErr(e.response?.data?.detail || "Kļūda");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div style={{ padding: `8px 12px 8px ${indent + 16}px`, background: bgColor, borderTop: `1px solid ${borderColor}` }}>
      <div style={{ display: "flex", gap: 8, alignItems: "flex-end", flexWrap: "wrap" }}>
        {fields.map(f => (
          <div key={f.key} style={{ flex: f.flex || 1, minWidth: f.minWidth || 100 }}>
            <label style={{ ...lbl, fontSize: 11 }}>{f.label}</label>
            {f.options
              ? <select value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))} style={{ ...inp, fontSize: 13, padding: "5px 8px" }}>
                  {f.options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              : <input type={f.type || "text"} value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))} style={{ ...inp, fontSize: 13, padding: "5px 8px" }} />
            }
          </div>
        ))}
        <div style={{ display: "flex", gap: 6, paddingBottom: 1 }}>
          <button onClick={save} disabled={saving} style={{
            padding: "6px 14px", borderRadius: 6, background: "#2563eb", color: "#fff",
            border: "none", cursor: "pointer", fontSize: 13, whiteSpace: "nowrap",
          }}>{saving ? "..." : "Saglabāt"}</button>
          <button onClick={onCancel} style={{
            padding: "6px 10px", borderRadius: 6, background: "#f1f5f9", color: "#374151",
            border: "1px solid #e2e8f0", cursor: "pointer", fontSize: 13,
          }}>Atcelt</button>
        </div>
      </div>
      {err && <div style={{ color: "#dc2626", fontSize: 12, marginTop: 4 }}>⚠️ {err}</div>}
    </div>
  );
}

// ── Structure tab ──────────────────────────────────────────────────────────────
function StructureTab() {
  const qc = useQueryClient();
  const [expCont, setExpCont]       = useState(null);
  const [expCountry, setExpCountry] = useState(null);
  const [editing, setEditing]       = useState(null); // { type, id }
  const [delConfirm, setDelConfirm] = useState(null); // { type, id, name }
  const [apiErr, setApiErr]         = useState(null);

  const { data: continents = [], isLoading } = useQuery({
    queryKey: ["admin-continents"],
    queryFn: () => api.get("/admin/continents").then(r => r.data),
  });
  const { data: countries = [] } = useQuery({
    queryKey: ["admin-countries", expCont],
    queryFn: () => api.get("/admin/countries", { params: { continent_id: expCont } }).then(r => r.data),
    enabled: !!expCont,
  });
  const { data: periods = [] } = useQuery({
    queryKey: ["admin-periods", expCountry],
    queryFn: () => api.get("/admin/periods", { params: { country_id: expCountry } }).then(r => r.data),
    enabled: !!expCountry,
  });

  const deleteMut = useMutation({
    mutationFn: ({ type, id }) => api.delete(`/admin/${type}/${id}`),
    onSuccess: (_, vars) => {
      setDelConfirm(null); setApiErr(null);
      qc.invalidateQueries({ queryKey: ["admin-continents"] });
      qc.invalidateQueries({ queryKey: ["admin-countries"] });
      qc.invalidateQueries({ queryKey: ["admin-periods"] });
      qc.invalidateQueries({ queryKey: ["continents"] });
      qc.invalidateQueries({ queryKey: ["countries"] });
      qc.invalidateQueries({ queryKey: ["periods"] });
      if (vars.type === "continents") setExpCont(p => p === vars.id ? null : p);
      if (vars.type === "countries") setExpCountry(p => p === vars.id ? null : p);
    },
    onError: (e) => { setDelConfirm(null); setApiErr(e.response?.data?.detail || "Nevar dzēst"); },
  });

  function isEditing(type, id) { return editing?.type === type && editing?.id === id; }
  function startEdit(type, id) { setEditing({ type, id }); setApiErr(null); }
  function stopEdit() { setEditing(null); }

  function toggleCont(id) {
    setExpCont(p => p === id ? null : id);
    setExpCountry(null);
    stopEdit();
  }
  function toggleCountry(id) {
    setExpCountry(p => p === id ? null : id);
    stopEdit();
  }

  const rowBase = (indent, highlight) => ({
    display: "flex", alignItems: "center", gap: 8,
    padding: `8px 12px 8px ${indent}px`,
    background: highlight ? "#eff6ff" : "transparent",
    cursor: "pointer", userSelect: "none",
  });

  const sectionIcon  = { coins: "🪙", medals: "🏅", stamps: "📮", banknotes: "💵" };
  const sectionLabel = { coins: "Monētas", medals: "Medaļas", stamps: "Pastmarkas", banknotes: "Banknotes" };
  const sectionBg    = { coins: "#fef9c3", medals: "#fce7f3", stamps: "#ecfdf5", banknotes: "#d1fae5" };
  const sectionClr   = { coins: "#854d0e", medals: "#9d174d", stamps: "#065f46", banknotes: "#065f46" };

  return (
    <div style={{ maxWidth: 860 }}>
      {apiErr && (
        <div style={{ background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 16px", marginBottom: 12, color: "#dc2626", fontSize: 13, display: "flex", gap: 12, alignItems: "center" }}>
          ⚠️ {apiErr}
          <button onClick={() => setApiErr(null)} style={{ marginLeft: "auto", background: "none", border: "none", cursor: "pointer", color: "#dc2626", fontSize: 16 }}>✕</button>
        </div>
      )}

      {delConfirm && (
        <div style={{ background: "#fff7ed", border: "1px solid #fdba74", borderRadius: 8, padding: "12px 16px", marginBottom: 12, display: "flex", alignItems: "center", gap: 12, fontSize: 13 }}>
          <span>⚠️ Dzēst <strong>{delConfirm.name}</strong>?</span>
          <button onClick={() => deleteMut.mutate({ type: delConfirm.type, id: delConfirm.id })}
            disabled={deleteMut.isPending}
            style={{ padding: "4px 14px", borderRadius: 6, background: "#dc2626", color: "#fff", border: "none", cursor: "pointer", fontWeight: 700, fontSize: 13 }}>
            {deleteMut.isPending ? "..." : "Jā, dzēst"}
          </button>
          <button onClick={() => setDelConfirm(null)} style={{ padding: "4px 14px", borderRadius: 6, background: "#f1f5f9", color: "#374151", border: "1px solid #e2e8f0", cursor: "pointer", fontSize: 13 }}>Atcelt</button>
        </div>
      )}

      <div style={{ background: "#fff", borderRadius: 12, border: "1px solid #e2e8f0", overflow: "hidden" }}>
        {isLoading && <p style={{ padding: 20, color: "#888" }}>Ielādē...</p>}

        {continents.map((cont, ci) => (
          <div key={cont.id} style={{ borderTop: ci > 0 ? "1px solid #f1f5f9" : "none" }}>
            {/* Continent row */}
            <div style={rowBase(12, expCont === cont.id)} onClick={() => toggleCont(cont.id)}>
              <span style={{ fontSize: 16 }}>🌍</span>
              <span style={{ fontWeight: 700, fontSize: 14 }}>{cont.name_lv || cont.name}</span>
              <span style={{ fontSize: 11, color: "#9ca3af" }}>{cont.name}</span>
              <span style={{ fontSize: 11, background: "#f1f5f9", color: "#64748b", padding: "1px 7px", borderRadius: 10, fontWeight: 600 }}>{cont.code}</span>
              <ActionBtns
                onEdit={() => isEditing("continent", cont.id) ? stopEdit() : startEdit("continent", cont.id)}
                onDelete={() => setDelConfirm({ type: "continents", id: cont.id, name: cont.name_lv || cont.name })}
              />
              <span style={{ fontSize: 11, color: "#94a3b8" }}>{expCont === cont.id ? "▼" : "▶"}</span>
            </div>

            {isEditing("continent", cont.id) && (
              <InlineEditForm
                indent={12} bgColor="#f0f9ff" borderColor="#bae6fd"
                fields={[
                  { key: "name",    label: "Nosaukums (EN)", value: cont.name,    flex: 2 },
                  { key: "name_lv", label: "Nosaukums (LV)", value: cont.name_lv, flex: 2 },
                  { key: "code",    label: "Kods",           value: cont.code, minWidth: 80, transform: v => v.toUpperCase() },
                ]}
                onSave={async data => {
                  await api.patch(`/admin/continents/${cont.id}`, data);
                  qc.invalidateQueries({ queryKey: ["admin-continents"] });
                  qc.invalidateQueries({ queryKey: ["continents"] });
                  stopEdit();
                }}
                onCancel={stopEdit}
              />
            )}

            {/* Countries */}
            {expCont === cont.id && countries.map(country => (
              <div key={country.id} style={{ borderTop: "1px solid #f8fafc" }}>
                <div style={rowBase(28, expCountry === country.id)} onClick={() => toggleCountry(country.id)}>
                  <span style={{ fontSize: 15 }}>{flagEmoji(country.code)}</span>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>{country.name_lv || country.name}</span>
                  <span style={{ fontSize: 11, color: "#9ca3af" }}>{country.name}</span>
                  <span style={{ fontSize: 11, background: "#f1f5f9", color: "#64748b", padding: "1px 6px", borderRadius: 8, fontWeight: 600 }}>{country.code}</span>
                  <ActionBtns
                    onEdit={() => isEditing("country", country.id) ? stopEdit() : startEdit("country", country.id)}
                    onDelete={() => setDelConfirm({ type: "countries", id: country.id, name: country.name_lv || country.name })}
                  />
                  <span style={{ fontSize: 11, color: "#94a3b8" }}>{expCountry === country.id ? "▼" : "▶"}</span>
                </div>

                {isEditing("country", country.id) && (
                  <InlineEditForm
                    indent={28} bgColor="#f0fdf4" borderColor="#bbf7d0"
                    fields={[
                      { key: "name",       label: "Nosaukums (EN)", value: country.name,    flex: 2 },
                      { key: "name_lv",    label: "Nosaukums (LV)", value: country.name_lv, flex: 2 },
                      { key: "code",       label: "ISO kods", value: country.code, minWidth: 80, transform: v => v.toUpperCase() },
                      { key: "is_extinct", label: "Izmirusi", value: String(country.is_extinct ?? false), minWidth: 90,
                        options: [{ value: "false", label: "Nē" }, { value: "true", label: "💀 Jā" }],
                        keepValue: true, transform: v => v === "true" },
                    ]}
                    onSave={async data => {
                      await api.patch(`/admin/countries/${country.id}`, data);
                      qc.invalidateQueries({ queryKey: ["admin-countries"] });
                      qc.invalidateQueries({ queryKey: ["countries"] });
                      stopEdit();
                    }}
                    onCancel={stopEdit}
                  />
                )}

                {/* Periods */}
                {expCountry === country.id && periods.map(period => (
                  <div key={period.id} style={{ borderTop: "1px solid #f8fafc" }}>
                    <div style={{ ...rowBase(44, false), cursor: "default" }}>
                      <span style={{ fontSize: 13 }}>{sectionIcon[period.section] || "📋"}</span>
                      <span style={{ fontSize: 13 }}>{period.name}</span>
                      {(period.year_start || period.year_end) && (
                        <span style={{ fontSize: 11, color: "#94a3b8" }}>{period.year_start}–{period.year_end ?? "..."}</span>
                      )}
                      <span style={{ fontSize: 11, background: sectionBg[period.section] || "#f1f5f9", color: sectionClr[period.section] || "#374151", padding: "1px 7px", borderRadius: 8, fontWeight: 600 }}>
                        {sectionLabel[period.section]}
                      </span>
                      <ActionBtns
                        onEdit={() => isEditing("period", period.id) ? stopEdit() : startEdit("period", period.id)}
                        onDelete={() => setDelConfirm({ type: "periods", id: period.id, name: period.name })}
                      />
                    </div>

                    {isEditing("period", period.id) && (
                      <InlineEditForm
                        indent={44} bgColor="#fdf4ff" borderColor="#e9d5ff"
                        fields={[
                          { key: "name",       label: "Nosaukums",  value: period.name,       flex: 3 },
                          { key: "year_start", label: "No gada",    value: period.year_start != null ? String(period.year_start) : "", type: "number", minWidth: 90, nullable: true },
                          { key: "year_end",   label: "Līdz gadam", value: period.year_end   != null ? String(period.year_end)   : "", type: "number", minWidth: 90, nullable: true },
                          { key: "section", label: "Sadaļa", value: period.section, minWidth: 120,
                            options: SECTIONS.map(s => ({ value: s.type, label: `${s.icon} ${s.label}` })) },
                        ]}
                        onSave={async data => {
                          const payload = { name: data.name || undefined, section: data.section || undefined };
                          if (data.year_start !== null && data.year_start !== "") payload.year_start = Number(data.year_start);
                          if (data.year_end !== null && data.year_end !== "") payload.year_end = Number(data.year_end);
                          await api.patch(`/admin/periods/${period.id}`, payload);
                          qc.invalidateQueries({ queryKey: ["admin-periods"] });
                          qc.invalidateQueries({ queryKey: ["periods"] });
                          stopEdit();
                        }}
                        onCancel={stopEdit}
                      />
                    )}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Admin tree sidebar (Section → Continent → Country → Period → CoinCat) ──────
function AdminTreeSidebar({ tree, filter, onSetFilter }) {
  const [openSection,   setOpenSection]   = useState(null);
  const [openContinent, setOpenContinent] = useState(null);
  const [openCountry,   setOpenCountry]   = useState(null);
  const [openPeriod,    setOpenPeriod]    = useState(null);

  function r(style, indent) {
    return { padding: `5px 8px 5px ${indent}px`, cursor: "pointer", borderRadius: 6,
      display: "flex", justifyContent: "space-between", alignItems: "center", ...style };
  }

  function selectAll() {
    setOpenSection(null); setOpenContinent(null); setOpenCountry(null); setOpenPeriod(null); onSetFilter({});
  }
  function clickSection(type) {
    setOpenSection(type); setOpenContinent(null); setOpenCountry(null); setOpenPeriod(null); onSetFilter({ section: type });
  }
  function clickContinent(sType, cont) {
    setOpenSection(sType);
    const id = cont.id;
    if (openContinent === id) { setOpenContinent(null); setOpenCountry(null); setOpenPeriod(null); onSetFilter({ section: sType }); }
    else { setOpenContinent(id); setOpenCountry(null); setOpenPeriod(null); onSetFilter({ section: sType }); }
  }
  function clickCountry(sType, country) {
    const id = country.id;
    if (openCountry === id) { setOpenCountry(null); setOpenPeriod(null); onSetFilter({ section: sType }); }
    else { setOpenCountry(id); setOpenPeriod(null); onSetFilter({ section: sType }); }
  }
  function clickPeriod(sType, country, period) {
    const id = period.id;
    if (openPeriod === id) {
      setOpenPeriod(null); onSetFilter({ section: sType });
    } else {
      setOpenPeriod(id); onSetFilter({ section: sType, periodId: id });
    }
  }
  function clickCoinCat(sType, period, catName) {
    onSetFilter({ section: sType, periodId: period.id, coinCat: catName });
  }

  return (
    <div style={{ width: 230, flexShrink: 0, background: "#fff", borderRadius: 12, padding: 12,
      boxShadow: "0 1px 3px rgba(0,0,0,.1)", alignSelf: "flex-start", position: "sticky", top: 72,
      maxHeight: "calc(100vh - 96px)", overflowY: "auto" }}>
      <div style={{ fontWeight: 700, fontSize: 11, color: "#94a3b8", marginBottom: 10, textTransform: "uppercase", letterSpacing: .5 }}>Katalogs</div>

      {/* All */}
      <div onClick={selectAll} style={{ padding: "6px 8px", borderRadius: 6, cursor: "pointer", fontWeight: 600, fontSize: 14, marginBottom: 4,
        background: !openSection ? "#eff6ff" : "transparent", color: !openSection ? "#2563eb" : "#374151",
        display: "flex", justifyContent: "space-between" }}>
        <span>Visi</span><span style={{ fontSize: 12, color: "#94a3b8" }}>{tree?.total || 0}</span>
      </div>

      {SECTIONS.map(s => {
        const continents = tree?.[s.type] || [];
        const total = continents.reduce((a, c) => a + c.count, 0);
        if (total === 0) return null;
        const sActive = openSection === s.type;

        return (
          <div key={s.type}>
            <div onClick={() => clickSection(s.type)} style={r({
              fontWeight: 700, fontSize: 14,
              background: sActive && !openContinent ? "#eff6ff" : "transparent",
              color: sActive ? "#2563eb" : "#374151",
            }, 8)}>
              <span>{s.icon} {s.label}</span>
              <span style={{ fontSize: 12, color: "#94a3b8" }}>{total}</span>
            </div>

            {sActive && continents.map(cont => {
              const cntActive = openContinent === cont.id;
              return (
                <div key={cont.id}>
                  <div onClick={() => clickContinent(s.type, cont)} style={r({
                    fontSize: 13, fontWeight: 700,
                    background: cntActive && !openCountry ? "#fef9c3" : "transparent",
                    color: cntActive ? "#854d0e" : "#374151",
                  }, 18)}>
                    <span>🌍 {cont.name}</span>
                    <span style={{ fontSize: 11, color: "#94a3b8" }}>{cont.count}</span>
                  </div>

                  {cntActive && cont.children?.map(country => {
                    const coActive = openCountry === country.id;
                    return (
                      <div key={country.id}>
                        <div onClick={() => clickCountry(s.type, country)} style={r({
                          fontSize: 13, fontWeight: 600,
                          background: coActive ? "#f0fdf4" : "transparent",
                          color: coActive ? "#166534" : "#374151",
                        }, 28)}>
                          <span>{flagEmoji(country.code)} {country.name}</span>
                          <span style={{ fontSize: 11, color: "#94a3b8" }}>{country.count}</span>
                        </div>

                        {coActive && country.children?.map(period => {
                          const pActive = openPeriod === period.id;
                          return (
                            <div key={period.id}>
                              <div onClick={() => clickPeriod(s.type, country, period)} style={r({
                                fontSize: 12,
                                background: pActive && !filter.coinCat ? "#ede9fe" : "transparent",
                                color: pActive ? "#7c3aed" : "#374151",
                                fontWeight: pActive ? 700 : 400,
                              }, 38)}>
                                <span>{period.name}</span>
                                <span style={{ fontSize: 11, color: "#94a3b8" }}>{period.count}</span>
                              </div>

                              {pActive && s.type === "coins" && period.children?.map(cat => (
                                <div key={cat.name} onClick={() => clickCoinCat(s.type, period, cat.name)} style={r({
                                  fontSize: 11,
                                  background: filter.coinCat === cat.name ? "#fce7f3" : "transparent",
                                  color: filter.coinCat === cat.name ? "#9d174d" : "#374151",
                                }, 50)}>
                                  <span>{COIN_CAT_LABELS[cat.name] || cat.name}</span>
                                  <span style={{ fontSize: 11, color: "#94a3b8" }}>{cat.count}</span>
                                </div>
                              ))}
                            </div>
                          );
                        })}
                      </div>
                    );
                  })}
                </div>
              );
            })}
          </div>
        );
      })}
    </div>
  );
}

// ── Photo slot (for EditPanel) ─────────────────────────────────────────────────
function PhotoSlot({ label, url, onUpload, onDelete, uploading, onImportUrl }) {
  const ref = useRef();
  const [urlMode, setUrlMode] = useState(false);
  const [urlInput, setUrlInput] = useState("");
  const [urlLoading, setUrlLoading] = useState(false);
  const [urlErr, setUrlErr] = useState(null);
  const imgSrc = url ? (url.startsWith("http") ? url : BASE + url) : null;

  async function importFromUrl() {
    if (!urlInput.trim()) return;
    setUrlLoading(true); setUrlErr(null);
    try {
      await onImportUrl(urlInput.trim());
      setUrlInput(""); setUrlMode(false);
    } catch (e) {
      setUrlErr(e.response?.data?.detail || "Lejupielāde neizdevās");
    } finally {
      setUrlLoading(false);
    }
  }

  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 12, fontWeight: 700, color: "#64748b", marginBottom: 4 }}>{label}</div>
      <div style={{ border: "2px dashed #cbd5e1", borderRadius: 10, height: 150, overflow: "hidden",
        display: "flex", alignItems: "center", justifyContent: "center", background: "#f8fafc", position: "relative", cursor: "pointer" }}
        onClick={() => !imgSrc && ref.current.click()}>
        {imgSrc
          ? <img src={imgSrc} alt={label} style={{ width: "100%", height: "100%", objectFit: "contain" }} />
          : <div style={{ textAlign: "center", color: "#94a3b8" }}><div style={{ fontSize: 28 }}>📷</div><div style={{ fontSize: 12 }}>Augšuplādēt</div></div>
        }
        {(uploading || urlLoading) && <div style={{ position: "absolute", inset: 0, background: "rgba(255,255,255,.7)",
          display: "flex", alignItems: "center", justifyContent: "center" }}>⏳</div>}
      </div>
      <input ref={ref} type="file" accept="image/*" style={{ display: "none" }}
        onChange={e => { const f = e.target.files[0]; if (f) onUpload(f); }} />
      <div style={{ display: "flex", gap: 6, marginTop: 6 }}>
        <button onClick={() => ref.current.click()} style={{ flex: 1, padding: "4px 0", fontSize: 12, borderRadius: 6,
          border: "1px solid #3b82f6", background: "#eff6ff", color: "#2563eb", cursor: "pointer" }}>
          {imgSrc ? "Mainīt" : "Augšuplādēt"}
        </button>
        {imgSrc && <button onClick={onDelete} style={{ padding: "4px 8px", fontSize: 12, borderRadius: 6,
          border: "1px solid #ef4444", background: "#fef2f2", color: "#dc2626", cursor: "pointer" }}>✕</button>}
        <button onClick={() => { setUrlMode(m => !m); setUrlErr(null); setUrlInput(""); }}
          title="Ielādēt no URL" style={{ padding: "4px 8px", fontSize: 12, borderRadius: 6,
          border: "1px solid #cbd5e1", background: urlMode ? "#e0f2fe" : "#f8fafc", color: "#64748b", cursor: "pointer" }}>
          🔗
        </button>
      </div>
      {urlMode && (
        <div style={{ marginTop: 6 }}>
          <div style={{ display: "flex", gap: 4 }}>
            <input
              value={urlInput} onChange={e => setUrlInput(e.target.value)}
              placeholder="https://ucoin.net/... vai cits URL"
              style={{ ...inp, fontSize: 11, padding: "4px 8px", flex: 1 }}
              onKeyDown={e => e.key === "Enter" && importFromUrl()}
              autoFocus
            />
            <button onClick={importFromUrl} disabled={urlLoading || !urlInput.trim()} style={{
              padding: "4px 10px", borderRadius: 6, background: "#2563eb", color: "#fff",
              border: "none", cursor: "pointer", fontSize: 11, whiteSpace: "nowrap",
            }}>
              {urlLoading ? "..." : "↓ Lejupielādēt"}
            </button>
          </div>
          {urlErr && <div style={{ color: "#dc2626", fontSize: 11, marginTop: 3 }}>⚠️ {urlErr}</div>}
        </div>
      )}
    </div>
  );
}

// ── Edit panel (existing item) ─────────────────────────────────────────────────
function EditPanel({ item, onClose }) {
  const qc = useQueryClient();
  const [form, setForm] = useState({
    name: item.name || "", year: item.year || "", denomination: item.denomination || "",
    material: item.material || "", diameter_mm: item.diameter_mm || "", weight_g: item.weight_g || "",
    mint: item.mint || "", mintage: item.mintage || "",
    designer: item.designer || "", engraver: item.engraver || "",
    catalog_number: item.catalog_number || "",
    coin_category: item.coin_category || "circulation", description: item.description || "",
    obverse_description: item.obverse_description || "", reverse_description: item.reverse_description || "",
    perforation: item.perforation || "", color: item.color || "",
  });
  const [obverseUrl, setObverseUrl] = useState(item.image_url || null);
  const [reverseUrl, setReverseUrl] = useState(item.image_url_reverse || null);
  const [uploadingOb, setUploadingOb] = useState(false);
  const [uploadingRev, setUploadingRev] = useState(false);
  const [saved, setSaved] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [saveAsNewMsg, setSaveAsNewMsg] = useState(null);

  const deleteMut = useMutation({
    mutationFn: () => api.delete(`/admin/catalog/${item.id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-tree"] });
      onClose();
    },
  });

  async function uploadPhoto(file, side, setUploading, setUrl) {
    setUploading(true);
    try {
      const fd = new FormData(); fd.append("file", file);
      const { data } = await api.post(`/admin/catalog/${item.id}/image?side=${side}`, fd);
      const newUrl = side === "reverse" ? data.image_url_reverse : data.image_url;
      setUrl(newUrl ? (newUrl.startsWith("http") ? newUrl : BASE + newUrl) : null);
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-items"] });
    } finally { setUploading(false); }
  }
  async function deletePhoto(side, setUrl) {
    await api.delete(`/admin/catalog/${item.id}/image?side=${side}`);
    setUrl(null);
    qc.invalidateQueries({ queryKey: ["admin-catalog"] });
    qc.invalidateQueries({ queryKey: ["catalog-items"] });
  }
  async function importPhotoFromUrl(url, side, setUrl) {
    const { data } = await api.post(`/admin/catalog/${item.id}/image-from-url`, { url, side });
    const newUrl = side === "reverse" ? data.image_url_reverse : data.image_url;
    setUrl(newUrl ? (newUrl.startsWith("http") ? newUrl : BASE + newUrl) : null);
    qc.invalidateQueries({ queryKey: ["admin-catalog"] });
    qc.invalidateQueries({ queryKey: ["catalog-items"] });
  }

  const save = useMutation({
    mutationFn: () => api.patch(`/admin/catalog/${item.id}`, form),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["admin-catalog"] }); setSaved(true); setTimeout(() => setSaved(false), 2000); },
  });

  const saveAsNew = useMutation({
    mutationFn: async () => {
      const r = await api.post("/admin/catalog", {
        period_id: item.period_id,
        section: item.section,
        coin_category: form.coin_category || item.coin_category || "circulation",
        name: form.name || "Nezināms",
        year: form.year || null,
        denomination: form.denomination || null,
        material: form.material || null,
        diameter_mm: form.diameter_mm || null,
        weight_g: form.weight_g || null,
        mint: form.mint || null,
        mintage: form.mintage || null,
        designer: form.designer || null,
        engraver: form.engraver || null,
        catalog_number: form.catalog_number || null,
        description: form.description || null,
        obverse_description: form.obverse_description || null,
        reverse_description: form.reverse_description || null,
        perforation: form.perforation || null,
        color: form.color || null,
      });
      const newId = r.data.id;
      const toAbs = url => url ? (url.startsWith("http") ? url : BASE + url) : null;
      const obUrl = toAbs(obverseUrl);
      const revUrl = toAbs(reverseUrl);
      if (obUrl) await api.post(`/admin/catalog/${newId}/image-from-url`, { url: obUrl, side: "obverse" }).catch(() => {});
      if (revUrl && isTwoSided) await api.post(`/admin/catalog/${newId}/image-from-url`, { url: revUrl, side: "reverse" }).catch(() => {});
      return r;
    },
    onSuccess: (r) => {
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-tree"] });
      setSaveAsNewMsg({ ok: `Izveidots jauns ieraksts: "${r.data.name}" (ID ${r.data.id})` });
    },
    onError: (e) => {
      const detail = e.response?.data?.detail || "Kļūda";
      setSaveAsNewMsg({ err: detail });
    },
  });

  const isTwoSided  = ["coins", "medals", "banknotes"].includes(item.section);
  const isCoinMedal = item.section === "coins" || item.section === "medals";

  function field(label, key, textarea = false) {
    return (
      <div style={{ marginBottom: 10 }}>
        <label style={lbl}>{label}</label>
        {textarea
          ? <textarea rows={3} value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
              style={{ ...inp, resize: "vertical" }} />
          : <input value={form[key]} onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))} style={inp} />
        }
      </div>
    );
  }

  return (
    <div style={card}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <div>
          <h3 style={{ fontWeight: 800, fontSize: 16, marginBottom: 2 }}>{item.name}</h3>
          <span style={{ fontSize: 11, background: item.admin_edited ? "#fef3c7" : "#f1f5f9",
            color: item.admin_edited ? "#92400e" : "#64748b", padding: "2px 8px", borderRadius: 20, fontWeight: 600 }}>
            {item.admin_edited ? "🔒 Admin rediģēts" : "Jauns"}
          </span>
        </div>
        <button onClick={onClose} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer", color: "#94a3b8" }}>✕</button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>Fotogrāfijas</div>
        <div style={{ display: "flex", gap: 10 }}>
          <PhotoSlot label="Averse" url={obverseUrl} uploading={uploadingOb}
            onUpload={f => uploadPhoto(f, "obverse", setUploadingOb, setObverseUrl)}
            onDelete={() => deletePhoto("obverse", setObverseUrl)}
            onImportUrl={url => importPhotoFromUrl(url, "obverse", setObverseUrl)} />
          {isTwoSided && <PhotoSlot label="Reverse" url={reverseUrl} uploading={uploadingRev}
            onUpload={f => uploadPhoto(f, "reverse", setUploadingRev, setReverseUrl)}
            onDelete={() => deletePhoto("reverse", setReverseUrl)}
            onImportUrl={url => importPhotoFromUrl(url, "reverse", setReverseUrl)} />}
        </div>
      </div>

      <hr style={{ border: "none", borderTop: "1px solid #f1f5f9", marginBottom: 14 }} />

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 12px" }}>
        <div>{field("Nosaukums", "name")}</div>
        <div>{field("Gads", "year")}</div>
        <div>{field("Nominālvērtība", "denomination")}</div>
        <div>{field("Materiāls", "material")}</div>
        {isCoinMedal && <div>{field("Diametrs (mm)", "diameter_mm")}</div>}
        {isCoinMedal && <div>{field("Svars (g)", "weight_g")}</div>}
        {item.section !== "stamps" && <div>{field(item.section === "banknotes" ? "Iespiestuve" : "Kaltuve", "mint")}</div>}
        <div>{field("Tirāža", "mintage")}</div>
        {isCoinMedal && <div>{field("Mākslinieks", "designer")}</div>}
        {isCoinMedal && <div>{field("Gravieris", "engraver")}</div>}
        <div>{field("Kataloga Nr.", "catalog_number")}</div>
        <div>
          <label style={lbl}>Kategorija</label>
          <select value={form.coin_category} onChange={e => setForm(f => ({ ...f, coin_category: e.target.value }))} style={inp}>
            <option value="circulation">Apgrozības</option>
            <option value="commemorative">Piemiņas</option>
            <option value="collector">Kolekcionēšanas</option>
          </select>
        </div>
      </div>
      {field("Apraksts", "description", true)}
      {field("Averse apraksts", "obverse_description", true)}
      {isTwoSided && field("Reverse apraksts", "reverse_description", true)}
      {item.section === "stamps" && <>{field("Perforācija", "perforation")}{field("Krāsa", "color")}</>}

      <div style={{ display: "flex", gap: 8, marginTop: 4 }}>
        <button className="btn btn-primary" style={{ flex: 1 }} onClick={() => save.mutate()} disabled={save.isPending}>
          {save.isPending ? "Saglabā..." : saved ? "✅ Saglabāts!" : "💾 Saglabāt"}
        </button>
        <button className="btn btn-outline" onClick={onClose}>Aizvērt</button>
      </div>

      <button onClick={() => { setSaveAsNewMsg(null); saveAsNew.mutate(); }} disabled={saveAsNew.isPending} style={{
        marginTop: 8, width: "100%", padding: "8px 0", borderRadius: 8, cursor: "pointer",
        border: "1.5px solid #7c3aed", background: saveAsNew.isPending ? "#f5f3ff" : "#faf5ff",
        color: "#7c3aed", fontWeight: 600, fontSize: 13,
      }}>
        {saveAsNew.isPending ? "Veido..." : "📋 Saglabāt kā jaunu ierakstu"}
      </button>
      {saveAsNewMsg?.ok && <div style={{ color: "#16a34a", fontWeight: 700, marginTop: 6, fontSize: 13 }}>✅ {saveAsNewMsg.ok}</div>}
      {saveAsNewMsg?.err && <div style={{ color: "#dc2626", fontWeight: 600, marginTop: 6, fontSize: 13 }}>⚠️ {saveAsNewMsg.err}</div>}

      {!confirmDelete ? (
        <button onClick={() => setConfirmDelete(true)} style={{
          marginTop: 8, width: "100%", padding: "8px 0", borderRadius: 8, cursor: "pointer",
          border: "1.5px solid #fca5a5", background: "#fff1f2", color: "#dc2626",
          fontWeight: 600, fontSize: 13,
        }}>
          🗑️ Dzēst ierakstu
        </button>
      ) : (
        <div style={{ marginTop: 8, background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, padding: "10px 14px" }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "#dc2626", marginBottom: 8 }}>
            Dzēst <strong>{item.name}</strong>? Šo nevar atcelt.
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => deleteMut.mutate()} disabled={deleteMut.isPending} style={{
              flex: 1, padding: "7px 0", borderRadius: 7, border: "none", cursor: "pointer",
              background: "#dc2626", color: "#fff", fontWeight: 700, fontSize: 13,
            }}>
              {deleteMut.isPending ? "Dzēš..." : "Jā, dzēst"}
            </button>
            <button onClick={() => setConfirmDelete(false)} style={{
              flex: 1, padding: "7px 0", borderRadius: 7, border: "1px solid #e2e8f0",
              background: "#f8fafc", color: "#374151", cursor: "pointer", fontSize: 13,
            }}>
              Atcelt
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Pending submissions tab ───────────────────────────────────────────────────
const BASE_URL = "http://localhost:8001";

function BulkBar({ checkedCount, onDelete, onCancel, confirm, onConfirm, onBack, deleting }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10,
      background: confirm ? "#fef2f2" : "#fff7ed",
      border: `1.5px solid ${confirm ? "#fca5a5" : "#fdba74"}`,
      borderRadius: 10, padding: "8px 14px" }}>
      <span style={{ fontWeight: 600, fontSize: 13, flex: 1 }}>
        {confirm
          ? `⚠️ Tiešām dzēst ${checkedCount} ierakstus? Šo nevar atcelt!`
          : `Atzīmēti ${checkedCount} ieraksti`}
      </span>
      {!confirm ? (
        <>
          <button onClick={onDelete} style={{ padding: "5px 14px", borderRadius: 7, fontWeight: 700, fontSize: 13,
            background: "#dc2626", color: "#fff", border: "none", cursor: "pointer" }}>
            🗑️ Dzēst
          </button>
          <button onClick={onCancel} style={{ padding: "5px 14px", borderRadius: 7, fontWeight: 600, fontSize: 13,
            background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0", cursor: "pointer" }}>
            Atcelt
          </button>
        </>
      ) : (
        <>
          <button disabled={deleting} onClick={onConfirm} style={{ padding: "5px 14px", borderRadius: 7, fontWeight: 700, fontSize: 13,
            background: deleting ? "#9ca3af" : "#991b1b", color: "#fff", border: "none",
            cursor: deleting ? "not-allowed" : "pointer" }}>
            {deleting ? "Dzēš..." : "Jā, dzēst!"}
          </button>
          <button onClick={onBack} style={{ padding: "5px 14px", borderRadius: 7, fontWeight: 600, fontSize: 13,
            background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0", cursor: "pointer" }}>
            Nē
          </button>
        </>
      )}
    </div>
  );
}

function PendingCatalogSection({ items, onRefresh }) {
  const qc = useQueryClient();
  const [loading, setLoading] = useState(null);
  const [checkedIds, setCheckedIds] = useState(new Set());
  const [bulkConfirm, setBulkConfirm] = useState(false);
  const [bulkDeleting, setBulkDeleting] = useState(false);

  async function approve(id) {
    setLoading(id);
    try {
      await api.post(`/admin/pending-catalog/${id}/approve`);
      qc.invalidateQueries({ queryKey: ["admin-pending-catalog"] });
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-tree"] });
      onRefresh();
    } catch(e) {
      alert(e.response?.data?.detail || "Kļūda");
    } finally {
      setLoading(null);
    }
  }

  async function reject(id) {
    if (!confirm("Noraidīt šo kataloga ierakstu?")) return;
    setLoading(id);
    try {
      await api.delete(`/admin/pending-catalog/${id}`);
      qc.invalidateQueries({ queryKey: ["admin-pending-catalog"] });
      onRefresh();
    } finally {
      setLoading(null);
    }
  }

  async function bulkDelete() {
    setBulkDeleting(true);
    for (const id of checkedIds) {
      try { await api.delete(`/admin/pending-catalog/${id}`); } catch {}
    }
    setCheckedIds(new Set());
    setBulkConfirm(false);
    setBulkDeleting(false);
    qc.invalidateQueries({ queryKey: ["admin-pending-catalog"] });
    onRefresh();
  }

  function toggleCheck(id, e) {
    e.stopPropagation();
    const next = new Set(checkedIds);
    if (next.has(id)) { next.delete(id); setBulkConfirm(false); } else next.add(id);
    setCheckedIds(next);
  }

  if (items.length === 0) return null;

  return (
    <div style={{ marginBottom: 28 }}>
      <h3 style={{ fontWeight: 800, fontSize: 15, marginBottom: 10, color: "#1e3a8a" }}>
        📚 AI atpazītie kataloga ieraksti ({items.length})
      </h3>

      {checkedIds.size > 0 && (
        <BulkBar checkedCount={checkedIds.size} confirm={bulkConfirm} deleting={bulkDeleting}
          onDelete={() => setBulkConfirm(true)}
          onCancel={() => { setCheckedIds(new Set()); setBulkConfirm(false); }}
          onConfirm={bulkDelete}
          onBack={() => setBulkConfirm(false)} />
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <button onClick={() => {
          if (checkedIds.size === items.length) { setCheckedIds(new Set()); setBulkConfirm(false); }
          else setCheckedIds(new Set(items.map(i => i.id)));
        }} style={{ padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: "pointer",
          background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0" }}>
          {checkedIds.size === items.length ? "Noatzīmēt visus" : "Atzīmēt visus"}
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {items.map(item => {
          const imgSrc = item.image_url ? BASE_URL + item.image_url : null;
          const isChecked = checkedIds.has(item.id);
          return (
            <div key={item.id} style={{
              border: `2px solid ${isChecked ? "#fbbf24" : "#bfdbfe"}`,
              borderRadius: 10, background: isChecked ? "#fef9c3" : "#eff6ff",
              padding: 12, display: "flex", gap: 12, alignItems: "center",
            }}>
              <input type="checkbox" checked={isChecked}
                onClick={e => e.stopPropagation()}
                onChange={e => toggleCheck(item.id, e)}
                style={{ width: 16, height: 16, flexShrink: 0, cursor: "pointer", accentColor: "#dc2626" }} />
              {imgSrc
                ? <img src={imgSrc} alt="" style={{ width: 60, height: 60, objectFit: "contain", borderRadius: 6, background: "#f1f5f9", flexShrink: 0 }} />
                : <div style={{ width: 60, height: 60, background: "#dbeafe", borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 22, flexShrink: 0 }}>🪙</div>
              }
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 700, fontSize: 14 }}>{item.name}</div>
                <div style={{ fontSize: 12, color: "#475569", display: "flex", gap: 10, flexWrap: "wrap" }}>
                  {item.year && <span>Gads: {item.year}</span>}
                  {item.denomination && <span>Nomināls: {item.denomination}</span>}
                  {item.material && <span>Materiāls: {item.material}</span>}
                  <span style={{ color: "#94a3b8" }}>Iesniedzējs: {item.username}</span>
                </div>
              </div>
              <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                <button onClick={() => approve(item.id)} disabled={loading === item.id}
                  style={{ padding: "6px 14px", borderRadius: 6, background: "#16a34a", color: "#fff",
                    border: "none", fontWeight: 700, cursor: "pointer", fontSize: 13 }}>
                  {loading === item.id ? "..." : "✓ Apstiprināt"}
                </button>
                <button onClick={() => reject(item.id)} disabled={loading === item.id}
                  style={{ padding: "6px 10px", borderRadius: 6, background: "#fef2f2", color: "#dc2626",
                    border: "1.5px solid #fca5a5", cursor: "pointer", fontSize: 13 }}>
                  Noraidīt
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function PendingTab({ pending, pendingCatalog, onRefresh }) {
  const qc = useQueryClient();
  const [confirmId, setConfirmId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [checkedIds, setCheckedIds] = useState(new Set());
  const [bulkConfirm, setBulkConfirm] = useState(false);
  const [bulkDeleting, setBulkDeleting] = useState(false);

  async function approve(id) {
    setLoading(true);
    try {
      await api.post(`/admin/pending/${id}/approve`);
      qc.invalidateQueries({ queryKey: ["admin-pending"] });
      qc.invalidateQueries({ queryKey: ["admin-catalog"] });
      qc.invalidateQueries({ queryKey: ["catalog-tree"] });
      setConfirmId(null);
      onRefresh();
    } catch(e) {
      alert(e.response?.data?.detail || "Kļūda");
    } finally {
      setLoading(false);
    }
  }

  async function dismiss(id) {
    await api.delete(`/admin/pending/${id}`);
    qc.invalidateQueries({ queryKey: ["admin-pending"] });
    onRefresh();
  }

  async function bulkDelete() {
    setBulkDeleting(true);
    for (const id of checkedIds) {
      try { await api.delete(`/admin/pending/${id}`); } catch {}
    }
    setCheckedIds(new Set());
    setBulkConfirm(false);
    setBulkDeleting(false);
    qc.invalidateQueries({ queryKey: ["admin-pending"] });
    onRefresh();
  }

  function toggleCheck(id, e) {
    e.stopPropagation();
    const next = new Set(checkedIds);
    if (next.has(id)) { next.delete(id); setBulkConfirm(false); } else next.add(id);
    setCheckedIds(next);
  }

  if (pending.length === 0 && pendingCatalog.length === 0) return (
    <div style={{ textAlign: "center", paddingTop: 60, color: "#94a3b8", fontSize: 16 }}>
      Nav neapstiprinātu iesniegumu.
    </div>
  );

  return (
    <div style={{ maxWidth: 860 }}>
      <PendingCatalogSection items={pendingCatalog} onRefresh={onRefresh} />

      {pending.length > 0 && (
        <>
          <h3 style={{ fontWeight: 800, fontSize: 15, marginBottom: 10, color: "#92400e" }}>
            ✍️ Manuāli ievadītie priekšmeti ({pending.length})
          </h3>

          {checkedIds.size > 0 && (
            <BulkBar checkedCount={checkedIds.size} confirm={bulkConfirm} deleting={bulkDeleting}
              onDelete={() => setBulkConfirm(true)}
              onCancel={() => { setCheckedIds(new Set()); setBulkConfirm(false); }}
              onConfirm={bulkDelete}
              onBack={() => setBulkConfirm(false)} />
          )}

          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <button onClick={() => {
              if (checkedIds.size === pending.length) { setCheckedIds(new Set()); setBulkConfirm(false); }
              else setCheckedIds(new Set(pending.map(i => i.id)));
            }} style={{ padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: "pointer",
              background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0" }}>
              {checkedIds.size === pending.length ? "Noatzīmēt visus" : "Atzīmēt visus"}
            </button>
          </div>
        </>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {pending.map(item => {
          const imgSrc = item.user_image ? BASE_URL + item.user_image : null;
          const isConfirming = confirmId === item.id;
          const isChecked = checkedIds.has(item.id);

          return (
            <div key={item.id} style={{
              border: `2px solid ${isChecked ? "#fbbf24" : "#fca5a5"}`,
              borderRadius: 12, background: isChecked ? "#fef9c3" : "#fff5f5",
              padding: 16, display: "flex", gap: 16, alignItems: "flex-start",
            }}>
              <input type="checkbox" checked={isChecked}
                onClick={e => e.stopPropagation()}
                onChange={e => toggleCheck(item.id, e)}
                style={{ width: 16, height: 16, marginTop: 4, flexShrink: 0, cursor: "pointer", accentColor: "#dc2626" }} />

              {/* Photo */}
              <div style={{ width: 90, flexShrink: 0 }}>
                {imgSrc
                  ? <img src={imgSrc} alt="" style={{ width: 90, height: 90, objectFit: "contain", borderRadius: 8, background: "#f1f5f9" }} />
                  : <div style={{ width: 90, height: 90, background: "#f1f5f9", borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28 }}>🪙</div>}
              </div>

              {/* Info */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>
                  {item.custom_name || `${item.custom_denomination || ""} ${item.custom_year || ""}`.trim() || "Bez nosaukuma"}
                </div>
                <div style={{ fontSize: 12, color: "#64748b", marginBottom: 6, display: "flex", gap: 12, flexWrap: "wrap" }}>
                  {item.custom_year        && <span>Gads: {item.custom_year}</span>}
                  {item.custom_denomination && <span>Nomināls: {item.custom_denomination}</span>}
                  {item.custom_country      && <span>Valsts: {item.custom_country}</span>}
                  {item.custom_material     && <span>Materiāls: {item.custom_material}</span>}
                  <span style={{ color: "#94a3b8" }}>Iesniedzējs: {item.username}</span>
                </div>
                {item.custom_description && (
                  <div style={{ fontSize: 12, color: "#374151", background: "#f8fafc", borderRadius: 6, padding: "4px 8px", marginBottom: 8 }}>
                    {item.custom_description}
                  </div>
                )}

                {isConfirming ? (
                  <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: 8,
                    background: "#f0fdf4", borderRadius: 8, padding: "8px 12px", border: "1px solid #86efac" }}>
                    <span style={{ fontSize: 13, color: "#166534", fontWeight: 600 }}>
                      Apstiprināt un novietot automātiski?
                    </span>
                    <button onClick={() => approve(item.id)} disabled={loading}
                      style={{ padding: "5px 16px", borderRadius: 6, background: "#16a34a", color: "#fff",
                        border: "none", fontWeight: 700, cursor: "pointer", fontSize: 13 }}>
                      {loading ? "..." : "Jā"}
                    </button>
                    <button onClick={() => setConfirmId(null)} disabled={loading}
                      style={{ padding: "5px 12px", borderRadius: 6, background: "#f1f5f9", color: "#374151",
                        border: "1px solid #e2e8f0", cursor: "pointer", fontSize: 13 }}>
                      Atcelt
                    </button>
                  </div>
                ) : (
                  <div style={{ display: "flex", gap: 8, marginTop: 6 }}>
                    <button onClick={() => setConfirmId(item.id)}
                      style={{ padding: "6px 16px", borderRadius: 6, background: "#16a34a", color: "#fff",
                        border: "none", fontWeight: 700, cursor: "pointer", fontSize: 13 }}>
                      ✓ Apstiprināt
                    </button>
                    <button onClick={() => dismiss(item.id)}
                      style={{ padding: "6px 12px", borderRadius: 6, background: "#f1f5f9", color: "#94a3b8",
                        border: "1.5px solid #e2e8f0", cursor: "pointer", fontSize: 13 }}>
                      Noraidīt
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Numista import tab ────────────────────────────────────────────────────────
const NUMISTA_CATS = [
  { value: "coin",      label: "🪙 Monētas" },
  { value: "banknote",  label: "💵 Banknotes" },
  { value: "stamp",     label: "📮 Pastmarkas" },
  { value: "exonumia",  label: "🏅 Exonumia" },
];
const NUMISTA_SECTION_MAP = { coin: "coins", banknote: "banknotes", stamp: "stamps", exonumia: "medals" };

function NumistaTab() {
  const [query, setQuery]           = useState("");
  const [category, setCategory]     = useState("coin");
  const [results, setResults]       = useState(null);
  const [searching, setSearching]   = useState(false);
  const [selected, setSelected]     = useState(null);
  const [detail, setDetail]         = useState(null);
  const [detailLoading, setDL]      = useState(false);
  const [importing, setImporting]   = useState(false);
  const [msg, setMsg]               = useState({ ok: null, err: null });

  async function doSearch() {
    if (!query.trim()) return;
    setSearching(true); setResults(null); setSelected(null); setDetail(null); setMsg({});
    try {
      const r = await api.get("/admin/numista/search", { params: { q: query, category, lang: "en" } });
      setResults(r.data);
    } catch (e) {
      setMsg({ err: e.response?.data?.detail || "Meklēšanas kļūda" });
    } finally {
      setSearching(false);
    }
  }

  async function selectCoin(coin) {
    setSelected(coin); setDetail(null); setDL(true);
    try {
      const r = await api.get(`/admin/numista/type/${coin.id}`, { params: { lang: "en" } });
      setDetail(r.data);
    } catch {
      setMsg({ err: "Nevar iegūt detaļas no Numista" });
    } finally {
      setDL(false);
    }
  }

  async function doImport() {
    setImporting(true); setMsg({});
    try {
      const r = await api.post("/admin/numista/import", {
        numista_id: String(selected.id),
      });
      setMsg({ ok: `Importēts: ${r.data.name} (kataloga ID ${r.data.id})` });
      setSelected(null); setDetail(null);
    } catch (e) {
      setMsg({ err: e.response?.data?.detail || "Importa kļūda" });
    } finally {
      setImporting(false);
    }
  }

  return (
    <div style={{ maxWidth: 920 }}>
      {/* Search bar */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <select value={category} onChange={e => setCategory(e.target.value)} style={{ ...inp, width: 150 }}>
          {NUMISTA_CATS.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={e => e.key === "Enter" && doSearch()}
          placeholder="Meklēt Numista (piem. Latvia 2 Lati)..."
          style={{ ...inp, flex: 1 }}
        />
        <button onClick={doSearch} disabled={searching} style={{
          padding: "7px 18px", borderRadius: 7, background: "#1e3a8a", color: "#fff",
          fontWeight: 700, fontSize: 13, border: "none", cursor: "pointer", whiteSpace: "nowrap",
        }}>
          {searching ? "..." : "🔍 Meklēt"}
        </button>
      </div>

      <Msg ok={msg.ok} err={msg.err} />

      {/* Results grid */}
      {results && (
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12, color: "#64748b", marginBottom: 10 }}>
            {results.count ?? (results.types?.length ?? 0)} rezultāti — noklikšķini uz monētas, lai importētu
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(130px,1fr))", gap: 10 }}>
            {(results.types || []).map(coin => (
              <div key={coin.id} onClick={() => selectCoin(coin)} style={{
                border: `2px solid ${selected?.id === coin.id ? "#3b82f6" : "#e2e8f0"}`,
                borderRadius: 10, padding: 10, cursor: "pointer", textAlign: "center",
                background: selected?.id === coin.id ? "#eff6ff" : "#fff",
              }}>
                {coin.obverse_thumbnail
                  ? <img src={coin.obverse_thumbnail} style={{ width: 64, height: 64, objectFit: "contain", marginBottom: 6 }} alt="" />
                  : <div style={{ width: 64, height: 64, background: "#f1f5f9", margin: "0 auto 6px", borderRadius: 32,
                      display: "flex", alignItems: "center", justifyContent: "center", fontSize: 26 }}>🪙</div>
                }
                <div style={{ fontSize: 11, fontWeight: 600, lineHeight: 1.3, marginBottom: 2 }}>{coin.title}</div>
                <div style={{ fontSize: 10, color: "#94a3b8" }}>{coin.issuer?.name}</div>
                <div style={{ fontSize: 10, color: "#94a3b8" }}>
                  {coin.min_year}{coin.max_year && coin.max_year !== coin.min_year ? `–${coin.max_year}` : ""}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detail + import panel */}
      {selected && (
        <div style={{ ...card, background: "#f8fafc" }}>
          {detailLoading && <p style={{ color: "#888" }}>Ielādē detaļas...</p>}
          {detail && (
            <>
              <div style={{ display: "flex", gap: 16, marginBottom: 16, flexWrap: "wrap" }}>
                <div style={{ display: "flex", gap: 8 }}>
                  {[detail.obverse_picture || detail.obverse?.picture, detail.reverse_picture || detail.reverse?.picture]
                    .filter(Boolean).map((src, i) => (
                      <img key={i} src={src}
                        style={{ width: 100, height: 100, objectFit: "contain", borderRadius: 8, border: "1px solid #e2e8f0", background: "#fff" }}
                        alt={i === 0 ? "Averse" : "Reverse"}
                      />
                    ))
                  }
                </div>
                <div style={{ flex: 1, minWidth: 160 }}>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>{detail.title}</div>
                  <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.8 }}>
                    {[
                      detail.issuer?.name && `🌍 ${detail.issuer.name}`,
                      detail.min_year && `📅 ${detail.min_year}${detail.max_year && detail.max_year !== detail.min_year ? `–${detail.max_year}` : ""}`,
                      detail.composition?.text && `⚗️ ${detail.composition.text}`,
                      detail.weight && `⚖️ ${detail.weight}g`,
                      detail.size && `⌀ ${detail.size}mm`,
                    ].filter(Boolean).map((line, i) => <div key={i}>{line}</div>)}
                  </div>
                  <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>Numista ID: {detail.id}</div>
                </div>
              </div>

              <div style={{ borderTop: "1px solid #e2e8f0", paddingTop: 14 }}>
                <button
                  onClick={doImport}
                  disabled={importing}
                  style={{
                    padding: "9px 24px", borderRadius: 8, border: "none",
                    background: "#16a34a", color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer",
                  }}
                >
                  {importing ? "Importē..." : "⬇️ Importēt katalogā"}
                </button>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

// ── Premium tab ───────────────────────────────────────────────────────────────
function PremiumTab() {
  const qc = useQueryClient();
  const [settings, setSettings] = useState(null);
  const [form, setForm] = useState(null);
  const [savedMsg, setSavedMsg] = useState(null);
  const [userSearch, setUserSearch] = useState("");
  const [granting, setGranting] = useState(null); // user_id being granted
  const [grantForm, setGrantForm] = useState({ plan: "manual", months: "" });

  const { data: fetchedSettings, refetch: refetchSettings } = useQuery({
    queryKey: ["admin-premium"],
    queryFn: () => api.get("/admin/premium").then(r => r.data),
  });
  if (fetchedSettings && !settings) {
    setSettings(fetchedSettings);
    setForm({ ...fetchedSettings });
  }

  const { data: users = [], refetch: refetchUsers } = useQuery({
    queryKey: ["admin-premium-users"],
    queryFn: () => api.get("/admin/premium/users").then(r => r.data),
  });

  const saveMut = useMutation({
    mutationFn: () => api.patch("/admin/premium", form),
    onSuccess: (r) => {
      setSettings(r.data);
      setForm({ ...r.data });
      setSavedMsg("Saglabāts!");
      qc.invalidateQueries({ queryKey: ["admin-premium"] });
      setTimeout(() => setSavedMsg(null), 2000);
    },
  });

  async function grantSub(userId) {
    await api.post(`/admin/premium/grant/${userId}`, {
      plan: grantForm.plan,
      months: grantForm.months ? Number(grantForm.months) : null,
    });
    setGranting(null);
    setGrantForm({ plan: "manual", months: "" });
    refetchUsers();
  }

  async function revokeSub(userId) {
    if (!window.confirm("Atsaukt abonementu?")) return;
    await api.delete(`/admin/premium/revoke/${userId}`);
    refetchUsers();
  }

  const filtered = users.filter(u =>
    !userSearch || u.username.toLowerCase().includes(userSearch.toLowerCase()) ||
    u.email.toLowerCase().includes(userSearch.toLowerCase())
  );

  const planLabel = { monthly: "Mēneša", yearly: "Gada", manual: "Manuāls" };

  return (
    <div style={{ maxWidth: 860 }}>
      {/* Settings card */}
      <div style={card}>
        <h3 style={{ fontWeight: 800, fontSize: 16, marginBottom: 16 }}>⚙️ Premium iestatījumi</h3>
        {form && (
          <>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: "flex", alignItems: "center", gap: 12, cursor: "pointer" }}>
                <div onClick={() => setForm(f => ({ ...f, premium_enabled: !f.premium_enabled }))} style={{
                  width: 48, height: 26, borderRadius: 13, background: form.premium_enabled ? "#16a34a" : "#cbd5e1",
                  position: "relative", cursor: "pointer", transition: "background .2s", flexShrink: 0,
                }}>
                  <div style={{
                    width: 20, height: 20, borderRadius: "50%", background: "#fff",
                    position: "absolute", top: 3, left: form.premium_enabled ? 25 : 3,
                    transition: "left .2s", boxShadow: "0 1px 3px rgba(0,0,0,.2)",
                  }} />
                </div>
                <span style={{ fontWeight: 700, fontSize: 15, color: form.premium_enabled ? "#16a34a" : "#64748b" }}>
                  {form.premium_enabled ? "Premium ieslēgts" : "Premium izslēgts"}
                </span>
              </label>
              {form.premium_enabled && (
                <div style={{ marginTop: 8, fontSize: 13, color: "#64748b", paddingLeft: 60 }}>
                  Lietotāji, kas sasnieguši limitu, nevar pievienot jaunus priekšmetus bez abonēšanas
                </div>
              )}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0 16px" }}>
              <Inp label="Bezmaksas limits (priekšmeti)" value={String(form.premium_free_limit || "")}
                onChange={e => setForm(f => ({ ...f, premium_free_limit: Number(e.target.value) || 0 }))} type="number" />
              <Inp label="Mēneša cena (€)" value={String(form.premium_price_monthly || "")}
                onChange={e => setForm(f => ({ ...f, premium_price_monthly: parseFloat(e.target.value) || 0 }))} type="number" />
              <Inp label="Gada cena (€)" value={String(form.premium_price_yearly || "")}
                onChange={e => setForm(f => ({ ...f, premium_price_yearly: parseFloat(e.target.value) || 0 }))} type="number" />
            </div>

            <button className="btn btn-primary" onClick={() => { setSavedMsg(null); saveMut.mutate(); }} disabled={saveMut.isPending}>
              {saveMut.isPending ? "Saglabā..." : savedMsg ? `✅ ${savedMsg}` : "💾 Saglabāt"}
            </button>
          </>
        )}
      </div>

      {/* Users list */}
      <div style={card}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
          <h3 style={{ fontWeight: 800, fontSize: 16 }}>👥 Lietotāji ({users.length})</h3>
          <input placeholder="🔍 Meklēt..." value={userSearch} onChange={e => setUserSearch(e.target.value)}
            style={{ ...inp, width: 200, padding: "6px 10px" }} />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          {filtered.map(u => {
            const hasSub = !!u.subscription;
            const isOver = form && u.item_count >= (form.premium_free_limit || 50);
            const isGranting = granting === u.id;

            return (
              <div key={u.id} style={{
                border: `1.5px solid ${hasSub ? "#86efac" : isOver && form?.premium_enabled ? "#fca5a5" : "#e2e8f0"}`,
                borderRadius: 10, padding: "10px 14px",
                background: hasSub ? "#f0fdf4" : isOver && form?.premium_enabled ? "#fff5f5" : "#fafafa",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <span style={{ fontWeight: 700, fontSize: 14 }}>{u.username}</span>
                    {u.is_admin && <span style={{ marginLeft: 6, fontSize: 10, background: "#fef3c7", color: "#92400e", padding: "1px 6px", borderRadius: 8, fontWeight: 700 }}>admin</span>}
                    <span style={{ marginLeft: 8, fontSize: 12, color: "#64748b" }}>{u.email}</span>
                    <div style={{ fontSize: 12, color: "#94a3b8", marginTop: 2 }}>
                      {u.item_count} priekšmeti
                      {form?.premium_free_limit > 0 && (
                        <span style={{ marginLeft: 6, color: isOver ? "#dc2626" : "#16a34a" }}>
                          ({isOver ? "virs limita" : `${form.premium_free_limit - u.item_count} brīvi`})
                        </span>
                      )}
                    </div>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                    {hasSub ? (
                      <>
                        <span style={{ fontSize: 12, color: "#16a34a", fontWeight: 700 }}>
                          ✅ {planLabel[u.subscription.plan] || u.subscription.plan}
                          {u.subscription.end_date && ` · līdz ${u.subscription.end_date.slice(0, 10)}`}
                          {!u.subscription.end_date && " · beztermiņa"}
                        </span>
                        <button onClick={() => revokeSub(u.id)} style={{
                          padding: "4px 10px", borderRadius: 6, fontSize: 12, cursor: "pointer",
                          border: "1.5px solid #fca5a5", background: "#fff1f2", color: "#dc2626", fontWeight: 600,
                        }}>Atsaukt</button>
                      </>
                    ) : (
                      <button onClick={() => { setGranting(isGranting ? null : u.id); setGrantForm({ plan: "manual", months: "" }); }} style={{
                        padding: "5px 12px", borderRadius: 6, fontSize: 12, cursor: "pointer",
                        border: "1.5px solid #7c3aed", background: isGranting ? "#f5f3ff" : "#faf5ff",
                        color: "#7c3aed", fontWeight: 600,
                      }}>+ Piešķirt</button>
                    )}
                  </div>
                </div>

                {isGranting && (
                  <div style={{ marginTop: 10, padding: "10px 12px", background: "#f5f3ff", borderRadius: 8, display: "flex", gap: 8, alignItems: "flex-end", flexWrap: "wrap" }}>
                    <div style={{ flex: 1, minWidth: 120 }}>
                      <label style={lbl}>Plāns</label>
                      <select value={grantForm.plan} onChange={e => setGrantForm(f => ({ ...f, plan: e.target.value }))} style={{ ...inp, fontSize: 13, padding: "5px 8px" }}>
                        <option value="manual">Manuāls (beztermiņa)</option>
                        <option value="monthly">Mēneša</option>
                        <option value="yearly">Gada</option>
                      </select>
                    </div>
                    {grantForm.plan !== "manual" && (
                      <div style={{ minWidth: 100 }}>
                        <label style={lbl}>{grantForm.plan === "monthly" ? "Mēneši" : "Gadi"}</label>
                        <input type="number" min={1} value={grantForm.months}
                          onChange={e => setGrantForm(f => ({ ...f, months: e.target.value }))}
                          style={{ ...inp, fontSize: 13, padding: "5px 8px" }} />
                      </div>
                    )}
                    <button onClick={() => grantSub(u.id)} style={{
                      padding: "6px 16px", borderRadius: 6, background: "#7c3aed", color: "#fff",
                      border: "none", fontWeight: 700, fontSize: 13, cursor: "pointer", marginBottom: 1,
                    }}>Piešķirt</button>
                    <button onClick={() => setGranting(null)} style={{
                      padding: "6px 12px", borderRadius: 6, background: "#f1f5f9", color: "#374151",
                      border: "1px solid #e2e8f0", fontSize: 13, cursor: "pointer", marginBottom: 1,
                    }}>Atcelt</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ── Main Admin page ────────────────────────────────────────────────────────────
export default function Admin() {
  const [tab, setTab] = useState("catalog"); // "catalog" | "add" | "structure"
  const [addSub, setAddSub] = useState("item"); // "continent" | "country" | "period" | "item"
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState({});
  const [selected, setSelected] = useState(null);
  const [adminLayout, setAdminLayout] = useState("list"); // "list" | "matrix"
  const [addPrefill, setAddPrefill] = useState(null);
  const [checkedIds, setCheckedIds] = useState(new Set());
  const [bulkConfirm, setBulkConfirm] = useState(false);
  const [bulkDeleting, setBulkDeleting] = useState(false);
  const qc = useQueryClient();

  // Finds continent + country IDs for a given period in the tree
  function treeLocate(section, periodId) {
    for (const cont of (tree?.[section] || [])) {
      for (const country of (cont.children || [])) {
        for (const period of (country.children || [])) {
          if (period.id === periodId) {
            return { continentId: String(cont.id), countryId: String(country.id) };
          }
        }
      }
    }
    return { continentId: "", countryId: "" };
  }

  function openAdd(year, denom) {
    const { continentId, countryId } = filter.periodId
      ? treeLocate(filter.section, filter.periodId)
      : { continentId: "", countryId: "" };
    setAddPrefill({
      cascade: {
        continentId,
        countryId,
        section: filter.section || "",
        coinCat: filter.coinCat || "circulation",
        periodId: filter.periodId ? String(filter.periodId) : "",
      },
      form: {
        year: year || "",
        denomination: denom || "",
      },
    });
    setTab("add");
    setAddSub("item");
  }

  const { data: tree } = useQuery({
    queryKey: ["catalog-tree"],
    queryFn: () => api.get("/catalog/tree").then(r => r.data),
  });

  const params = {};
  if (search) params.search = search;
  if (filter.periodId) params.period_id = filter.periodId;
  else if (filter.section) params.section = filter.section;
  if (filter.coinCat) params.coin_category = filter.coinCat;

  const { data: items = [], isLoading } = useQuery({
    queryKey: ["admin-catalog", params],
    queryFn: () => api.get("/admin/catalog", { params }).then(r => r.data),
    enabled: tab === "catalog",
  });

  const { data: pending = [], refetch: refetchPending } = useQuery({
    queryKey: ["admin-pending"],
    queryFn: () => api.get("/admin/pending").then(r => r.data),
  });
  const { data: pendingCatalog = [], refetch: refetchPendingCatalog } = useQuery({
    queryKey: ["admin-pending-catalog"],
    queryFn: () => api.get("/admin/pending-catalog").then(r => r.data),
  });

  const tabBtn = (t, label) => (
    <button onClick={() => setTab(t)} style={{
      padding: "8px 20px", borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: "pointer",
      background: tab === t ? "#1e3a8a" : "#f1f5f9",
      color: tab === t ? "#fff" : "#374151",
      border: "none",
    }}>{label}</button>
  );

  const subBtn = (s, label) => (
    <button onClick={() => setAddSub(s)} style={{
      padding: "6px 14px", borderRadius: 8, fontWeight: 600, fontSize: 13, cursor: "pointer",
      background: addSub === s ? "#2563eb" : "#f1f5f9",
      color: addSub === s ? "#fff" : "#374151",
      border: addSub === s ? "none" : "1.5px solid #e2e8f0",
    }}>{label}</button>
  );

  return (
    <div style={{ paddingTop: 24, maxWidth: 1200, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 20 }}>
        <h1 style={{ fontWeight: 800, fontSize: 24 }}>🔧 Admin panelis</h1>
        {tab === "catalog" && <span style={{ color: "#94a3b8", fontSize: 14 }}>{items.length} ieraksti</span>}
      </div>

      {/* Main tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {tabBtn("catalog", "📋 Katalogs")}
        {tabBtn("add", "➕ Pievienot")}
        {tabBtn("structure", "🗂️ Struktūra")}
        {tabBtn("numista", "🔍 Numista")}
        {tabBtn("premium", "💎 Premium")}
        <button onClick={() => setTab("pending")} style={{
          padding: "8px 20px", borderRadius: 8, fontWeight: 700, fontSize: 14, cursor: "pointer",
          background: tab === "pending" ? "#dc2626" : (pending.length + pendingCatalog.length > 0 ? "#fef2f2" : "#f1f5f9"),
          color: tab === "pending" ? "#fff" : (pending.length + pendingCatalog.length > 0 ? "#dc2626" : "#374151"),
          border: pending.length + pendingCatalog.length > 0 && tab !== "pending" ? "2px solid #fca5a5" : "none",
        }}>
          Iesniegumi {pending.length + pendingCatalog.length > 0 && `(${pending.length + pendingCatalog.length})`}
        </button>
      </div>

      {/* ── Catalog tab ── */}
      {tab === "catalog" && (
        <>
          <div style={{ marginBottom: 16, display: "flex", gap: 10, alignItems: "center" }}>
            <input placeholder="🔍 Meklēt pēc nosaukuma..." value={search} onChange={e => setSearch(e.target.value)}
              style={{ padding: "8px 12px", borderRadius: 8, border: "1.5px solid #ddd", fontSize: 14, flex: 1, maxWidth: 400 }} />
            <div style={{ display: "flex", border: "1.5px solid #e2e8f0", borderRadius: 8, overflow: "hidden", flexShrink: 0 }}>
              {[["list","≡","Saraksts"],["matrix","⊠","Laikmeta tabula"]].map(([mode, icon, title], i, arr) => (
                <button key={mode} onClick={() => setAdminLayout(mode)} title={title} style={{
                  padding: "7px 13px", border: "none", cursor: "pointer",
                  fontSize: mode === "list" ? 18 : 15, lineHeight: 1, fontWeight: 700,
                  background: adminLayout === mode ? "#1e3a8a" : "#fff",
                  color: adminLayout === mode ? "#fff" : "#64748b",
                  borderRight: i < arr.length - 1 ? "1.5px solid #e2e8f0" : "none",
                }}>{icon}</button>
              ))}
            </div>
          </div>
          <div style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
            <AdminTreeSidebar tree={tree} filter={filter} onSetFilter={f => { setFilter(f); setSelected(null); }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              {isLoading && <p style={{ color: "#888" }}>Ielādē...</p>}
              {!isLoading && items.length === 0 && (
                <p style={{ color: "#94a3b8", textAlign: "center", paddingTop: 40 }}>Nav atrasts neviens ieraksts</p>
              )}

              {/* ── Bulk delete bar ── */}
              {adminLayout === "list" && checkedIds.size > 0 && (
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10,
                  background: bulkConfirm ? "#fef2f2" : "#fff7ed",
                  border: `1.5px solid ${bulkConfirm ? "#fca5a5" : "#fdba74"}`,
                  borderRadius: 10, padding: "8px 14px" }}>
                  <span style={{ fontWeight: 600, fontSize: 13, flex: 1 }}>
                    {bulkConfirm
                      ? `⚠️ Tiešām dzēst ${checkedIds.size} ierakstus? Šo nevar atcelt!`
                      : `Atzīmēti ${checkedIds.size} ieraksti`}
                  </span>
                  {!bulkConfirm ? (
                    <>
                      <button onClick={() => setBulkConfirm(true)} style={{
                        padding: "5px 14px", borderRadius: 7, fontWeight: 700, fontSize: 13,
                        background: "#dc2626", color: "#fff", border: "none", cursor: "pointer" }}>
                        🗑️ Dzēst
                      </button>
                      <button onClick={() => { setCheckedIds(new Set()); setBulkConfirm(false); }} style={{
                        padding: "5px 14px", borderRadius: 7, fontWeight: 600, fontSize: 13,
                        background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0", cursor: "pointer" }}>
                        Atcelt
                      </button>
                    </>
                  ) : (
                    <>
                      <button disabled={bulkDeleting} onClick={async () => {
                        setBulkDeleting(true);
                        for (const id of checkedIds) {
                          try { await api.delete(`/admin/catalog/${id}`); } catch {}
                        }
                        setCheckedIds(new Set());
                        setBulkConfirm(false);
                        setBulkDeleting(false);
                        setSelected(null);
                        qc.invalidateQueries({ queryKey: ["admin-catalog"] });
                      }} style={{
                        padding: "5px 14px", borderRadius: 7, fontWeight: 700, fontSize: 13,
                        background: bulkDeleting ? "#9ca3af" : "#991b1b", color: "#fff", border: "none", cursor: bulkDeleting ? "not-allowed" : "pointer" }}>
                        {bulkDeleting ? "Dzēš..." : "Jā, dzēst!"}
                      </button>
                      <button onClick={() => setBulkConfirm(false)} style={{
                        padding: "5px 14px", borderRadius: 7, fontWeight: 600, fontSize: 13,
                        background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0", cursor: "pointer" }}>
                        Nē
                      </button>
                    </>
                  )}
                </div>
              )}

              {adminLayout === "matrix" ? (
                <MatrixView
                  items={items}
                  onSelect={item => setSelected(selected?.id === item.id ? null : item)}
                  onEmpty={(year, denom) => openAdd(year, denom)}
                  onAddYear={() => openAdd("", "")}
                  onAddDenom={() => openAdd("", "")}
                />
              ) : (
                <>
                  {items.length > 0 && (
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <button onClick={() => {
                        if (checkedIds.size === items.length) { setCheckedIds(new Set()); setBulkConfirm(false); }
                        else setCheckedIds(new Set(items.map(i => i.id)));
                      }} style={{
                        padding: "4px 12px", borderRadius: 6, fontSize: 12, fontWeight: 600, cursor: "pointer",
                        background: "#f1f5f9", color: "#374151", border: "1.5px solid #e2e8f0" }}>
                        {checkedIds.size === items.length ? "Noatzīmēt visus" : "Atzīmēt visus"}
                      </button>
                    </div>
                  )}
                  <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                    {items.map(item => {
                      const isChecked = checkedIds.has(item.id);
                      return (
                        <div key={item.id} onClick={() => setSelected(selected?.id === item.id ? null : item)}
                          style={{ background: isChecked ? "#fef9c3" : selected?.id === item.id ? "#eff6ff" : "#fff",
                            border: `1.5px solid ${isChecked ? "#fbbf24" : selected?.id === item.id ? "#3b82f6" : "#e2e8f0"}`,
                            borderRadius: 10, padding: "10px 14px", cursor: "pointer",
                            display: "flex", alignItems: "center", gap: 12, transition: "border-color .15s" }}>
                          <input type="checkbox" checked={isChecked}
                            onClick={e => e.stopPropagation()}
                            onChange={e => {
                              e.stopPropagation();
                              const next = new Set(checkedIds);
                              if (e.target.checked) next.add(item.id); else next.delete(item.id);
                              setCheckedIds(next);
                              if (!e.target.checked) setBulkConfirm(false);
                            }}
                            style={{ width: 16, height: 16, flexShrink: 0, cursor: "pointer", accentColor: "#dc2626" }} />
                          <div style={{ width: 48, height: 48, borderRadius: 6, overflow: "hidden",
                            background: "#f1f5f9", flexShrink: 0, display: "flex", alignItems: "center", justifyContent: "center" }}>
                            {item.image_url
                              ? <img src={item.image_url.startsWith("http") ? item.image_url : BASE + item.image_url}
                                  style={{ width: "100%", height: "100%", objectFit: "contain" }} alt="" />
                              : <span style={{ fontSize: 20 }}>{item.section === "coins" ? "🪙" : item.section === "medals" ? "🏅" : "📮"}</span>
                            }
                          </div>
                          <div style={{ flex: 1, minWidth: 0 }}>
                            <div style={{ fontWeight: 600, fontSize: 13, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{item.name}</div>
                            <div style={{ fontSize: 12, color: "#64748b" }}>
                              {[item.year, item.denomination].filter(Boolean).join(" · ")}
                              {item.admin_edited && <span style={{ marginLeft: 8, color: "#d97706", fontSize: 11 }}>🔒</span>}
                            </div>
                          </div>
                          <div style={{ display: "flex", gap: 6, flexShrink: 0 }}>
                            {item.image_url && <span style={{ fontSize: 10, background: "#f0fdf4", color: "#16a34a", padding: "2px 6px", borderRadius: 10, fontWeight: 700 }}>OB</span>}
                            {item.image_url_reverse && <span style={{ fontSize: 10, background: "#f0fdf4", color: "#16a34a", padding: "2px 6px", borderRadius: 10, fontWeight: 700 }}>REV</span>}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>
            {selected && (
              <div style={{ width: 420, flexShrink: 0, position: "sticky", top: 72 }}>
                <EditPanel key={selected.id} item={selected} onClose={() => setSelected(null)} />
              </div>
            )}
          </div>
        </>
      )}

      {/* ── Structure tab ── */}
      {tab === "structure" && <StructureTab />}

      {/* ── Numista import tab ── */}
      {tab === "numista" && <NumistaTab />}
      {tab === "premium" && <PremiumTab />}

      {/* ── Pending submissions tab ── */}
      {tab === "pending" && (
        <PendingTab
          pending={pending}
          pendingCatalog={pendingCatalog}
          onRefresh={() => { refetchPending(); refetchPendingCatalog(); }}
        />
      )}

      {/* ── Add tab ── */}
      {tab === "add" && (
        <div style={{ maxWidth: 860 }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
            {subBtn("item",      "🪙 Monēta / ieraksts")}
            {subBtn("period",    "📅 Periods")}
            {subBtn("country",   "🏳️ Valsts")}
            {subBtn("continent", "🌍 Kontinents")}
          </div>
          {addSub === "continent" && <AddContinentForm />}
          {addSub === "country"   && <AddCountryForm />}
          {addSub === "period"    && <AddPeriodForm />}
          {addSub === "item"      && <AddItemForm
            prefill={addPrefill}
            onDuplicate={async (id) => {
              const r = await api.get(`/admin/catalog/${id}`);
              setSelected(r.data);
              setTab("catalog");
            }}
          />}
        </div>
      )}
    </div>
  );
}

