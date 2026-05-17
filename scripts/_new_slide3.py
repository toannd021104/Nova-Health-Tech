
# =============================================================================
# SLIDE 3: Multi-Agent Architecture (12 departments in PoC)
# =============================================================================
slide = new_slide(prs)
slide_title(slide, 'Multi-Agent Architecture: 12 Specialty Agents (PoC)')

RED_COLOR = RGBColor(0xC0, 0x39, 0x2B)

left_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(1.1), Inches(5.8), Inches(5.5))
bordered(left_card, ORANGE_LIGHT, ORANGE, line_pt=1.5)
header_card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), 'How It Works', ORANGE_DARK)

add_text(slide, Inches(0.7), Inches(1.72), Inches(5.4), Inches(0.55),
    'Each department is a specialized agent: its own system prompt, '
    'clinical scope, and model. The router picks the right one.',
    size=11, color=GRAY_DARK)

flow_items = [
    ('Doctors question', ORANGE, False),
    ('PHI mask + cache check', ORANGE, False),
    ('Emergency toggle ON?', RED_COLOR, True),
    ('YES: Emergency agent (Haiku 4.5)', RED_COLOR, False),
    ('NO: Router (Nova Micro, JSON mode)', ORANGE_DARK, False),
    ('Routes to 1 of 12 specialty agents', ORANGE, False),
    ('Specialty agent (Sonnet 4.5) generates answer', ORANGE_DARK, False),
    ('Citations validated + streamed to browser', GREEN, False),
]
for i, (text, color, is_decision) in enumerate(flow_items):
    y = Inches(2.38 + i * 0.46)
    if is_decision:
        shape = slide.shapes.add_shape(MSO_SHAPE.DIAMOND, Inches(0.7), y, Inches(5.2), Inches(0.38))
    else:
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), y, Inches(5.2), Inches(0.38))
        shape.adjustments[0] = 0.15
    shape.fill.solid(); shape.fill.fore_color.rgb = color; shape.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.7), y, Inches(5.2), Inches(0.38))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = text
    run.font.name = 'Calibri'; run.font.size = Pt(9.5)
    run.font.bold = True; run.font.color.rgb = WHITE

right_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(6.6), Inches(1.1), Inches(6.2), Inches(5.5))
bordered(right_card, WHITE, ORANGE, line_pt=1.5)
header_card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(0.5),
            '12 Deployed Department Agents (PoC)', ORANGE)

depts = [
    ('Emergency', 'Haiku 4.5', RED_COLOR),
    ('Cardiology', 'Sonnet 4.5', ORANGE_DARK),
    ('Pulmonology', 'Sonnet 4.5', ORANGE_DARK),
    ('Gastroenterology', 'Sonnet 4.5', ORANGE_DARK),
    ('Nephrology', 'Sonnet 4.5', ORANGE_DARK),
    ('Endocrinology', 'Sonnet 4.5', ORANGE_DARK),
    ('Neurology', 'Sonnet 4.5', ORANGE_DARK),
    ('Infectious Disease', 'Sonnet 4.5', ORANGE_DARK),
    ('Oncology', 'Sonnet 4.5', ORANGE_DARK),
    ('Obstetrics & Gyn', 'Sonnet 4.5', ORANGE_DARK),
    ('Pediatrics', 'Sonnet 4.5', ORANGE_DARK),
    ('Radiology', 'Sonnet 4.5 + Vision', ORANGE),
]
col_w = Inches(1.9); row_h = Inches(0.72)
gap_x = Inches(0.1); gap_y = Inches(0.1)
start_x = Inches(6.7); start_y = Inches(1.72)

for i, (name, model, color) in enumerate(depts):
    col = i % 3; row = i // 3
    x = start_x + col * (col_w + gap_x)
    y = start_y + row * (row_h + gap_y)
    dc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, col_w, row_h)
    bordered(dc, ORANGE_LIGHT if i % 2 == 0 else WHITE, color, line_pt=1.5, radius=0.1)
    add_text(slide, x + Inches(0.08), y + Inches(0.08), col_w - Inches(0.16), Inches(0.35),
             name, size=10, bold=True, color=color)
    add_text(slide, x + Inches(0.08), y + Inches(0.42), col_w - Inches(0.16), Inches(0.25),
             model, size=8.5, italic=True, color=GRAY_MED)

note_y = Inches(6.55)
note = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), note_y, Inches(12.3), Inches(0.42))
solid(note, ORANGE); note.adjustments[0] = 0.2
add_text(slide, Inches(0.7), note_y + Inches(0.06), Inches(11.9), Inches(0.32),
         'PoC: 12 departments, system prompt per agent, bedrock.converse() directly.  '
         'Production: 40 sub-specialties, Bedrock Agents service with tool calling.',
         size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

print('  Slide 3 (Multi-Agent 12 depts): done')

