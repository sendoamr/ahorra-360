# Quality gates

Automated commands: `npm run typecheck`, `npm test`, `npm run data:validate`, `npm run build`.

Manual smoke test after install:
- `/`: search submits and navigates.
- `/ayudas`: free-text and status filters combine.
- `/ayudas/[slug]`: official source opens in a new tab.
- `/herramientas`: values update and inputs clamp negative outcomes.
- Responsive widths: 320, 768, 1280 px.
- Keyboard: visible focus, labelled input/select, semantic headings.

The delivery environment could not complete `npm install` within its per-command network time limit. Run `npm install && npm run typecheck && npm test && npm run data:validate && npm run build` in CI or locally before production deployment.
