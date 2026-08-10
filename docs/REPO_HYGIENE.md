# LexiaTek — higiene del repositorio

## Qué sí va a GitHub

- Código (`site/`, `intake-api/`), workflows, Markdown/HTML de producto.
- Scripts que **generan** decks (`docs/decks/*.py`) y su README.

## Qué no va a GitHub

- Presentaciones (`.pptx`, `.ppt`, `.key`, …)
- Word/Excel/Pages/Numbers
- PDF y archives (`.zip`, …)

Compartir esos archivos por **Google Drive / Slides**. Están en `.gitignore` y CI (`repo-hygiene.yml`) falla si se trackean.

## Agentes / commits

No usar `git add -f` sobre binarios Office. Si el usuario pide subir un deck, recordar esta política.
