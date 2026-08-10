# LexiaTek — Onboarding Despacho Virtual

## Cómo generar (local, no va a Git)

Los `.pptx` **no se versionan** (ver `.gitignore`). Genera el deck en tu máquina:

```bash
cd docs/decks
python3 build_onboarding_deck_v2.py
```

Salida esperada: `LexiaTek_Onboarding_Despacho_Virtual.pptx` (solo local).

## Abrir como Google Slides (30 s)

1. Sube el `.pptx` a [Google Drive](https://drive.google.com).
2. Clic derecho → **Abrir con** → **Google Slides**.
3. (Opcional) **Archivo → Guardar como Google Slides** para una copia nativa editable.

## Contenido

Onboarding no técnico, con foco en la abogada:

- concepto de agentes dedicados a funciones;
- diferencia entre agente, skill y herramienta;
- herramientas implementadas para expediente y conocimiento;
- arquitectura y ciclo de vida de una tarea;
- responsabilidades, skills, entradas, salidas y límites de los 10 agentes;
- cinco tareas explicadas de inicio a cierre: apertura, tipicidad, audiencia, memorial de impulso y seguimiento;
- controles profesionales que permanecen en cabeza de la abogada.

Regla de oro: *la IA propone; la abogada revisa, ajusta y aprueba*.

## Política del repo

No subir presentaciones, PDFs ni Office a GitHub. Compartir por Drive/Slides. CI falla si aparecen en el árbol trackeado.
