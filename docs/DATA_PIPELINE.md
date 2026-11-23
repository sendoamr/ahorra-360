# Actualización del catálogo

## Un comando

```bash
npm run data:update
```

Alternativa Bash:

```bash
./scripts/update-catalog.sh
```

Por defecto descarga los últimos 14 días desde la API oficial SNPSAP/BDNS, normaliza, clasifica la relevancia para hogares, deduplica por código BDNS, valida y publica atómicamente en `data/published/opportunities.json`.

## Opciones

```bash
npm run data:update -- --days 30
npm run data:update -- --include-low
npm run data:update:dry
npm run data:update:full
```

`--full` puede ser costoso. Controle `SYNC_MAX_PAGES`, `SYNC_PAGE_SIZE` y `SYNC_DELAY_SECONDS`. El pipeline nunca sustituye el catálogo publicado si la descarga o validación falla.

## Variables

- `SNPSAP_API_BASE`: servidor oficial; valor por defecto `https://www.subvenciones.gob.es/bdnstrans/api`.
- `SYNC_DAYS`: ventana incremental, 14 por defecto.
- `SYNC_PAGE_SIZE`: 100 por defecto.
- `SYNC_MAX_PAGES`: 20 por defecto.
- `SYNC_DELAY_SECONDS`: pausa respetuosa, 0.5 s por defecto.

## Salidas

- `data/raw/snpsap/*.json`: respuesta original para auditoría.
- `data/published/opportunities.json`: catálogo consumido por Next.js.
- `data/published/metadata.json`: métricas de ejecución.
- `data/state/sync.json`: última sincronización correcta.

## Limitaciones de clasificación

La clasificación inicial usa reglas explicables. Registros de baja relevancia no se publican salvo `--include-low`. La cuantía, requisitos y fechas ausentes permanecen nulos; no se infieren.
