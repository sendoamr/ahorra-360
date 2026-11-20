import { NextRequest, NextResponse } from 'next/server';
import { timingSafeEqual } from 'node:crypto';

export const runtime = 'nodejs';

function authorized(request: NextRequest) {
  const expected = process.env.ADMIN_PASSWORD || '';
  const supplied = request.headers.get('x-admin-password') || '';
  if (!expected || !supplied) return false;
  const a = Buffer.from(expected);
  const b = Buffer.from(supplied);
  return a.length === b.length && timingSafeEqual(a, b);
}

function validateCatalog(value: unknown): string | null {
  if (!Array.isArray(value)) return 'El catálogo debe ser un array JSON.';
  const ids = new Set<string>();
  const slugs = new Set<string>();
  const categories = new Set(['vivienda', 'suministros', 'fiscalidad', 'oportunidades']);
  const statuses = new Set(['vigente', 'permanente', 'informativo', 'revision', 'cerrado']);
  for (const [index, row] of value.entries()) {
    if (!row || typeof row !== 'object') return `La ficha ${index + 1} no es un objeto.`;
    const item = row as Record<string, unknown>;
    for (const key of ['id', 'slug', 'title', 'subtitle', 'audience', 'howTo', 'deadline', 'verifiedAt']) {
      if (typeof item[key] !== 'string' || !item[key]) return `La ficha ${index + 1}: falta ${key}.`;
    }
    const id = String(item.id); const slug = String(item.slug);
    if (ids.has(id)) return `ID duplicado: ${id}`;
    if (slugs.has(slug)) return `Slug duplicado: ${slug}`;
    ids.add(id); slugs.add(slug);
    if (!categories.has(String(item.category))) return `Categoría inválida en ${slug}.`;
    if (!statuses.has(String(item.status))) return `Estado inválido en ${slug}.`;
    if (!Array.isArray(item.requirements) || !item.requirements.length) return `Faltan requisitos en ${slug}.`;
    if (!Array.isArray(item.sources) || !item.sources.length) return `Faltan fuentes en ${slug}.`;
    for (const source of item.sources as Record<string, unknown>[]) {
      try { if (new URL(String(source.url)).protocol !== 'https:') throw new Error(); }
      catch { return `Fuente HTTPS inválida en ${slug}.`; }
    }
  }
  return null;
}

export async function POST(request: NextRequest) {
  if (!authorized(request)) return NextResponse.json({ error: 'Contraseña editorial incorrecta.' }, { status: 401 });
  const token = process.env.GITHUB_TOKEN;
  const owner = process.env.GITHUB_OWNER;
  const repo = process.env.GITHUB_REPO;
  const branch = process.env.GITHUB_BRANCH || 'main';
  if (!token || !owner || !repo) return NextResponse.json({ error: 'Falta configurar GITHUB_TOKEN, GITHUB_OWNER y GITHUB_REPO en Vercel.' }, { status: 503 });

  try {
    const declaredLength = Number(request.headers.get('content-length') || 0);
    if (declaredLength > 1_500_000) return NextResponse.json({ error: 'El catálogo supera el tamaño máximo permitido (1,5 MB).' }, { status: 413 });
    const catalog = await request.json();
    const invalid = validateCatalog(catalog);
    if (invalid) return NextResponse.json({ error: invalid }, { status: 400 });
    const apiUrl = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/contents/data/opportunities.json`;
    const headers = { Authorization: `Bearer ${token}`, Accept: 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json' };
    const current = await fetch(`${apiUrl}?ref=${encodeURIComponent(branch)}`, { headers, cache: 'no-store' });
    if (!current.ok) return NextResponse.json({ error: `GitHub no pudo leer el catálogo (${current.status}). Comprueba repositorio, rama y permisos del token.` }, { status: 502 });
    const currentFile = await current.json() as { sha?: string };
    if (!currentFile.sha) return NextResponse.json({ error: 'GitHub no devolvió el SHA del archivo.' }, { status: 502 });
    const content = Buffer.from(`${JSON.stringify(catalog, null, 2)}\n`, 'utf8').toString('base64');
    const saved = await fetch(apiUrl, {
      method: 'PUT', headers, cache: 'no-store',
      body: JSON.stringify({ message: 'content: update Ahorra360 opportunities catalog', content, sha: currentFile.sha, branch })
    });
    const responseBody = await saved.json().catch(() => ({}));
    if (!saved.ok) return NextResponse.json({ error: `GitHub rechazó la publicación (${saved.status}). ${responseBody.message || ''}` }, { status: 502 });
    return NextResponse.json({ ok: true, message: 'Catálogo guardado en GitHub. Vercel iniciará un nuevo despliegue.', commit: responseBody.commit?.html_url || null });
  } catch (error) {
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Error procesando el catálogo.' }, { status: 400 });
  }
}
