#!/usr/bin/env python3
"""Ayuda oral — propuesta de asociación LexiaTek.

Plantilla visual: LexiaTek_Alexia_Letigia_Abogados_v1
  navy / teal / oro · Arial · 16:9 · notas de orador · sin stretch.

El documento que se entrega es el Word. Este deck no se deja como hoja de términos.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

HERE = Path(__file__).resolve().parent
OUT_DECK = HERE / "LexiaTek_Plan_Negocios_Abogada.pptx"

TEMPLATE = Path("/Users/ricardodebiase/Documents/agente de IA juridico")
COMBO = TEMPLATE / "docs/assets/alexia-letigia-combo.png"
DBX_LOGO = TEMPLATE / "docs/assets/dbx-logo.png"

FONT = "Arial"
NAVY = "0A1F3D"
NAVY_MID = "0B2545"
TEAL = "0E7C7B"
TEAL_SOFT = "7EC8C8"
TEAL_PALE = "E8F6F5"
GOLD = "C4A35A"
WHITE = "FFFFFF"
LIGHT = "F4F7FA"
INK = "0A1F3D"
MUTED = "5B6B7C"
LINE = "D5DEE8"
SLATE = "8BA3B8"
TOTAL = 11


def rgb(h: str) -> RGBColor:
    return RGBColor(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def set_run(run, size=18, bold=False, color=INK, italic=False):
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = rgb(color)
    run.font.name = FONT


def add_text(slide, x, y, w, h, value, size=18, bold=False, color=INK,
             align=PP_ALIGN.LEFT, italic=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = value
    set_run(run, size=size, bold=bold, color=color, italic=italic)
    return box


def add_paras(slide, x, y, w, h, lines, size=15, color=INK, gap_pt=6, bold=False):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(gap_pt)
        run = p.add_run()
        run.text = line
        set_run(run, size=size, color=color, bold=bold)
    return box


def add_rect(slide, x, y, w, h, fill, line=None, radius=False):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    if radius:
        try:
            shape.adjustments[0] = 0.08
        except Exception:
            pass
    return shape


def notes(slide, bullets: list[str]):
    ns = slide.notes_slide
    tf = ns.notes_text_frame
    tf.clear()
    for i, b in enumerate(bullets):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = f"• {b}"


def blank(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def footer_light(slide, page):
    add_text(slide, 0.5, 7.15, 10.2, 0.25,
             "LexiaTek  ·  ayuda oral  ·  propuesta de asociación", size=10, color=MUTED)
    add_text(slide, 11.5, 7.15, 1.4, 0.25, f"{page}/{TOTAL}",
             size=10, color=MUTED, align=PP_ALIGN.RIGHT)


def footer_dark(slide, page):
    add_text(slide, 0.5, 7.15, 10.2, 0.25,
             "LexiaTek  ·  ayuda oral  ·  propuesta de asociación", size=10, color=SLATE)
    add_text(slide, 11.5, 7.15, 1.4, 0.25, f"{page}/{TOTAL}",
             size=10, color=SLATE, align=PP_ALIGN.RIGHT)


def eyebrow_title(slide, kicker, title, subtitle=None):
    add_text(slide, 0.5, 0.22, 12.3, 0.28, kicker, size=12, bold=True, color=TEAL)
    add_text(slide, 0.5, 0.5, 12.3, 0.48, title, size=24, bold=True, color=NAVY)
    if subtitle:
        add_text(slide, 0.5, 1.02, 12.3, 0.32, subtitle, size=13, color=MUTED)


def add_pic(slide, path: Path, x, y, w=None, h=None):
    if not path.exists():
        return None
    kwargs = {}
    if w is not None:
        kwargs["width"] = Inches(w)
    if h is not None:
        kwargs["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kwargs)


def new_prs():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    return prs


def cover(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, NAVY)
    add_rect(s, 0, 0, 13.333, 0.08, GOLD)
    add_text(s, 0.6, 0.4, 7.2, 0.28, "PROPUESTA DE ASOCIACIÓN", size=12, bold=True, color=GOLD)
    add_text(s, 0.6, 0.85, 7.3, 1.7, "LexiaTek", size=40, bold=True, color=WHITE)
    add_text(
        s, 0.6, 2.55, 7.2, 1.1,
        "Constitución y operación de un despacho\nde orientación y representación jurídica.",
        size=18, color=TEAL_SOFT,
    )
    add_rect(s, 0.6, 3.9, 7.2, 1.85, NAVY_MID, radius=True)
    add_paras(
        s, 0.85, 4.1, 6.7, 1.55,
        [
            "Socios: Michele Aguilar y Ricardo De Biase, 50 % cada uno.",
            "Abogada titular: Michele Aguilar. Socio técnico: Ricardo De Biase.",
            "Licencias recíprocas, vigentes solo mientras dure la asociación.",
        ],
        size=13, color=TEAL_SOFT, gap_pt=8,
    )
    add_pic(s, COMBO, 8.05, 1.05, h=5.15)
    add_pic(s, DBX_LOGO, 0.6, 5.95, w=1.15)
    add_text(s, 1.95, 6.15, 5.8, 0.28, "Ayuda oral  ·  el documento es el Word", size=12, color=GOLD)
    add_text(s, 0.6, 6.65, 7.2, 0.3, "Confidencial  ·  Colombia  ·  agosto de 2026", size=12, color=SLATE)
    notes(s, [
        "El Word es el documento. Este deck solo acompaña la exposición.",
        "Nombre a nombre: Michele Aguilar, abogada titular; Ricardo De Biase, socio técnico.",
        "No mencione a Michele Aguilar en relación con DBX. La tecnología se licencia al despacho.",
        "No use jerga. Registro formal, usted.",
    ])
    footer_dark(s, 1)


def slide_problema(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Punto de partida",
        "Tres tensiones que el despacho debe resolver",
        "No se limitan al derecho penal.",
    )
    pains = [
        ("Tiempo", "Redactar desde cero, vigilar términos y ordenar el expediente consume las horas que deberían destinarse al criterio y al cliente.", GOLD),
        ("Acceso", "Quien más necesita orientación —penal, laboral, de tutela o de una simple reclamación— a menudo no puede sufragar el modelo tradicional de honorarios.", TEAL),
        ("Rigor", "Atender más asuntos sin método pone en riesgo la calidad del trabajo, la tarjeta profesional y la reputación del despacho.", NAVY),
    ]
    for i, (title, body, accent) in enumerate(pains):
        x = 0.5 + i * 4.2
        add_rect(s, x, 1.7, 4.0, 4.35, WHITE, LINE, radius=True)
        add_rect(s, x, 1.7, 4.0, 0.1, accent)
        add_text(s, x + 0.25, 2.05, 3.5, 0.4, title, size=20, bold=True, color=NAVY)
        add_text(s, x + 0.25, 2.6, 3.5, 2.9, body, size=15, color=MUTED)
    add_rect(s, 0.5, 6.2, 12.35, 0.7, NAVY, radius=True)
    add_text(
        s, 0.75, 6.38, 11.9, 0.38,
        "Un despacho que atienda a más personas, sin relajar el criterio ni prometer resultados.",
        size=14, bold=True, color=TEAL_SOFT, align=PP_ALIGN.CENTER,
    )
    notes(s, [
        "Empiece por el problema profesional, no por la tecnología.",
        "Tres tensiones: tiempo, acceso y rigor. El alcance no es solo penal.",
        "No nombre todavía las licencias ni DBX.",
    ])
    footer_light(s, 2)


def slide_lexiatek(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "LexiaTek",
        "Dos socios. Funciones distintas.",
        "La participación es igual. El trabajo no lo es.",
    )
    add_rect(s, 0.5, 1.65, 6.0, 4.85, WHITE, LINE, radius=True)
    add_text(s, 0.8, 1.9, 5.4, 0.35, "MICHELE AGUILAR", size=14, bold=True, color=GOLD)
    add_text(s, 0.8, 2.25, 5.4, 0.3, "Socia 50 %  ·  abogada titular", size=13, italic=True, color=TEAL)
    add_paras(
        s, 0.8, 2.75, 5.4, 3.4,
        [
            "Usa las herramientas. Confirma, ajusta y aprueba.",
            "Firma, radica, acepta o rechaza asuntos.",
            "Veta ética, conflictos y textos públicos.",
            "El cliente recibe el servicio jurídico de usted.",
            "El expediente es su responsabilidad profesional.",
        ],
        size=15, color=MUTED, gap_pt=8,
    )
    add_rect(s, 6.8, 1.65, 6.05, 4.85, NAVY, radius=True)
    add_text(s, 7.1, 1.9, 5.45, 0.35, "RICARDO DE BIASE", size=14, bold=True, color=TEAL_SOFT)
    add_text(s, 7.1, 2.25, 5.45, 0.3, "Socio 50 %  ·  responsable técnico", size=13, italic=True, color=GOLD)
    add_paras(
        s, 7.1, 2.75, 5.45, 3.4,
        [
            "Construye y opera según las prioridades que usted fije.",
            "No orienta, no firma, no litiga.",
            "No se anuncia como abogado.",
            "El 50 % es de la utilidad de LexiaTek,",
            "no de un honorario profesional.",
        ],
        size=15, color="B8C9D9", gap_pt=8,
    )
    notes(s, [
        "Propiedad igual. Trabajo distinto. Diga los dos nombres.",
        "Usted no ejerce el derecho. Ella no construye la tecnología.",
        "El 50 % no vota un escrito.",
    ])
    footer_light(s, 3)


def slide_licencias(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Licencias recíprocas",
        "Dos autorizaciones. La misma condición temporal.",
        "Nacen con la asociación y se extinguen con ella.",
    )
    add_rect(s, 0.5, 1.65, 6.0, 4.4, NAVY, radius=True)
    add_text(s, 0.8, 1.9, 5.4, 0.55, "TECNOLOGÍA", size=13, bold=True, color=TEAL_SOFT)
    add_paras(
        s, 0.8, 2.5, 5.4, 3.2,
        [
            "La IP y la arquitectura de la IA pertenecen",
            "de manera exclusiva a DBX Solutions.",
            "Se licencian a Michele Aguilar y, a través",
            "de ella, a LexiaTek, solo mientras subsista",
            "la asociación. No hay cesión ni copropiedad.",
        ],
        size=15, color="B8C9D9", gap_pt=8,
    )
    add_rect(s, 6.8, 1.65, 6.05, 4.4, WHITE, LINE, radius=True)
    add_text(s, 7.1, 1.9, 5.45, 0.55, "SERVICIOS PROFESIONALES", size=13, bold=True, color=GOLD)
    add_paras(
        s, 7.1, 2.5, 5.45, 3.2,
        [
            "Michele Aguilar autoriza a LexiaTek a contar",
            "con sus servicios como abogada titular",
            "solo mientras subsista la asociación.",
            "Al terminar, esa autorización cesa, con el",
            "periodo transitorio que usted confirme.",
        ],
        size=15, color=MUTED, gap_pt=8,
    )
    add_rect(s, 0.5, 6.2, 12.35, 0.7, NAVY, radius=True)
    add_text(
        s, 0.75, 6.38, 11.9, 0.38,
        "Ser socia de LexiaTek no la hace titular de la IA. Ser titular de DBX no autoriza a ejercer el derecho.",
        size=14, bold=True, color=GOLD, align=PP_ALIGN.CENTER,
    )
    notes(s, [
        "Esta es la lámina central. Léala despacio.",
        "Simetría: DBX licencia la IA al despacho; ella autoriza sus servicios al despacho.",
        "Ninguna licencia sobrevive a la asociación, salvo el periodo transitorio que ella confirme por ética (no abandono de clientes).",
        "No mencione ningún vínculo profesional de ella con DBX.",
    ])
    footer_light(s, 4)


def slide_alcance(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Alcance del despacho",
        "Procesos frecuentes de la ciudadanía",
        "Usted acepta o rechaza cada asunto.",
    )
    areas = [
        ("Penal", "Orientación y representación en asuntos penales, en el alcance que usted acepte."),
        ("Civil", "Controversias y trámites civiles habituales de personas."),
        ("Laboral", "Reclamaciones y orientación en materia de trabajo."),
        ("Acoso sexual", "Acompañamiento con el rigor y la reserva que el asunto exige."),
        ("PQRS", "Peticiones, quejas, reclamos y sugerencias ante entidades."),
        ("Tutelas y trámites", "Acciones de tutela, derechos de petición e impulsos análogos."),
    ]
    for i, (title, body) in enumerate(areas):
        r, c = divmod(i, 3)
        x = 0.5 + c * 4.2
        y = 1.65 + r * 2.4
        add_rect(s, x, y, 4.0, 2.2, WHITE, LINE, radius=True)
        add_text(s, x + 0.22, y + 0.2, 3.55, 0.4, title, size=16, bold=True, color=TEAL)
        add_text(s, x + 0.22, y + 0.7, 3.55, 1.25, body, size=13, color=MUTED)
    notes(s, [
        "No es un despacho solo penal. Enumere las áreas sin convertirlas en promesa de resultado.",
        "Ella decide el alcance de cada caso.",
        "El sitio público actual sigue siendo penal; no se cambia hoy. Ella lo auditará.",
    ])
    footer_light(s, 5)


def slide_proposito(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(s, "Propósito", "Qué se le propone, y qué no")
    rows = [
        ("Titularidad del despacho", "LexiaTek es de ambos. No se le ofrece un empleo: se le propone ser la abogada titular y socia."),
        ("Criterio, no automatismo", "Las herramientas preparan insumos. Usted revisa, ajusta y, si corresponde, firma."),
        ("Tecnología licenciada", "La IA permanece en DBX Solutions. El despacho la usa mientras dure la asociación."),
        ("Servicios autorizados", "Sus servicios profesionales se prestan a LexiaTek mientras dure la asociación."),
        ("Sin dilución", "Quien entre después —abogado o ingeniero— será empleado o contratista. El 50 % no se parte."),
        ("Tarifas después", "El catálogo al público se elabora de común acuerdo. Usted veta el cobro éticamente inadmisible."),
    ]
    for i, (title, body) in enumerate(rows):
        r, c = divmod(i, 3)
        x = 0.5 + c * 4.2
        y = 1.55 + r * 2.55
        add_rect(s, x, y, 4.0, 2.35, WHITE, LINE, radius=True)
        add_text(s, x + 0.22, y + 0.2, 3.55, 0.45, title, size=14, bold=True, color=TEAL)
        add_text(s, x + 0.22, y + 0.75, 3.55, 1.4, body, size=13, color=MUTED)
    notes(s, [
        "Léalo con calma. Titularidad, no empleo.",
        "Repita la simetría de las licencias sin nombrar a DBX como su empleador.",
        "Las tarifas no se cierran en esta reunión.",
    ])
    footer_light(s, 6)


def slide_existe(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(s, "Estado actual", "Lo construido y lo que falta formalizar")
    blocks = [
        (TEAL, "YA OPERA", [
            "Sitio lexiatek.com",
            "Páginas de privacidad y datos",
            "Recepción de asuntos",
            "Herramientas internas de apoyo",
            "Usted audita el texto y el alcance",
        ]),
        (NAVY, "TITULARIDAD TÉCNICA", [
            "IP y arquitectura: DBX Solutions",
            "Licencia al despacho, no cesión",
            "La IA propone; usted aprueba",
            "Nada firma ni radica",
            "Expedientes: nunca entrenamiento",
        ]),
        (GOLD, "POR FORMALIZAR", [
            "Pacto de socios de LexiaTek",
            "Licencia de la IA al despacho",
            "Autorización de sus servicios",
            "Constitución, RUT y cuenta",
            "Nombre legal que usted confirme",
        ]),
    ]
    for i, (accent, title, lines) in enumerate(blocks):
        x = 0.5 + i * 4.2
        add_rect(s, x, 1.65, 4.0, 4.85, WHITE, LINE, radius=True)
        add_rect(s, x, 1.65, 4.0, 0.55, accent)
        add_text(s, x + 0.15, 1.77, 3.7, 0.32, title, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_paras(s, x + 0.3, 2.45, 3.45, 3.7, lines, size=14, color=MUTED, gap_pt=10)
    notes(s, [
        "Distinga lo que ya existe de lo que falta por escrito.",
        "Sin ella, el sitio promete un abogado que no está formalizado.",
        "No hay periodo de prueba. El pedido es formalizar.",
    ])
    footer_light(s, 7)


def slide_operacion(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Operación diaria",
        "La herramienta prepara. Usted decide.",
    )
    moments = [
        ("1", "Recepción", "El asunto entra al despacho. Se ordena el expediente y se identifican términos.", False),
        ("2", "Preparación", "Las herramientas producen cronología, hipótesis preliminar y borrador interno.", False),
        ("3", "Decisión", "Usted revisa, corrige o descarta. Si corresponde, firma y radica.", True),
        ("4", "Cliente", "La orientación y la representación son humanas. La herramienta no se dirige al público como abogado.", False),
    ]
    for i, (num, when, body, gate) in enumerate(moments):
        x = 0.5 + i * 3.2
        fill = TEAL if gate else WHITE
        border = None if gate else LINE
        add_rect(s, x, 1.7, 3.0, 4.35, fill, line=border, radius=True)
        add_text(s, x + 0.2, 1.9, 2.6, 0.25, num, size=11, bold=True, color=GOLD if gate else TEAL)
        add_text(s, x + 0.2, 2.25, 2.6, 0.4, when, size=18, bold=True, color=WHITE if gate else NAVY)
        add_text(s, x + 0.2, 2.85, 2.6, 2.4, body, size=14, color=TEAL_PALE if gate else MUTED)
        if gate:
            add_text(s, x + 0.2, 5.45, 2.6, 0.3, "USTED APRUEBA", size=11, bold=True, color=GOLD, align=PP_ALIGN.CENTER)
    add_rect(s, 0.5, 6.2, 12.35, 0.7, NAVY, radius=True)
    add_text(
        s, 0.75, 6.38, 11.9, 0.38,
        "Si usted no puede atender un asunto, la suplencia solo recae en otro abogado del despacho.",
        size=14, bold=True, color=TEAL_SOFT, align=PP_ALIGN.CENTER,
    )
    notes(s, [
        "El tercer recuadro es el control: ella aprueba.",
        "Ni usted ni el sistema ocupan la función de abogado.",
        "Registro formal. Sin jerga técnica ni tono de venta.",
    ])
    footer_light(s, 8)


def slide_cascada(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Régimen económico de LexiaTek",
        "Del ingreso se cubre la operación. Luego se reparte. DBX no se reparte.",
    )
    bands = [
        (NAVY, TEAL_SOFT, "1  INGRESO",
         "El cliente paga a LexiaTek el servicio contratado. El catálogo y las tarifas se definirán después, de común acuerdo. Usted veta el cobro que no resulte éticamente defendible."),
        (TEAL, WHITE, "2  OPERACIÓN",
         "Con cargo a ese ingreso se cubren inteligencia artificial, hospedaje, sitio, herramientas y, cuando existan, remuneraciones. DBX Solutions factura tecnología como costo, no como mitad de un honorario."),
        (NAVY_MID, TEAL_PALE, "3  UTILIDAD",
         "El remanente se distribuye por partes iguales entre Michele Aguilar y Ricardo De Biase. Sin utilidad, no hay reparto. Los gastos de DBX Solutions los decide su único socio."),
    ]
    for i, (fill, color, title, body) in enumerate(bands):
        y = 1.6 + i * 1.55
        add_rect(s, 0.5, y, 12.35, 1.4, fill, radius=True)
        add_text(s, 0.8, y + 0.18, 11.8, 0.32, title, size=14, bold=True, color=GOLD)
        add_text(s, 0.8, y + 0.58, 11.8, 0.65, body, size=14, color=color)
    add_text(
        s, 0.5, 6.35, 12.35, 0.5,
        "No se parte un honorario de abogado. No se coparticipa la inteligencia artificial.",
        size=13, bold=True, color=NAVY, align=PP_ALIGN.CENTER,
    )
    notes(s, [
        "Tres bandas, en ese orden. No invierta operación y utilidad.",
        "DBX se paga como costo tecnológico, no como participación profesional.",
        "Las tarifas son otro trabajo, con su veto ético.",
    ])
    footer_light(s, 9)


def slide_ruta(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, LIGHT)
    eyebrow_title(
        s, "Hoja de ruta en Colombia",
        "Contratos, luego constitución, luego cumplimiento, luego clientes.",
        "Usted confirma cada paso jurídico. Esto no es un dictamen.",
    )
    steps = [
        ("A", "Borrador", "Usted corrige el Word con control de cambios hasta que el lenguaje le represente."),
        ("B", "Contratos", "Pacto de socios. Licencia de la IA. Autorización de sus servicios profesionales."),
        ("C", "Constitución", "Nombre, estatutos, Cámara, RUT, cuenta de LexiaTek y, si falta, DBX Solutions."),
        ("D", "Cumplimiento", "Tarjeta, seguro, datos personales, auditoría del sitio y de la publicidad."),
        ("E", "Operación", "Catálogo de tarifas, canales que usted autorice y atención a nombre del despacho."),
    ]
    for i, (letter, title, body) in enumerate(steps):
        y = 1.55 + i * 1.0
        add_rect(s, 0.5, y, 12.35, 0.9, WHITE, LINE, radius=True)
        add_rect(s, 0.5, y, 0.7, 0.9, TEAL if i == 1 else NAVY)
        add_text(s, 0.5, y + 0.28, 0.7, 0.35, letter, size=16, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
        add_text(s, 1.4, y + 0.12, 3.2, 0.3, title, size=15, bold=True, color=NAVY)
        add_text(s, 4.6, y + 0.18, 7.9, 0.55, body, size=13, color=MUTED)
    notes(s, [
        "El orden importa: no se constituye antes de alinear los contratos; no se capta clientela antes del cumplimiento.",
        "Los tres contratos: pacto de socios; licencia DBX → LexiaTek; autorización de servicios de Michele Aguilar → LexiaTek.",
        "No atribuya a Michele Aguilar función alguna en DBX Solutions.",
        "Ella confirma la ética del periodo transitorio al cesar la asociación.",
    ])
    footer_light(s, 10)


def slide_cierre(prs):
    s = blank(prs)
    add_rect(s, 0, 0, 13.333, 7.5, NAVY)
    add_rect(s, 0, 0, 13.333, 0.08, GOLD)
    add_text(s, 0.6, 0.4, 7.2, 0.28, "SOLICITUD", size=12, bold=True, color=GOLD)
    add_text(s, 0.6, 0.85, 7.3, 1.35, "Formalizar LexiaTek\ncomo despacho de ambos.", size=26, bold=True, color=WHITE)
    add_paras(
        s, 0.6, 2.5, 7.2, 2.6,
        [
            "1. Pacto de socios: Michele Aguilar y Ricardo De Biase, 50 % cada uno.",
            "2. Licencia de la IA: DBX Solutions al despacho, mientras dure la asociación.",
            "3. Autorización de sus servicios profesionales a LexiaTek, en la misma condición.",
        ],
        size=15, color=TEAL_SOFT, gap_pt=10,
    )
    add_text(
        s, 0.6, 5.35, 7.2, 0.85,
        "Luego: constitución, cumplimiento y, solo entonces, clientes.",
        size=14, color=GOLD,
    )
    add_pic(s, COMBO, 8.05, 1.1, h=5.1)
    add_text(
        s, 0.6, 6.4, 12, 0.35,
        "El documento para anotar es el Word. Este deck no se deja como contrato.",
        size=13, color=SLATE,
    )
    notes(s, [
        "Cierre con la solicitud, no con una consigna.",
        "Tres instrumentos. Luego constitución. Luego cumplimiento. Luego clientes.",
        "Entréguele el Word y pídale control de cambios. Calle y deje que anote.",
    ])
    footer_dark(s, 11)


def build_deck():
    prs = new_prs()
    cover(prs)
    slide_problema(prs)
    slide_lexiatek(prs)
    slide_licencias(prs)
    slide_alcance(prs)
    slide_proposito(prs)
    slide_existe(prs)
    slide_operacion(prs)
    slide_cascada(prs)
    slide_ruta(prs)
    slide_cierre(prs)
    prs.save(OUT_DECK)
    print(f"Wrote {OUT_DECK} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    build_deck()
