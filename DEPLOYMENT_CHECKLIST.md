# Checklist de despliegue Ahorra360 v2

- [ ] Subir el proyecto a GitHub.
- [ ] Confirmar que `npm run check:data` termina correctamente.
- [ ] Ejecutar `npm install` y `npm run build` en local o CI.
- [ ] Importar el repositorio en Vercel como proyecto Next.js.
- [ ] Configurar `NEXT_PUBLIC_SITE_URL` con el dominio real.
- [ ] Confirmar que no se requiere ninguna base de datos ni servicio de IA.
- [ ] Si se quiere publicar desde `/admin`, configurar `ADMIN_PASSWORD`, `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO` y opcionalmente `GITHUB_BRANCH`.
- [ ] Limitar el token GitHub a Contents read/write en el repositorio de Ahorra360.
- [ ] Revisar el workflow GitHub Actions y los permisos de escritura del repositorio.
- [ ] Ejecutar manualmente `Monitor de fuentes oficiales` desde Actions.
- [ ] Revisar `/`, `/fuentes`, `/metodologia`, `/admin`, `/robots.txt` y `/sitemap.xml`.
- [ ] Completar aviso legal, privacidad y contacto con los datos reales del titular.
- [ ] Revisar todas las fichas y sus convocatorias antes de promocionar el portal.
- [ ] Confirmar las condiciones de Vercel Hobby antes de activar monetización comercial.
- [ ] Si vas a usar Google Analytics, configurar `GA_MEASUREMENT_ID` en `config/analytics.ts` y revisar la política de privacidad/cookies.
