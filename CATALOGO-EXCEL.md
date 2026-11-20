# Gestor del catálogo de Ahorra360 (Excel + Python)

Este gestor permite mantener `data/opportunities.json` sin editar JSON a mano. No usa base de datos,
servicios externos ni IA. Solo requiere Python 3.10+ y `openpyxl`.

## Instalación

Desde la carpeta raíz del proyecto:

```bash
python -m pip install -r requirements-catalog.txt
```

## 1. Exportar el catálogo actual a Excel

```bash
python tools/catalog_manager.py export
```

Se genera `catalogo-ahorra360.xlsx` con tres hojas:

- **Oportunidades**: una fila por ayuda, descuento o programa. Cada campo de la ficha tiene su columna.
- **Fuentes**: una fila por fuente; `opportunity_id` relaciona la fuente con su oportunidad.
- **LEEME**: instrucciones dentro del propio Excel.

También puedes indicar rutas:

```bash
python tools/catalog_manager.py export --catalog data/opportunities.json --output trabajo.xlsx
```

## 2. Gestionar el Excel

- Para crear una oportunidad, añade una fila en **Oportunidades**.
- Usa un `id` único y estable, por ejemplo `ayuda-alquiler-catalunya-2027`.
- `slug` es la parte final de la URL y también debe ser único.
- En `requirements`, escribe un requisito por línea dentro de la celda.
- Añade al menos una fuente en **Fuentes**, con el mismo `opportunity_id`.
- Para publicar, usa `editorialStatus = published`.
- Para retirar una ficha sin perder su histórico, usa `editorialStatus = archived`.
- `verifiedAt` debe ser una fecha `AAAA-MM-DD`.
- Las fuentes deben incluir URL HTTP/HTTPS válida.

Los desplegables ayudan con categoría, estado, confianza y estado editorial. Puedes ampliar las listas en
`tools/catalog_manager.py` si incorporas nuevas categorías.

## 3. Importar y validar

Fusionar las filas del Excel con el catálogo actual (recomendado):

```bash
python tools/catalog_manager.py import --input catalogo-ahorra360.xlsx
```

La fusión se hace por `id`: si el ID ya existe, actualiza esa oportunidad; si es nuevo, la añade.
Las oportunidades que no aparezcan en el Excel se conservan. Antes de escribir, valida campos,
IDs/slugs duplicados, requisitos, fechas y fuentes. Si falla una validación, no modifica el JSON.
Al importar crea además `data/opportunities.json.bak`.

Para sustituir completamente el catálogo por el Excel:

```bash
python tools/catalog_manager.py import --input catalogo-ahorra360.xlsx --replace
```

Usa `--replace` solo si realmente quieres eliminar del catálogo las oportunidades que no estén
en el fichero Excel.

Validar sin importar:

```bash
python tools/catalog_manager.py validate
```

## 4. Publicar en la web

Después de una importación correcta:

```bash
git add data/opportunities.json
git commit -m "Actualiza catálogo de oportunidades"
git push
```

Vercel desplegará automáticamente el cambio si el repositorio está conectado.

## Qué automatiza y qué no

El gestor automatiza la edición estructurada, la relación entre oportunidades y fuentes, la fusión
de registros y las validaciones técnicas. **No verifica el contenido jurídico ni si una convocatoria
sigue abierta**: eso requiere revisar la fuente oficial y actualizar `status`, `statusLabel`,
`deadline` y `verifiedAt`. No publiques una ayuda solo porque el Excel pase la validación.
