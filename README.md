# Ahorra360
Plataforma nacional de ahorro, ayudas públicas y oportunidades económicas para hogares españoles.

## Ejecutar
```bash
cp .env.example .env.local
npm install
npm run dev
```
Abrir `http://localhost:3000`.

## Calidad
```bash
npm run typecheck
npm test
npm run data:validate
npm run build
```

## Despliegue en Vercel
1. Subir el repositorio a GitHub.
2. Importarlo en Vercel como proyecto Next.js.
3. Definir `NEXT_PUBLIC_SITE_URL` con el dominio definitivo.
4. Mantener `LLM_PROVIDER=disabled` mientras no haya proveedor.
5. Desplegar. No requiere base de datos en el MVP.

## Datos
El catálogo vive en `data/opportunities.json` y se valida con Zod. GitHub Actions ejecuta una comprobación semanal. Los conectores que no estén verificados fallan de forma explícita y no modifican el catálogo.

## Alcance real
Incluye navegación, búsqueda, filtros, fichas, cálculo orientativo, rutas SEO, sitemap, API de búsqueda, modelo de datos, conectores, workflows y tests. No incluye autenticación, OCR, alertas, precios comerciales ni ingestión SNPSAP activa porque requieren configuración, términos o validación adicional. Ninguna de estas capacidades se simula en la interfaz.

## Actualizar el catálogo

```bash
npm run data:update
```

O directamente:

```bash
./scripts/update-catalog.sh
```

Consulta `docs/DATA_PIPELINE.md` para carga completa, dry-run, variables y política de publicación segura.
