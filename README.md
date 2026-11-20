# Ahorra360 — portal de ayudas y oportunidades

Portal Next.js para informar sobre ayudas públicas, beneficios fiscales, descuentos y oportunidades de ahorro. Diseñado para desplegar el portal público en Vercel sin base de datos externa ni API de IA de pago.

## Arquitectura sin base de datos

- **Web:** Next.js App Router, React y TypeScript.
- **Hosting:** Vercel.
- **Datos editoriales:** JSON versionado en Git (`data/opportunities.json`, `data/sources.json`).
- **Histórico:** Git conserva el historial de cambios del catálogo y de las fuentes.
- **Monitor de fuentes:** Python estándar + GitHub Actions. Comprueba disponibilidad y huellas de contenido de las páginas oficiales registradas.
- **Panel editorial:** `/admin`, editor en navegador para importar, editar y validar el JSON. Puede descargar el archivo o, si se configura, publicarlo directamente en GitHub mediante una API protegida.
- **IA:** no se requiere.

No hay Supabase, PostgreSQL, almacenamiento externo ni claves de servicio.

## Requisitos

- Node.js 20.9 o superior.
- npm.
- Python 3.10 o superior para ejecutar el monitor de fuentes.

## Desarrollo local

```bash
npm install
npm run dev
```

Abrir http://localhost:3000.

## Validación del catálogo

```bash
npm run check:data
```

Valida IDs y slugs únicos, campos obligatorios, categorías, estados, fechas, fuentes HTTPS y estructura básica.

## Panel editorial

Abrir `/admin` en la web o en local.

1. Editar el JSON directamente o importar un archivo.
2. Revisar el resultado de la validación en pantalla.
3. Descargar `opportunities.json`.
4. Sustituir `data/opportunities.json` en el repositorio GitHub.
5. Ejecutar `npm run check:data` y hacer commit.
6. Vercel desplegará el cambio mediante la integración Git.

**Importante:** `/admin` no es un CMS multiusuario. Sin configuración adicional, funciona como editor local y descarga el JSON. Para publicar directamente desde el panel, configura estas variables de entorno en Vercel:

- `ADMIN_PASSWORD`: contraseña larga y exclusiva para el panel editorial.
- `GITHUB_TOKEN`: token GitHub con permiso de lectura y escritura de Contents únicamente sobre el repositorio del portal.
- `GITHUB_OWNER`: usuario u organización propietaria del repositorio.
- `GITHUB_REPO`: nombre del repositorio.
- `GITHUB_BRANCH`: rama de publicación (opcional; por defecto `main`).

La API de publicación comprueba la contraseña en el servidor, valida el catálogo y crea un commit sobre `data/opportunities.json`. El token nunca se entrega al navegador. Vercel despliega el commit mediante la integración Git. Si no configuras estas variables, sigue funcionando la descarga manual. No introduzcas datos personales en el catálogo.

## Monitorización de fuentes

El registro de organismos está en `data/sources.json`. El script `scripts/monitor_sources.py`:

- Solo consulta URLs HTTPS declaradas en el catálogo de fuentes.
- Comprueba respuesta HTTP, URL final y tipo de contenido.
- Calcula un hash SHA-256 del contenido normalizado.
- Compara el hash con la ejecución anterior, guardada en `data/source-monitor.json`.
- Registra cambios como señales para revisión editorial.

Ejecución manual:

```bash
python3 scripts/monitor_sources.py
```

GitHub Actions ejecuta el monitor de lunes a viernes a las 05:23 UTC y actualiza el informe si detecta diferencias. El workflow necesita permiso `contents: write`, ya declarado en el propio YAML.

**Límite funcional deliberado:** el monitor no interpreta automáticamente documentos legales ni cambia el estado de las ayudas. Un hash distinto puede deberse a cambios de diseño, banners o contenido dinámico. Es una alerta de revisión, no una prueba de modificación de convocatoria. No se publica automáticamente ninguna condición nueva.

## Añadir una fuente

Añadir un objeto a `data/sources.json`:

```json
{
  "id": "organismo-id",
  "name": "Nombre del organismo",
  "scope": "Cataluña",
  "kind": "portal",
  "url": "https://organismo.example/",
  "priority": "alta",
  "reviewFrequency": "weekly",
  "notes": "Qué información oficial ofrece."
}
```

Utilizar URLs HTTPS oficiales. No añadir endpoints privados, URLs con credenciales ni fuentes sin revisar sus condiciones de uso y políticas de acceso automatizado.

## Añadir o modificar una oportunidad

El tipo de datos está definido en `lib/data.ts`. Cada ficha debe incluir como mínimo:

- `id`, `slug`, `title`, `subtitle`.
- `category`, `scope`, `region`.
- `status`, `statusLabel`.
- `amount`, `amountNote`.
- `audience`, `requirements`, `howTo`, `deadline`, `notes`.
- `sources` con nombre, URL oficial y tipo.
- `verifiedAt`, `reviewFrequency`, `confidence`, `editorialStatus`.

Estados editoriales: `vigente`, `permanente`, `informativo`, `revision`, `cerrado`. No confundir anuncio político, norma publicada y convocatoria abierta. Los préstamos deben identificarse como financiación reembolsable, no como subvención.

## Despliegue en Vercel

1. Subir el contenido del proyecto a un repositorio GitHub.
2. Importar el repositorio en Vercel.
3. Seleccionar Next.js y dejar el comando de build predeterminado (`next build`).
4. No configurar variables de entorno para el funcionamiento básico.
5. Definir `NEXT_PUBLIC_SITE_URL` con el dominio definitivo (por ejemplo `https://ahorra360.es`).
6. Configurar el dominio en Vercel.
7. Verificar `/`, `/fuentes`, `/metodologia`, `/admin`, `/robots.txt` y `/sitemap.xml`.

## Costes y límites

La aplicación no necesita base de datos, API de IA, almacenamiento externo ni servicio de correo. GitHub Actions tiene cuotas y límites según el plan y la visibilidad del repositorio. El hosting Vercel Hobby está sujeto a sus condiciones vigentes, límites y restricciones de uso comercial. Antes de monetizar con publicidad o afiliación, confirmar que el plan elegido permite ese uso; si no, habrá que presupuestar un plan compatible.

No se puede garantizar coste cero absoluto: dominio, posibles excesos de cuota y servicios que se incorporen en el futuro pueden generar costes.

## SEO, privacidad y lanzamiento

- Sustituir `TU-DOMINIO.es` en `app/robots.ts` y definir `NEXT_PUBLIC_SITE_URL`.
- Completar datos legales del titular y canales de contacto.
- Revisar privacidad, cookies y consentimiento antes de añadir analítica o publicidad no esencial.
- No activar anuncios hasta tener tráfico y revisar el cumplimiento normativo.
- Revisar manualmente las fichas, sus plazos y las fuentes antes de hacerlas públicas.
- Configurar Search Console y analítica solo cuando se haya decidido qué herramientas utilizar.

## Estructura

- `app/`: páginas y rutas Next.js.
- `components/`: componentes de interfaz.
- `data/opportunities.json`: catálogo editorial.
- `data/sources.json`: registro de fuentes oficiales.
- `data/source-monitor.json`: último informe de monitorización.
- `scripts/validate-data.mjs`: validador de datos.
- `scripts/monitor_sources.py`: monitor técnico de fuentes.
- `.github/workflows/monitor-sources.yml`: ejecución programada.

## Limitaciones conocidas

El monitor comprueba páginas raíz institucionales, no descubre todas las convocatorias ni sustituye la lectura de boletines y bases reguladoras. La extracción automática de convocatorias desde RSS, APIs o documentos PDF debe añadirse con conectores específicos y validación editorial. El panel `/admin` exporta JSON y puede publicar mediante GitHub si se configuran las variables opcionales; no utiliza una base de datos. El portal no presta asesoramiento jurídico, fiscal ni financiero.

## Google Analytics 4

Ahorra360 incluye integración opcional con Google Analytics 4 y un aviso de consentimiento
para las cookies analíticas.

1. Abre `config/analytics.ts`.
2. Sustituye el valor vacío de `GA_MEASUREMENT_ID` por tu identificador, por ejemplo
   `G-XXXXXXXXXX`.
3. Guarda el cambio y despliega de nuevo en Vercel.

Si el identificador está vacío, Google Analytics queda desactivado y no se muestra el aviso
de consentimiento de analítica. Cuando está configurado, Analytics solo se carga después de
que el visitante pulse **Aceptar analítica**. Si pulsa **Rechazar**, no se carga.
La elección se guarda en el navegador para no volver a mostrar el aviso en cada visita.

Para cambiar el identificador en el futuro, solo tendrás que modificar `config/analytics.ts`.
Antes de publicar, revisa también la política de privacidad y la configuración de cookies
para que describan correctamente las herramientas y finalidades que utilices.
