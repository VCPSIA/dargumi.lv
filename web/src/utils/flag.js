// Extinct/historical countries with custom icons (no standard flag emoji)
const EXTINCT_ICONS = {
  USSR: "☆", YUG: "★", CSK: "✦", DDR: "✦",
  PRU: "⚜", HRE: "⚜", AHE: "⚜", OTE: "☽",
  PLC: "⚜", VEN: "🦁", PAP: "✝", TAS: "⚜",
  SAR: "⚜", BAV: "⚜", WTB: "⚜", SAX: "⚜",
  HAN: "⚜", BOH: "⚜", BYZ: "☦", ROM: "⚜",
  GRC: "⚜", CAR: "⚜", OTT: "☽", MNG: "⚜",
  PER: "⚜", PAR: "⚜", SAF: "⚜", ABB: "☽",
  UMY: "☽", MGL: "⚜", CRU: "✝", CHV: "⚜",
  AZT: "⚜", INC: "⚜", MAY: "⚜", BRI: "⚜",
  FIN: "⚜", QIN: "⚜", MNC: "⚜", IND: "⚜",
  FIC: "⚜", NEI: "⚜", TIB: "⚜", MUG: "⚜",
  RHO: "⚜", CSA: "⚜", TXS: "⚜", HAW: "⚜",
  EMB: "⚜", NGR: "⚜", ZAN: "⚜", EAF: "⚜",
  SOM: "⚜", MDG: "⚜",
};

export function flagEmoji(code) {
  if (!code) return "";
  const upper = code.toUpperCase();
  if (upper.length === 2) {
    // Standard ISO 3166-1 alpha-2 → Unicode regional indicator symbols
    return [...upper].map(c => String.fromCodePoint(c.charCodeAt(0) + 0x1F1A5)).join("");
  }
  // Extinct/historical — use mapped icon or generic black flag
  return EXTINCT_ICONS[upper] || "🏴";
}
