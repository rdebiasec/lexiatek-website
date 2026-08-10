#!/usr/bin/env python3
"""Generate LexiaTek onboarding PPTX — despacho virtual (10 agentes)."""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

# —— LexiaTek tokens ——
NAVY = RGBColor(0x0F, 0x17, 0x2A)
NAVY_BRAND = RGBColor(0x1E, 0x3A, 0x8A)
ACCENT = RGBColor(0x25, 0x63, 0xEB)
CYAN = RGBColor(0x06, 0xB6, 0xD4)
MIST = RGBColor(0xE6, 0xEE, 0xF7)
SOFT = RGBColor(0xDC, 0xE7, 0xF2)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SURFACE = RGBColor(0xF4, 0xF8, 0xFC)
BODY = RGBColor(0x47, 0x55, 0x69)
MUTED = RGBColor(0x64, 0x74, 0x8B)
HEADING = RGBColor(0x0F, 0x17, 0x2A)
BORDER = RGBColor(0xD5, 0xE0, 0xEB)

FONT_H = "Calibri"
FONT_B = "Calibri"

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

OUT = Path(__file__).resolve().parent / "LexiaTek_Onboarding_Despacho_Virtual.pptx"

AGENTS = [
    ("Coordinador del Caso", "Voz única del despacho: prioriza, pide faltantes y enruta."),
    ("Cronología y Hechos", "Ordena hechos, fuentes y vacíos del relato."),
    ("Tipicidad y Responsabilidad", "Hipótesis tipica preliminar — no definitiva."),
    ("Ruta Procesal Ley 906", "Etapa y actuaciones posibles para la víctima."),
    ("Representación de Víctimas", "Teoría del caso centrada en la víctima."),
    ("Evidencia y Pruebas", "Inventario de prueba y brechas probatorias."),
    ("Audiencias Penales", "Guion, solicitudes orales y checklist."),
    ("Redacción Documentos", "Memorial, impulso, derecho de petición."),
    ("Seguimiento Procesal", "Radicado, términos, alertas y estado."),
    ("Control de Calidad Jurídica", "Coherencia, riesgos y listo-para-firmar."),
]


def _set_run(run, text, *, size=18, bold=False, color=BODY, font=FONT_B):
    run.text = text
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = font


def add_text(slide, left, top, width, height, text, *, size=18, bold=False, color=BODY, align=PP_ALIGN.LEFT, font=FONT_B, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.word_wrap = True
    try:
        tf.vertical_anchor = anchor
    except Exception:
        pass
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    _set_run(r, text, size=size, bold=bold, color=color, font=font)
    return box


def fill_shape(shape, color: RGBColor):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()


def rounded_rect(slide, left, top, width, height, fill, *, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    fill_shape(shape, fill)
    if line is not None:
        shape.line.color.rgb = line
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    # softer corners
    try:
        adj = shape.adjustments
        adj[0] = 0.12
    except Exception:
        pass
    return shape


def rect(slide, left, top, width, height, fill):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    fill_shape(shape, fill)
    return shape


def set_bg(slide, color: RGBColor):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def eyebrow_bar(slide, text="Onboarding · Abogada"):
    rect(slide, Inches(0), Inches(0), SLIDE_W, Inches(0.08), CYAN)
    add_text(slide, Inches(0.7), Inches(0.25), Inches(6), Inches(0.35), text, size=12, bold=True, color=CYAN, font=FONT_H)


def title_block(slide, title, subtitle=None):
    eyebrow_bar(slide)
    add_text(slide, Inches(0.7), Inches(0.55), Inches(12), Inches(0.6), title, size=28, bold=True, color=HEADING, font=FONT_H)
    if subtitle:
        add_text(slide, Inches(0.7), Inches(1.15), Inches(11.5), Inches(0.45), subtitle, size=15, color=MUTED, font=FONT_B)


def labeled_box(slide, left, top, width, height, title, body, *, fill=WHITE, title_color=NAVY_BRAND, accent=False):
    shape = rounded_rect(slide, left, top, width, height, fill, line=BORDER if not accent else CYAN)
    if accent:
        rect(slide, left, top, Inches(0.12), height, CYAN)
    add_text(slide, left + Inches(0.22), top + Inches(0.15), width - Inches(0.35), Inches(0.35), title, size=14, bold=True, color=title_color, font=FONT_H)
    add_text(slide, left + Inches(0.22), top + Inches(0.5), width - Inches(0.35), height - Inches(0.6), body, size=13, color=BODY, font=FONT_B)
    return shape


def arrow_right(slide, left, top, width=Inches(0.28)):
    s = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, left, top, width, Inches(0.22))
    fill_shape(s, CYAN)
    return s


# ―――――― Slides ――――――


def slide_01_cover(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, NAVY)
    # accent bar
    rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, CYAN)
    # soft brand block
    rounded_rect(slide, Inches(8.2), Inches(1.2), Inches(4.4), Inches(5.1), NAVY_BRAND)
    add_text(slide, Inches(8.5), Inches(2.0), Inches(3.8), Inches(0.4), "10 agentes", size=14, bold=True, color=CYAN, font=FONT_H)
    add_text(slide, Inches(8.5), Inches(2.5), Inches(3.8), Inches(1.5), "Un despacho virtual\npenal-víctimas\ncon una sola voz.", size=22, bold=True, color=WHITE, font=FONT_H)
    add_text(slide, Inches(8.5), Inches(4.4), Inches(3.8), Inches(1.2), "La IA propone.\nUsted revisa, ajusta y firma.", size=14, color=SOFT, font=FONT_B)

    add_text(slide, Inches(0.9), Inches(2.0), Inches(6.5), Inches(0.4), "LexiaTek", size=18, bold=True, color=CYAN, font=FONT_H)
    add_text(slide, Inches(0.9), Inches(2.5), Inches(7), Inches(1.4), "Despacho virtual\npenal-víctimas", size=40, bold=True, color=WHITE, font=FONT_H)
    add_text(slide, Inches(0.9), Inches(4.3), Inches(6.8), Inches(0.8), "Onboarding para la abogada · Colombia · Ley 906", size=16, color=SOFT, font=FONT_B)
    add_text(slide, Inches(0.9), Inches(6.6), Inches(8), Inches(0.35), "Firma1 de Abogados LexiaTek", size=12, color=MUTED, font=FONT_B)


def slide_02_que_es(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Qué es y qué no es", "Regla de oro: la IA propone; usted revisa, ajusta y firma.")

    labeled_box(
        slide, Inches(0.7), Inches(1.9), Inches(5.7), Inches(4.8),
        "Qué agiliza",
        "• Ordenar hechos y cronología\n"
        "• Tipicidad preliminar (hipótesis)\n"
        "• Inventario de prueba y brechas\n"
        "• Ruta procesal Ley 906\n"
        "• Guiones de audiencia\n"
        "• Borradores: memorial, impulso,\n  derecho de petición\n"
        "• Alertas de seguimiento y términos\n\n"
        "Usted conserva criterio, estrategia y firma.",
        fill=WHITE, accent=True,
    )
    labeled_box(
        slide, Inches(6.9), Inches(1.9), Inches(5.7), Inches(4.8),
        "Qué no hace / fuera de alcance",
        "• No reemplaza su criterio ni su firma\n"
        "• No envía nada al cliente o a la\n  autoridad sin su revisión\n"
        "• Tipicidad no es “definitiva”\n"
        "• Tutela / vía constitucional: fuera\n  del producto\n"
        "• No es defensa del investigado\n"
        "• No inventa normas, sentencias\n  ni radicados\n\n"
        "Si el asunto no es penal-víctimas,\n  el sistema deriva; no lo force.",
        fill=WHITE,
    )


def slide_03_analogia(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Un despacho con áreas", "Hable con el Coordinador. Por detrás trabaja el equipo interno; usted ve una sola voz.")

    # Coordinator
    rounded_rect(slide, Inches(4.0), Inches(1.85), Inches(5.3), Inches(0.95), NAVY)
    add_text(slide, Inches(4.1), Inches(1.95), Inches(5.1), Inches(0.35), "Coordinador del Caso", size=16, bold=True, color=WHITE, font=FONT_H, align=PP_ALIGN.CENTER)
    add_text(slide, Inches(4.1), Inches(2.35), Inches(5.1), Inches(0.35), "Voz única · triage · faltantes · enruta", size=12, color=SOFT, font=FONT_B, align=PP_ALIGN.CENTER)

    # connector line visual
    rect(slide, Inches(6.55), Inches(2.8), Inches(0.08), Inches(0.35), CYAN)

    areas = [a[0] for a in AGENTS[1:]]
    # 3 rows of 3
    w, h = Inches(3.7), Inches(0.72)
    start_y = Inches(3.25)
    gap_x, gap_y = Inches(0.25), Inches(0.2)
    start_x = Inches(0.85)
    for i, name in enumerate(areas):
        row, col = divmod(i, 3)
        left = start_x + col * (w + gap_x)
        top = start_y + row * (h + gap_y)
        rounded_rect(slide, left, top, w, h, WHITE, line=BORDER)
        add_text(slide, left + Inches(0.15), top + Inches(0.2), w - Inches(0.3), Inches(0.4), name, size=13, bold=True, color=NAVY_BRAND, font=FONT_H, align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    add_text(slide, Inches(0.7), Inches(6.7), Inches(12), Inches(0.35), "Analogía: como un despacho real — recepción/coordinación arriba; áreas especializadas abajo.", size=12, color=MUTED)


def slide_04_flujo(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Cómo fluye un pedido", "De su consulta al borrador listo para su revisión.")

    steps = [
        ("1. Consulta", "Usted pide\nen lenguaje\nnatural"),
        ("2. Coordinador", "Prioriza,\ncompleta\nfaltantes"),
        ("3. Área", "Especialista\ninterno\ntrabaja"),
        ("4. Borrador", "Respuesta\ncon una\nsola voz"),
        ("5. Usted", "Revisa,\naprueba\ny firma"),
    ]
    box_w = Inches(2.0)
    box_h = Inches(2.4)
    y = Inches(2.4)
    gap = Inches(0.35)
    start = Inches(0.55)
    for i, (title, body) in enumerate(steps):
        left = start + i * (box_w + gap)
        fill = NAVY if i == 4 else WHITE
        title_c = WHITE if i == 4 else NAVY_BRAND
        body_c = SOFT if i == 4 else BODY
        rounded_rect(slide, left, y, box_w, box_h, fill, line=CYAN if i == 4 else BORDER)
        add_text(slide, left + Inches(0.12), y + Inches(0.25), box_w - Inches(0.24), Inches(0.5), title, size=14, bold=True, color=title_c, font=FONT_H, align=PP_ALIGN.CENTER)
        add_text(slide, left + Inches(0.12), y + Inches(0.9), box_w - Inches(0.24), Inches(1.3), body, size=13, color=body_c, font=FONT_B, align=PP_ALIGN.CENTER)
        if i < len(steps) - 1:
            arrow_right(slide, left + box_w + Inches(0.05), y + Inches(1.05), Inches(0.25))

    add_text(
        slide, Inches(0.7), Inches(5.3), Inches(12), Inches(1.2),
        "Si el pedido es una pieza escrita (memorial, impulso, derecho de petición): primero se aprueba el plan de redacción, "
        "luego usted revisa el borrador en bandeja y firma antes de radicar o enviar.",
        size=14, color=BODY,
    )


def slide_05_mapa(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Mapa de los 10 agentes", "Nombres de despacho — sin IDs técnicos.")

    # Center coordinator
    cx, cy = Inches(5.4), Inches(3.55)
    rounded_rect(slide, cx, cy, Inches(2.5), Inches(1.1), NAVY)
    add_text(slide, cx + Inches(0.1), cy + Inches(0.25), Inches(2.3), Inches(0.6), "Coordinador\ndel Caso", size=14, bold=True, color=WHITE, font=FONT_H, align=PP_ALIGN.CENTER)

    # Surrounding 9 in a ring-ish grid: top 3, mid 2 sides, bottom 4
    others = AGENTS[1:]
    positions = [
        (Inches(0.6), Inches(1.85)),
        (Inches(3.5), Inches(1.85)),
        (Inches(7.3), Inches(1.85)),
        (Inches(10.2), Inches(1.85)),
        (Inches(0.6), Inches(3.7)),
        (Inches(10.2), Inches(3.7)),
        (Inches(1.5), Inches(5.55)),
        (Inches(5.0), Inches(5.55)),
        (Inches(8.5), Inches(5.55)),
    ]
    bw, bh = Inches(2.5), Inches(0.85)
    for (name, _), (left, top) in zip(others, positions):
        rounded_rect(slide, left, top, bw, bh, WHITE, line=BORDER)
        add_text(slide, left + Inches(0.1), top + Inches(0.25), bw - Inches(0.2), Inches(0.45), name, size=12, bold=True, color=NAVY_BRAND, font=FONT_H, align=PP_ALIGN.CENTER)


def slide_06_analisis(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Áreas de análisis", "Cómo pedirlas al Coordinador — lenguaje natural.")

    items = [
        ("Cronología y Hechos", "“Ordene la cronología con fuentes y vacíos.”"),
        ("Tipicidad y Responsabilidad", "“Hipótesis tipica preliminar, no definitiva.”"),
        ("Ruta Procesal Ley 906", "“Etapa y actuaciones posibles para la víctima.”"),
        ("Representación de Víctimas", "“Teoría del caso centrada en la víctima, sin revictimizar.”"),
        ("Evidencia y Pruebas", "“Inventario de prueba y brechas.”"),
    ]
    for i, (title, ask) in enumerate(items):
        row, col = divmod(i, 3) if i < 3 else (1, i - 3)
        if i < 3:
            left = Inches(0.7) + col * Inches(4.1)
            top = Inches(1.9)
            w = Inches(3.9)
        else:
            left = Inches(0.7) + (i - 3) * Inches(6.15)
            top = Inches(4.35)
            w = Inches(5.95)
        labeled_box(slide, left, top, w, Inches(2.1), title, f"Pida así:\n{ask}", fill=WHITE)


def slide_07_actuacion(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Áreas de actuación y control", "Piezas, audiencias, seguimiento y calidad — siempre bajo su firma.")

    items = [
        ("Audiencias Penales", "“Guion, solicitudes y checklist para la audiencia.”"),
        ("Redacción Documentos", "“Borrador de memorial / impulso / derecho de petición.”\n→ Apruebe el plan → revise → firme."),
        ("Seguimiento Procesal", "“Estado del radicado, alertas y resumen para cliente (borrador).”"),
        ("Control de Calidad Jurídica", "“Revise coherencia, riesgos y tono antes de firmar.”"),
        ("Coordinador del Caso", "“Clasifique urgencia, complete faltantes, siguiente paso del despacho.”"),
    ]
    for i, (title, ask) in enumerate(items):
        if i < 3:
            left = Inches(0.7) + i * Inches(4.1)
            top = Inches(1.9)
            w = Inches(3.9)
        else:
            left = Inches(0.7) + (i - 3) * Inches(6.15)
            top = Inches(4.35)
            w = Inches(5.95)
        accent = title.startswith("Redacción")
        labeled_box(slide, left, top, w, Inches(2.1), title, f"Pida así:\n{ask}", fill=WHITE, accent=accent)


def slide_08_dia_tipico(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Día típico del expediente", "Flujo habitual de una mañana de trabajo.")

    steps = [
        ("01", "Apertura / hechos", "Cronología + vacíos"),
        ("02", "Tipicidad preliminar", "Hipótesis + brechas de prueba"),
        ("03", "Ruta Ley 906", "Etapa + objetivo de víctima"),
        ("04", "Si hay audiencia", "Guion + checklist"),
        ("05", "Si hay pieza escrita", "Plan → borrador → firma"),
        ("06", "Seguimiento", "Alertas y reporte interno"),
    ]
    # vertical timeline
    line_x = Inches(1.15)
    rect(slide, line_x, Inches(1.95), Inches(0.06), Inches(4.9), CYAN)
    for i, (num, title, body) in enumerate(steps):
        top = Inches(1.85) + i * Inches(0.85)
        # dot
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(1.0), top + Inches(0.15), Inches(0.35), Inches(0.35))
        fill_shape(dot, NAVY if i == 4 else CYAN)
        add_text(slide, Inches(1.6), top + Inches(0.05), Inches(1.0), Inches(0.4), num, size=16, bold=True, color=NAVY_BRAND, font=FONT_H)
        add_text(slide, Inches(2.7), top + Inches(0.05), Inches(4.5), Inches(0.35), title, size=16, bold=True, color=HEADING, font=FONT_H)
        add_text(slide, Inches(7.4), top + Inches(0.05), Inches(5.2), Inches(0.55), body, size=15, color=BODY, font=FONT_B)


def slide_09_controles(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Controles que usted conserva", "El despacho virtual acelera; la responsabilidad profesional es suya.")

    controls = [
        ("Estrategia", "Decide el rumbo del caso y las pretensiones."),
        ("Salida externa", "Nada sale al cliente o a la autoridad sin su revisión."),
        ("Radicados y fuentes", "Valida números, documentos y citas antes de usarlos."),
        ("Tono y pretensiones", "Ajusta el lenguaje al rol de víctima y al foro."),
        ("Firma y radicación", "Solo usted firma y decide cuándo radicar."),
        ("Plan de redacción", "Si hay pieza escrita: apruebe el plan, revise el borrador, firme."),
    ]
    for i, (t, b) in enumerate(controls):
        row, col = divmod(i, 3)
        left = Inches(0.7) + col * Inches(4.1)
        top = Inches(1.9) + row * Inches(2.35)
        labeled_box(slide, left, top, Inches(3.9), Inches(2.15), t, b, fill=WHITE, accent=(i == 5))


def slide_10_leer(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Cómo leer una respuesta", "Señales rápidas en el chat del despacho.")

    rows = [
        ("Eco + respuesta corta", "El Coordinador entendió el pedido."),
        ("“Equipo interno” / “área de…”", "Consultó especialistas (no verá IDs técnicos)."),
        ("Pendientes / vacíos", "Falta dato; complete antes de radicar."),
        ("Pedido de aprobar plan", "Hay redacción accionable en cola de revisión."),
        ("[PENDIENTE DE VERIFICAR]", "Separe hecho confirmado / narrado / inferido."),
    ]
    # header
    rounded_rect(slide, Inches(0.7), Inches(1.85), Inches(12), Inches(0.55), NAVY)
    add_text(slide, Inches(0.95), Inches(1.95), Inches(4.5), Inches(0.35), "Señal", size=14, bold=True, color=WHITE, font=FONT_H)
    add_text(slide, Inches(5.6), Inches(1.95), Inches(6.8), Inches(0.35), "Significa", size=14, bold=True, color=WHITE, font=FONT_H)

    for i, (sig, mean) in enumerate(rows):
        top = Inches(2.5) + i * Inches(0.75)
        bg = WHITE if i % 2 == 0 else SURFACE
        rounded_rect(slide, Inches(0.7), top, Inches(12), Inches(0.68), bg, line=BORDER)
        add_text(slide, Inches(0.95), top + Inches(0.18), Inches(4.5), Inches(0.4), sig, size=14, bold=True, color=NAVY_BRAND, font=FONT_H)
        add_text(slide, Inches(5.6), top + Inches(0.18), Inches(6.8), Inches(0.4), mean, size=14, color=BODY, font=FONT_B)


def slide_11_ejemplos(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, MIST)
    title_block(slide, "Ejemplos de pedidos", "Hable en español natural. No necesita invocar skills ni IDs.")

    prompts = [
        "Ordene los hechos de este caso con fecha, fuente y vacíos.",
        "Haga tipicidad preliminar de VIF; marque lo que falta probar.",
        "¿En qué etapa de la Ley 906 estamos y qué puede pedir la víctima?",
        "Prepare un guion y checklist para la próxima audiencia.",
        "Borrador de derecho de petición al fiscal — con plan para aprobar.",
        "Resuma el estado del radicado y alertas de términos (borrador interno).",
    ]
    for i, text in enumerate(prompts):
        row, col = divmod(i, 2)
        left = Inches(0.7) + col * Inches(6.2)
        top = Inches(1.85) + row * Inches(1.55)
        rounded_rect(slide, left, top, Inches(5.95), Inches(1.4), WHITE, line=BORDER)
        rect(slide, left, top, Inches(0.12), Inches(1.4), CYAN)
        add_text(slide, left + Inches(0.35), top + Inches(0.25), Inches(5.4), Inches(0.3), f"Pedido {i + 1}", size=11, bold=True, color=CYAN, font=FONT_H)
        add_text(slide, left + Inches(0.35), top + Inches(0.55), Inches(5.4), Inches(0.7), f"“{text}”", size=14, color=HEADING, font=FONT_B)


def slide_12_cierre(prs):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, NAVY)
    rect(slide, Inches(0), Inches(0), Inches(0.18), SLIDE_H, CYAN)

    add_text(slide, Inches(0.9), Inches(1.3), Inches(11), Inches(0.4), "LexiaTek · Onboarding", size=14, bold=True, color=CYAN, font=FONT_H)
    add_text(slide, Inches(0.9), Inches(1.8), Inches(11), Inches(0.8), "Tres reglas para empezar", size=32, bold=True, color=WHITE, font=FONT_H)

    rules = [
        ("1", "Hable con el Coordinador", "Una sola voz de despacho; el equipo interno trabaja por detrás."),
        ("2", "La IA propone; usted firma", "Revise hechos, citas y pretensiones antes de cualquier salida."),
        ("3", "Pieza escrita = plan + firma", "Apruebe el plan, revise el borrador, firme antes de radicar."),
    ]
    for i, (n, t, b) in enumerate(rules):
        top = Inches(2.9) + i * Inches(1.05)
        rounded_rect(slide, Inches(0.9), top, Inches(11.5), Inches(0.9), NAVY_BRAND)
        add_text(slide, Inches(1.15), top + Inches(0.25), Inches(0.5), Inches(0.4), n, size=22, bold=True, color=CYAN, font=FONT_H)
        add_text(slide, Inches(1.8), top + Inches(0.15), Inches(10), Inches(0.3), t, size=16, bold=True, color=WHITE, font=FONT_H)
        add_text(slide, Inches(1.8), top + Inches(0.48), Inches(10), Inches(0.3), b, size=13, color=SOFT, font=FONT_B)

    add_text(slide, Inches(0.9), Inches(6.5), Inches(11), Inches(0.4), "Referencia interna: guía de 1 página para el abogado · Pack de uso diario", size=12, color=MUTED, font=FONT_B)


def build():
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H

    slide_01_cover(prs)
    slide_02_que_es(prs)
    slide_03_analogia(prs)
    slide_04_flujo(prs)
    slide_05_mapa(prs)
    slide_06_analisis(prs)
    slide_07_actuacion(prs)
    slide_08_dia_tipico(prs)
    slide_09_controles(prs)
    slide_10_leer(prs)
    slide_11_ejemplos(prs)
    slide_12_cierre(prs)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(OUT))
    print(f"Wrote {OUT}")
    return OUT


if __name__ == "__main__":
    build()
