/**
 * Nominālvērtību kārtošanas vērtība.
 * Kārtošanas secība: santīmi → lati → eiro centi → eiro → pārējie
 */
export function denomVal(d) {
  if (!d) return Infinity;
  const s = String(d).toLowerCase();
  const m = s.match(/[\d.,]+/);
  const num = m ? parseFloat(m[0].replace(",", ".")) : Infinity;

  if (s.includes("santīm") || s.includes("santim")) return num;
  if (s.includes("lats") || s.includes("lati") || /\blat\b/.test(s)) return 100 + num;
  if (s.includes("cent") || /\bct\b/.test(s)) return 1000 + num;
  if (s.includes("eiro") || s.includes("euro") || /\beur\b/.test(s)) return 2000 + num;
  return 10000 + num;
}
