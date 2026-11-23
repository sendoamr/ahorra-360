# Arquitectura Ahorra360

## Decisiones
- Next.js App Router y datos JSON versionados para un MVP desplegable en Vercel sin base de datos.
- Capas: UI (`app`, `components`), dominio (`lib`, `features`, `types`), datos (`data`) e ingestión (`scripts/connectors`).
- La vigencia se deriva de fechas, agotamiento y verificación. Nunca se etiqueta una convocatoria como abierta solo por estar publicada.
- Actualización fuera de Vercel mediante GitHub Actions. El catálogo previo se conserva si falla una fuente.

## Pipeline
Descubrir → obtener → extraer → normalizar → deduplicar → validar → derivar estado → enriquecer → publicar. La publicación es atómica: primero se crea un catálogo candidato, se valida y solo entonces sustituye al vigente.

## Evolución PostgreSQL/Supabase
Las claves de `Opportunity` se trasladan a `opportunities`, `sources`, `territories`, `requirements`, `beneficiaries` y `opportunity_versions`. Mantener repositorios para evitar acoplar React a SQL.

## IA
El proveedor se habilita mediante `LLM_PROVIDER`/`LLM_API_KEY`. La IA solo extrae intención y explica coincidencias del catálogo. Si falla, la búsqueda textual y los filtros siguen disponibles.

## Facturas
Flujo futuro: subida directa a almacenamiento efímero → antivirus → OCR/document AI → campos detectados → confirmación → cálculo → borrado. No almacenar PDF por defecto. Requiere DPA, retención explícita y proveedor configurado.

## Seguridad
Zod en límites, secretos solo servidor, CSP antes de producción, rate limiting en endpoints con coste, sanitización de contenido externo, logs sin PII, revisión RGPD/LSSI.
