'use client';

import { useMemo, useState } from 'react';
import initial from '@/data/opportunities.json';

type Row = Record<string, unknown>;
const starter = JSON.stringify(initial, null, 2);

export default function EditorialWorkspace() {
  const [json, setJson] = useState(starter);
  const [message, setMessage] = useState('');
  const [fileName, setFileName] = useState('opportunities.json');
  const [password, setPassword] = useState('');
  const [publishing, setPublishing] = useState(false);
  const parsed = useMemo(() => {
    try {
      const value = JSON.parse(json);
      if (!Array.isArray(value)) return { ok: false, count: 0, error: 'El catálogo debe ser un array JSON.' };
      const ids = new Set<string>();
      const slugs = new Set<string>();
      for (const [i, row] of value.entries()) {
        if (!row || typeof row !== 'object') return { ok: false, count: value.length, error: `La ficha ${i + 1} no es un objeto.` };
        const item = row as Row;
        if (!item.id || !item.slug || !item.title || !item.sources || !item.verifiedAt) return { ok: false, count: value.length, error: `La ficha ${i + 1} necesita id, slug, title, sources y verifiedAt.` };
        if (ids.has(String(item.id))) return { ok: false, count: value.length, error: `ID duplicado: ${item.id}` };
        if (slugs.has(String(item.slug))) return { ok: false, count: value.length, error: `Slug duplicado: ${item.slug}` };
        ids.add(String(item.id)); slugs.add(String(item.slug));
        if (!Array.isArray(item.sources) || item.sources.length === 0) return { ok: false, count: value.length, error: `La ficha ${item.title} no tiene fuentes.` };
      }
      return { ok: true, count: value.length, error: '' };
    } catch (error) {
      return { ok: false, count: 0, error: error instanceof Error ? error.message : 'JSON no válido.' };
    }
  }, [json]);

  function download() {
    const blob = new Blob([json.endsWith('\n') ? json : `${json}\n`], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = fileName; a.click(); URL.revokeObjectURL(url);
    setMessage('Archivo preparado. Sustituye data/opportunities.json en el repositorio y haz commit para desplegarlo.');
  }
  async function publish() {
    if (!parsed.ok || !password) return;
    setPublishing(true); setMessage('Enviando el catálogo a GitHub…');
    try {
      const response = await fetch('/api/admin/publish', { method: 'POST', headers: { 'Content-Type': 'application/json', 'x-admin-password': password }, body: json });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error || 'No se pudo publicar.');
      setMessage(result.message + (result.commit ? ` Commit: ${result.commit}` : ''));
    } catch (error) { setMessage(error instanceof Error ? error.message : 'Error publicando el catálogo.'); }
    finally { setPublishing(false); }
  }
  function importFile(file?: File) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => { setJson(String(reader.result ?? '')); setFileName(file.name.endsWith('.json') ? file.name : 'opportunities.json'); setMessage(`Importado ${file.name}. Revisa la validación antes de exportar.`); };
    reader.readAsText(file);
  }

  return <main className="admin-page"><div className="container admin-container">
    <div className="eyebrow">ESPACIO EDITORIAL LOCAL</div>
    <h1>Gestión del catálogo</h1>
    <p className="admin-intro">Edita y valida el catálogo de oportunidades desde tu navegador. No necesita base de datos: puedes descargar el JSON o publicarlo directamente en GitHub si activas la integración opcional.</p>
    <div className="admin-notice"><strong>Importante:</strong> el editor no guarda borradores en el servidor. La publicación directa solo está disponible si se configuran las variables de GitHub y la contraseña editorial. No introduzcas datos personales ni secretos.</div>
    <div className="admin-stats"><div><strong>{parsed.count}</strong><span>Fichas en el editor</span></div><div><strong className={parsed.ok ? 'valid' : 'invalid'}>{parsed.ok ? 'Correcto' : 'Error'}</strong><span>Validación estructural</span></div></div>
    <div className="admin-actions"><label className="button-secondary">Importar JSON<input type="file" accept="application/json,.json" hidden onChange={e => importFile(e.target.files?.[0])}/></label><button className="button-primary" onClick={download} disabled={!parsed.ok}>Descargar catálogo validado</button><button className="button-secondary" onClick={() => {setJson(starter);setMessage('Catálogo original restaurado en el editor.');}}>Restaurar original</button></div>
    <div className="admin-publish"><div><strong>Publicar directamente en GitHub (opcional)</strong><p>Requiere configurar las variables de entorno descritas en el README. El token de GitHub nunca se envía al navegador.</p></div><input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} placeholder="Contraseña editorial" aria-label="Contraseña editorial"/><button className="button-primary" onClick={publish} disabled={!parsed.ok || !password || publishing}>{publishing ? 'Publicando…' : 'Publicar y desplegar'}</button></div>
    <label className="admin-label" htmlFor="catalog-json">Catálogo JSON</label>
    <textarea id="catalog-json" className="json-editor" spellCheck={false} value={json} onChange={e => setJson(e.target.value)} />
    <div className={parsed.ok ? 'validation validation-ok' : 'validation validation-error'}>{parsed.ok ? `✓ JSON válido · ${parsed.count} fichas · IDs y slugs únicos · todas las fichas tienen fuente.` : `✕ ${parsed.error}`}</div>
    {message && <p className="admin-message" role="status">{message}</p>}
    <section className="admin-how"><h2>Cómo publicar los cambios</h2><ol><li>Descarga el JSON validado o utiliza la publicación directa opcional.</li><li>Si publicas manualmente, sustituye <code>data/opportunities.json</code> en GitHub y haz commit.</li><li>Vercel detectará el commit y desplegará la nueva versión.</li><li>Comprueba la ficha publicada y sus fuentes.</li></ol><p>La validación del navegador es básica. Antes de publicar, ejecuta también <code>npm run check:data</code> en el proyecto.</p></section>
  </div></main>;
}
