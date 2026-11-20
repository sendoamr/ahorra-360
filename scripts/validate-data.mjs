import fs from 'node:fs';
const data = JSON.parse(fs.readFileSync(new URL('../data/opportunities.json', import.meta.url), 'utf8'));
const sources = JSON.parse(fs.readFileSync(new URL('../data/sources.json', import.meta.url), 'utf8'));
const errors = [];
const ids = new Set(); const slugs = new Set();
const categories = ['vivienda','suministros','fiscalidad','oportunidades'];
const statuses = ['vigente','permanente','informativo','revision','cerrado'];
for (const [i,x] of data.entries()) {
  const label = x.slug || `fila ${i+1}`;
  for (const key of ['id','slug','title','subtitle','audience','howTo','deadline','verifiedAt']) if (!x[key]) errors.push(`${label}: falta ${key}`);
  if (ids.has(x.id)) errors.push(`ID duplicado: ${x.id}`); ids.add(x.id);
  if (slugs.has(x.slug)) errors.push(`Slug duplicado: ${x.slug}`); slugs.add(x.slug);
  if (!categories.includes(x.category)) errors.push(`${label}: categoría inválida ${x.category}`);
  if (!statuses.includes(x.status)) errors.push(`${label}: estado inválido ${x.status}`);
  if (!Array.isArray(x.requirements) || !x.requirements.length) errors.push(`${label}: requisitos vacíos`);
  if (!Array.isArray(x.sources) || !x.sources.length) errors.push(`${label}: sin fuentes`);
  for (const source of x.sources || []) { try { const u = new URL(source.url); if (u.protocol !== 'https:') throw new Error(); } catch { errors.push(`${label}: URL de fuente no HTTPS válida: ${source.url}`); } }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(x.verifiedAt || '') || Number.isNaN(Date.parse(x.verifiedAt))) errors.push(`${label}: verifiedAt debe ser YYYY-MM-DD`);
  if (!['alta','media','baja'].includes(x.confidence)) errors.push(`${label}: confianza inválida`);
}
const sourceIds = new Set();
for (const source of sources) { if (sourceIds.has(source.id)) errors.push(`Fuente duplicada: ${source.id}`); sourceIds.add(source.id); try { if (new URL(source.url).protocol !== 'https:') throw new Error(); } catch { errors.push(`URL de fuente inválida: ${source.id}`); } }
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
console.log(`OK: ${data.length} oportunidades, ${slugs.size} slugs únicos y ${sources.length} fuentes oficiales.`);
