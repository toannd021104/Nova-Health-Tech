# =============================================================================
# SLIDE 7: Compliance, Regulations & Security Standards
# =============================================================================
slide = new_slide(prs)
slide_title(slide, 'Compliance, Regulations & Security')

TEAL         = RGBColor(0x00, 0x89, 0x7B)
TEAL_LIGHT   = RGBColor(0xE0, 0xF2, 0xF1)
BLUE         = RGBColor(0x21, 0x96, 0xF3)
BLUE_LIGHT   = RGBColor(0xE3, 0xF2, 0xFD)
PURPLE       = RGBColor(0x7B, 0x1F, 0xA2)
PURPLE_LIGHT = RGBColor(0xF3, 0xE5, 0xF5)
AMBER        = RGBColor(0xFF, 0x8F, 0x00)
AMBER_LIGHT  = RGBColor(0xFF, 0xF8, 0xE1)
RED_COLOR    = RGBColor(0xC0, 0x39, 0x2B)
RED_LIGHT    = RGBColor(0xFE, 0xF2, 0xF2)

# ============================================================
# ROW 1: Singapore Regulations (top-left 3 cards)
# ============================================================
sg_label = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(0.5), Inches(1.1), Inches(7.8), Inches(0.38))
solid(sg_label, TEAL)
add_text(slide, Inches(0.5), Inches(1.1), Inches(7.8), Inches(0.38),
         'Singapore Healthcare Regulations', size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

sg_regs = [
    ('PDPA', 'Personal Data Protection Act',
     'Patient data protection, 72h breach notification, DPO required',
     'PHI mask + KMS BYOK + audit trail'),
    ('HCSA 2020', 'Healthcare Services Act',
     'License for clinical decision support (replaces PHMC 1980)',
     'Decision support only, human-in-the-loop, audit ready'),
    ('HIA 2026', 'Health Information Act',
     'Mandatory NEHR contribution (effective early 2027)',
     'NEHR connector planned Year 2, consent + audit trail'),
    ('AIHGle 2.0', 'AI in Healthcare Guidelines\n(MOH+HSA, March 2026)',
     '7 principles: safety, fairness, transparency, explainability...',
     'All 7 principles addressed in architecture'),
]
sg_w = Inches(1.85); sg_h = Inches(1.55); sg_gap = Inches(0.08)
sg_start_x = Inches(0.5); sg_y = Inches(1.55)

for i, (code, name, scope, impl) in enumerate(sg_regs):
    x = sg_start_x + i * (sg_w + sg_gap)
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, sg_y, sg_w, sg_h)
    bordered(c, TEAL_LIGHT, TEAL, line_pt=1.5, radius=0.06)
    hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, sg_y, sg_w, Inches(0.38))
    solid(hdr, TEAL)
    add_text(slide, x, sg_y, sg_w, Inches(0.38),
             code, size=13, bold=True, color=WHITE, align=PP_ALIGN.CENTER)
    add_text(slide, x + Inches(0.08), sg_y + Inches(0.42), sg_w - Inches(0.16), Inches(0.32),
             name, size=8.5, bold=True, color=TEAL)
    add_text(slide, x + Inches(0.08), sg_y + Inches(0.76), sg_w - Inches(0.16), Inches(0.38),
             scope, size=8, italic=True, color=GRAY_DARK)
    add_text(slide, x + Inches(0.08), sg_y + Inches(1.18), sg_w - Inches(0.16), Inches(0.32),
             impl, size=8, color=GREEN, bold=True)

# ============================================================
# ROW 1 RIGHT: Clinical Standards
# ============================================================
cl_label = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(8.55), Inches(1.1), Inches(4.3), Inches(0.38))
solid(cl_label, BLUE)
add_text(slide, Inches(8.55), Inches(1.1), Inches(4.3), Inches(0.38),
         'Clinical & International Standards', size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

cl_items = [
    ('HSA SaMD Class B', 'Software as Medical Device registration\nvia SHARE platform (July 2025)'),
    ('HIPAA 164.530(j)', '6-year audit retention via S3 Object Lock\nSigned BAA over Bedrock + S3 + Lambda'),
    ('ISO 27001 / SOC 2', 'Inherited from AWS Singapore\nNo separate Nova certification needed'),
    ('IMDA AI Verify', 'Responsible AI framework\nSelf-assessment planned Month 5'),
]
cl_y = Inches(1.55)
for i, (std, desc) in enumerate(cl_items):
    y = cl_y + i * Inches(0.38)
    bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(8.55), y, Inches(4.3), Inches(0.35))
    bordered(bg, BLUE_LIGHT if i % 2 == 0 else WHITE, BLUE, line_pt=1, radius=0.08)
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.55), y, Inches(0.05), Inches(0.35))
    solid(acc, BLUE)
    add_text(slide, Inches(8.65), y + Inches(0.02), Inches(1.3), Inches(0.18),
             std, size=9, bold=True, color=BLUE)
    add_text(slide, Inches(10.0), y + Inches(0.02), Inches(2.75), Inches(0.32),
             desc, size=8, italic=True, color=GRAY_DARK)

# ============================================================
# ROW 2: Shared Responsibility Model
# ============================================================
sr_y = Inches(3.28)
sr_label = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(0.5), sr_y, Inches(12.3), Inches(0.38))
solid(sr_label, ORANGE_DARK)
add_text(slide, Inches(0.5), sr_y, Inches(12.3), Inches(0.38),
         'AWS Shared Responsibility Model', size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

# AWS responsibility (left)
aws_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), sr_y + Inches(0.42), Inches(5.8), Inches(1.85))
bordered(aws_card, ORANGE_LIGHT, ORANGE, line_pt=1.5)
aws_hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(0.5), sr_y + Inches(0.42), Inches(5.8), Inches(0.38))
solid(aws_hdr, ORANGE)
add_text(slide, Inches(0.5), sr_y + Inches(0.42), Inches(5.8), Inches(0.38),
         'AWS Responsibility  (Security OF the Cloud)', size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

aws_items = [
    'Physical data center security (Singapore ap-southeast-1)',
    'Hardware, network, hypervisor infrastructure',
    'Managed service availability (Bedrock, OpenSearch, Neptune)',
    'ISO 27001, SOC 2, PCI-DSS certifications',
    'Compliance with Singapore data residency requirements',
]
for i, item in enumerate(aws_items):
    tb = slide.shapes.add_textbox(Inches(0.65), sr_y + Inches(0.88 + i * 0.27), Inches(5.5), Inches(0.26))
    tf = tb.text_frame; p = tf.paragraphs[0]
    b = p.add_run(); b.text = '\u25b8 '
    b.font.name = 'Calibri'; b.font.size = Pt(10); b.font.bold = True; b.font.color.rgb = ORANGE
    t = p.add_run(); t.text = item
    t.font.name = 'Calibri'; t.font.size = Pt(9.5); t.font.color.rgb = GRAY_DARK

# Nova responsibility (middle)
nova_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(6.55), sr_y + Inches(0.42), Inches(3.0), Inches(1.85))
bordered(nova_card, PURPLE_LIGHT, PURPLE, line_pt=1.5)
nova_hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(6.55), sr_y + Inches(0.42), Inches(3.0), Inches(0.38))
solid(nova_hdr, PURPLE)
add_text(slide, Inches(6.55), sr_y + Inches(0.42), Inches(3.0), Inches(0.38),
         'Nova Responsibility', size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

nova_items = [
    'PHI masking (Comprehend Medical)',
    'Application security + PDPA',
    'HCSA license + audit trail',
    'Guardrails + citation validator',
    'Incident response + DPO',
]
for i, item in enumerate(nova_items):
    tb = slide.shapes.add_textbox(Inches(6.7), sr_y + Inches(0.88 + i * 0.27), Inches(2.7), Inches(0.26))
    tf = tb.text_frame; p = tf.paragraphs[0]
    b = p.add_run(); b.text = '\u25b8 '
    b.font.name = 'Calibri'; b.font.size = Pt(10); b.font.bold = True; b.font.color.rgb = PURPLE
    t = p.add_run(); t.text = item
    t.font.name = 'Calibri'; t.font.size = Pt(9.5); t.font.color.rgb = GRAY_DARK

# Hospital responsibility (right)
hosp_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(9.8), sr_y + Inches(0.42), Inches(3.0), Inches(1.85))
bordered(hosp_card, AMBER_LIGHT, AMBER, line_pt=1.5)
hosp_hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(9.8), sr_y + Inches(0.42), Inches(3.0), Inches(0.38))
solid(hosp_hdr, AMBER)
add_text(slide, Inches(9.8), sr_y + Inches(0.42), Inches(3.0), Inches(0.38),
         'Hospital Responsibility', size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

hosp_items = [
    'Clinical decisions (physician)',
    'HCSA license (deployer)',
    'Staff training + consent',
    'EHR access controls',
    'Adverse event reporting',
]
for i, item in enumerate(hosp_items):
    tb = slide.shapes.add_textbox(Inches(9.95), sr_y + Inches(0.88 + i * 0.27), Inches(2.7), Inches(0.26))
    tf = tb.text_frame; p = tf.paragraphs[0]
    b = p.add_run(); b.text = '\u25b8 '
    b.font.name = 'Calibri'; b.font.size = Pt(10); b.font.bold = True; b.font.color.rgb = AMBER
    t = p.add_run(); t.text = item
    t.font.name = 'Calibri'; t.font.size = Pt(9.5); t.font.color.rgb = GRAY_DARK

# ============================================================
# ROW 3: Security Controls (bottom)
# ============================================================
sec_y = Inches(5.38)
sec_label = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(0.5), sec_y, Inches(12.3), Inches(0.38))
solid(sec_label, GRAY_DARK)
add_text(slide, Inches(0.5), sec_y, Inches(12.3), Inches(0.38),
         'Security Controls in the Solution', size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

sec_controls = [
    ('\U0001f512', 'PHI Masking', 'Comprehend Medical\ntokenizes before model'),
    ('\U0001f5dd\ufe0f', 'KMS BYOK', 'Hospital controls\nencryption keys'),
    ('\U0001f4cb', 'Audit Trail', 'S3 Object Lock\n6-year WORM retention'),
    ('\U0001f6e1\ufe0f', 'Guardrails', 'Bedrock Guardrails\ngrounding + PHI filter'),
    ('\U0001f310', 'Data Residency', '100% ap-southeast-1\nzero cross-border'),
    ('\U0001f465', 'Access Control', 'Cognito + ABAC\ntenant isolation'),
]
ctrl_w = Inches(1.95); ctrl_h = Inches(0.88); ctrl_gap = Inches(0.1)
ctrl_start_x = Inches(0.5); ctrl_y = sec_y + Inches(0.42)

for i, (icon, title, desc) in enumerate(sec_controls):
    x = ctrl_start_x + i * (ctrl_w + ctrl_gap)
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, ctrl_y, ctrl_w, ctrl_h)
    bordered(c, ORANGE_LIGHT if i % 2 == 0 else WHITE, ORANGE, line_pt=1.2, radius=0.1)
    icon_tb = slide.shapes.add_textbox(x, ctrl_y + Inches(0.04), ctrl_w, Inches(0.38))
    tf = icon_tb.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = icon
    run.font.name = 'Segoe UI Emoji'; run.font.size = Pt(20)
    add_text(slide, x, ctrl_y + Inches(0.42), ctrl_w, Inches(0.2),
             title, size=9.5, bold=True, color=ORANGE_DARK, align=PP_ALIGN.CENTER)
    add_text(slide, x, ctrl_y + Inches(0.62), ctrl_w, Inches(0.24),
             desc, size=8, italic=True, color=GRAY_MED, align=PP_ALIGN.CENTER)

# Bottom note
note = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(6.65), Inches(12.3), Inches(0.38))
solid(note, ORANGE); note.adjustments[0] = 0.2
add_text(slide, Inches(0.7), Inches(6.69), Inches(11.9), Inches(0.32),
         'AWS secures the cloud infrastructure.  Nova secures the application + data.  Hospital secures clinical decisions + staff.',
         size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

print('  Slide 7 (Compliance + Security): done')
