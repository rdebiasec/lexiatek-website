# LexiaTek — Decks (local, no van a Git)

Los `.pptx` **no se versionan** (ver `.gitignore`). Genera en tu máquina y comparte por Drive/Slides.

## Ayuda oral — propuesta de asociación

El documento que se entrega es el Word (`docs/propuesta/`). Este PowerPoint es **solo ayuda oral**. No se deja como hoja de términos ni como contrato.

**Plantilla visual:** `LexiaTek_Alexia_Letigia_Abogados_v1` (navy / teal / oro, Arial, notas de orador). Registro formal. Nombres: Michele Aguilar y Ricardo De Biase.

```bash
cd docs/decks
python3 build_plan_negocios_abogada.py
```

Salida local: `LexiaTek_Plan_Negocios_Abogada.pptx` (11 láminas).

Orden: portada → tensiones → socios y funciones → licencias recíprocas → alcance (penal, civil, laboral, acoso sexual, PQRS, tutelas y trámites) → propósito → estado actual → operación diaria → régimen económico → hoja de ruta (contratos, constitución, cumplimiento, clientes) → solicitud.

No genera hoja de términos ni guion en Markdown.

## Onboarding del despacho virtual

```bash
cd docs/decks
python3 build_onboarding_deck_v2.py
```

Salida esperada: `LexiaTek_Onboarding_Despacho_Virtual.pptx` (solo local).

Onboarding no técnico, con foco en la abogada: agentes, skills, herramientas, tareas de inicio a cierre. Regla de oro: *la IA propone; la abogada revisa, ajusta y aprueba*. Ese deck no es el plan de negocios.

## Abrir como Google Slides (30 s)

1. Sube el `.pptx` a [Google Drive](https://drive.google.com).
2. Clic derecho → **Abrir con** → **Google Slides**.
3. (Opcional) **Archivo → Guardar como Google Slides** para una copia nativa editable.

## Política del repo

No subir presentaciones, PDFs ni Office a GitHub. Compartir por Drive/Slides. CI falla si aparecen en el árbol trackeado.
