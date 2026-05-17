import { flagEmoji } from "../utils/flag";

const EXTINCT_CODES = new Set([
  "USSR","YUG","CSK","DDR","PRU","HRE","AHE","OTE","PLC","VEN","PAP","TAS",
  "SAR","BAV","WTB","SAX","HAN","BOH","BYZ","ROM","GRC","CAR","OTT","MNG",
  "PER","PAR","SAF","ABB","UMY","MGL","CRU","CHV","AZT","INC","MAY","BRI",
  "FIN","QIN","MNC","IND","FIC","NEI","TIB","MUG","RHO","CSA","TXS","HAW",
  "EMB","NGR","ZAN","EAF","SOM","MDG",
]);

export default function FlagIcon({ code, style }) {
  if (!code) return null;
  const upper = code.toUpperCase();

  if (upper.length === 2 && !EXTINCT_CODES.has(upper)) {
    return (
      <span
        className={`fi fi-${upper.toLowerCase()}`}
        style={{ width: 20, height: 15, display: "inline-block", verticalAlign: "middle", borderRadius: 2, flexShrink: 0, ...style }}
      />
    );
  }

  // Vēsturiskās valstis — simbols no flagEmoji
  return <span style={{ fontSize: 14, verticalAlign: "middle", ...style }}>{flagEmoji(upper)}</span>;
}
