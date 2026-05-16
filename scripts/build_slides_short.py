"""Build the 3-minute Nova Health Tech client presentation deck.

Output: docs/Nova_Health_Tech_AWS_Claude_Presentation_3min.pptx

Design rules:
- 6 slides total, ~3 minutes speaking time
- Slide 1: Title (mainslide.png background)
- Slides 2-6: White background, orange accent (FF6B35)
- Strong emphasis on Singapore healthcare compliance
- Concise presenter notes (20-30s each)
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from lxml import etree

REPO = Path(__file__).resolve().parent.parent
BG_IMAGE = str(REPO / "mainslide.png")
OUT_PATH = str(REPO / "docs" / "Nova_Health_Tech_AWS_Claude_Presentation_3min.pptx")

# Color palette
ORANGE = RGBColor(0xFF, 0x6B, 0x35)
ORANGE_DARK = RGBColor(0xCC, 0x4F, 0x1F)
ORANGE_LIGHT = RGBColor(0xFF, 0xE8, 0xDA)
GRAY_DARK = RGBColor(0x2C, 0x3E, 0x50)
GRAY_MED = RGBColor(0x64, 0x64, 0x64)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x27, 0xAE, 0x60)
RED = RGBColor(0xC0, 0x39, 0x2B)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)


def add_title_slide(prs, title, subtitle, notes):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)
    slide.shapes.add_picture(BG_IMAGE, 0, 0, width=SLIDE_W, height=SLIDE_H)

    overlay = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(2.5), SLIDE_W, Inches(2.5))
    overlay.fill.solid()
    overlay.fill.fore_color.rgb = RGBColor(0x00, 0x00, 0x00)
    sp = overlay.fill._xPr.find(qn('a:solidFill'))
    if sp is not None:
        srgbClr = sp.find(qn('a:srgbClr'))
        if srgbClr is not None:
            alpha = etree.SubElement(srgbClr, qn('a:alpha'))
            alpha.set('val', '40000')
    overlay.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(1.2))
    tf = title_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    run.font.name = "Calibri"
    run.font.size = Pt(40)
    run.font.bold = True
    run.font.color.rgb = WHITE

    sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(4.0), Inches(11.7), Inches(0.7))
    tf = sub_box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = subtitle
    run.font.name = "Calibri"
    run.font.size = Pt(20)
    run.font.color.rgb = WHITE

    slide.notes_slide.notes_text_frame.text = notes
    return slide


def add_content_slide(prs, title, notes):
    blank = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank)

    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid()
    bg.fill.fore_color.rgb = WHITE
    bg.line.fill.background()

    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.12))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ORANGE
    top_bar.line.fill.background()

    title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.25), Inches(12.3), Inches(0.7))
    tf = title_box.text_frame
    tf.margin_left = 0
    tf.margin_top = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = title
    run.font.name = "Calibri"
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = ORANGE_DARK

    underline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.0), Inches(2), Inches(0.04))
    underline.fill.solid()
    underline.fill.fore_color.rgb = ORANGE
    underline.line.fill.background()

    footer = slide.shapes.add_textbox(Inches(0.5), Inches(7.05), Inches(12.3), Inches(0.3))
    tf = footer.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = "Nova Health Tech · Clinical GenAI Assistant · AWS Singapore"
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.color.rgb = GRAY_MED
    run.font.italic = True

    slide.notes_slide.notes_text_frame.text = notes
    return slide


def add_table_simple(slide, left, top, width, height, headers, rows, *, header_color=ORANGE):
    n_rows = len(rows) + 1
    n_cols = len(headers)
    tbl_shape = slide.shapes.add_table(n_rows, n_cols, left, top, width, height)
    tbl = tbl_shape.table

    for j, h in enumerate(headers):
        cell = tbl.cell(0, j)
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_color
        tf = cell.text_frame
        tf.margin_left = Inches(0.08)
        tf.margin_top = Inches(0.04)
        p = tf.paragraphs[0]
        p.clear()
        run = p.add_run()
        run.text = h
        run.font.name = "Calibri"
        run.font.size = Pt(12)
        run.font.bold = True
        run.font.color.rgb = WHITE

    for i, row in enumerate(rows, start=1):
        for j, cell_text in enumerate(row):
            cell = tbl.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if i % 2 == 1 else ORANGE_LIGHT
            tf = cell.text_frame
            tf.margin_left = Inches(0.08)
            tf.margin_top = Inches(0.03)
            p = tf.paragraphs[0]
            p.clear()
            run = p.add_run()
            run.text = str(cell_text)
            run.font.name = "Calibri"
            run.font.size = Pt(10)
            run.font.color.rgb = GRAY_DARK
    return tbl


# ============================================================================
prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H

# ----------------------------------------------------------------------------
# SLIDE 1: TITLE (10 seconds)
# ----------------------------------------------------------------------------
add_title_slide(
    prs,
    title="Nova Health Tech · Clinical GenAI Assistant",
    subtitle="AWS with Claude · Singapore · PDPA & HCSA compliant by design",
    notes=(
        "[10s opening]\n\n"
        "Đề xuất kiến trúc trợ lý AI lâm sàng cho Nova Health Tech: "
        "AWS Singapore, Claude 4.5, tuân thủ PDPA và HCSA ngay từ thiết kế."
    )
)

# ----------------------------------------------------------------------------
# SLIDE 2: PAIN POINTS + REQUIREMENTS (30s)
# ----------------------------------------------------------------------------
slide = add_content_slide(
    prs,
    "The Challenge",
    "[30s]\n\n"
    "Bác sĩ Nova hiện đang mất niềm tin vào công cụ hỗ trợ lâm sàng vì câu trả lời chậm "
    "và thiếu cụ thể. Có 3 thách thức lớn nhất.\n\n"
    "Một, cấp cứu cần dưới 2 giây, không có chỗ cho độ trễ. Hai, dữ liệu thử nghiệm nội bộ "
    "chứa thông tin bệnh nhân, không được rò rỉ ra ngoài Singapore. Ba, WHO cập nhật hàng tháng, "
    "ICD-11 hàng ngày, hệ thống phải tự đồng bộ.\n\n"
    "Cộng thêm yêu cầu tuân thủ PDPA, HCSA, và sẵn sàng cho HIPAA khi onboard khách Mỹ."
)

# 3 main pain points (large cards)
pains = [
    ("⚡", "Speed", "Emergency response\n< 2 seconds", RED),
    ("🔒", "Patient PHI", "Trial data must stay\nin Singapore", ORANGE_DARK),
    ("📅", "Freshness", "WHO monthly,\nICD-11 daily updates", ORANGE),
]

card_w = Inches(3.8)
card_h = Inches(3.5)
gap = Inches(0.3)
total_w = card_w * 3 + gap * 2
start_x = (SLIDE_W - total_w) / 2

for i, (icon, title, desc, color) in enumerate(pains):
    x = start_x + i * (card_w + gap)
    y = Inches(1.7)
    
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, card_w, card_h)
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = color
    card.line.width = Pt(2.5)
    card.adjustments[0] = 0.06
    
    # Icon
    icon_tb = slide.shapes.add_textbox(x, y + Inches(0.4), card_w, Inches(1.0))
    tf = icon_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = icon
    run.font.name = "Segoe UI Emoji"
    run.font.size = Pt(56)
    
    # Title
    title_tb = slide.shapes.add_textbox(x, y + Inches(1.6), card_w, Inches(0.5))
    tf = title_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    run.font.name = "Calibri"
    run.font.size = Pt(22)
    run.font.bold = True
    run.font.color.rgb = color
    
    # Desc
    desc_tb = slide.shapes.add_textbox(x + Inches(0.2), y + Inches(2.3), card_w - Inches(0.4), Inches(1.1))
    tf = desc_tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = desc
    run.font.name = "Calibri"
    run.font.size = Pt(14)
    run.font.color.rgb = GRAY_DARK

# Bottom note
note_y = Inches(5.5)
note_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), note_y, Inches(11.3), Inches(1.0))
note_box.fill.solid()
note_box.fill.fore_color.rgb = ORANGE_LIGHT
note_box.line.color.rgb = ORANGE
note_box.line.width = Pt(1)
note_box.adjustments[0] = 0.2

note_tb = slide.shapes.add_textbox(Inches(1.2), note_y + Inches(0.15), Inches(10.9), Inches(0.8))
tf = note_tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Plus: Singapore PDPA + HCSA compliance · auditable for 6 years · 600k calls/month at launch"
run.font.name = "Calibri"
run.font.size = Pt(15)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK
p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
run2 = p2.add_run()
run2.text = "Internal trial PDFs · WHO API · ICD-11 · PubMed · EHR (FHIR R4)"
run2.font.name = "Calibri"
run2.font.size = Pt(11)
run2.font.italic = True
run2.font.color.rgb = GRAY_MED

# ----------------------------------------------------------------------------
# SLIDE 3: SOLUTION OVERVIEW (45s)
# ----------------------------------------------------------------------------
slide = add_content_slide(
    prs,
    "Solution: Two-Lane Architecture, Singapore-Native",
    "[45s]\n\n"
    "Giải pháp là kiến trúc 2 luồng. Cấp cứu đi thẳng Claude Haiku 4.5 với top-3 vector và "
    "top-2 graph, không qua router, không guardrails để đạt TTFT 2.5 giây. Phức tạp đi qua "
    "Nova Micro phân loại 12 phòng ban, rồi Sonnet 4.5 với top-15 vector và top-3 graph, "
    "có guardrails đầy đủ.\n\n"
    "RAG dùng 2 loại: vector trên OpenSearch Serverless và GraphRAG trên Neptune Analytics. "
    "Cả 2 đều ở Singapore, dùng Cohere Embed v3 SG-native. Không có cross-region hop nào "
    "cho dữ liệu lâm sàng.\n\n"
    "PoC đã chạy live trên EC2 Singapore, 100% pass SLA, 100% câu trả lời có citation."
)

# Two-lane comparison
lane_y = Inches(1.4)
lane_w = Inches(6.0)
lane_h = Inches(4.0)

# Emergency lane
em_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), lane_y, lane_w, lane_h)
em_card.fill.solid()
em_card.fill.fore_color.rgb = WHITE
em_card.line.color.rgb = RED
em_card.line.width = Pt(2.5)
em_card.adjustments[0] = 0.04

em_h = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), lane_y, lane_w, Inches(0.6))
em_h.fill.solid()
em_h.fill.fore_color.rgb = RED
em_h.line.fill.background()

em_h_tb = slide.shapes.add_textbox(Inches(0.5), lane_y, lane_w, Inches(0.6))
tf = em_h_tb.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "EMERGENCY · 2.5s TTFT"
run.font.name = "Calibri"
run.font.size = Pt(18)
run.font.bold = True
run.font.color.rgb = WHITE

em_lines = [
    "▸  Claude Haiku 4.5 (fast)",
    "▸  Vector top-3 + GraphRAG top-2",
    "▸  No router, direct to emergency agent",
    "▸  No guardrails (speed priority)",
    "▸  max_tokens 300, streaming SSE",
    "▸  Target SLA: < 5 seconds",
    "▸  PoC measured: 100% pass",
]
em_tb = slide.shapes.add_textbox(Inches(0.8), lane_y + Inches(0.85), lane_w - Inches(0.5), lane_h - Inches(1.0))
tf = em_tb.text_frame
tf.word_wrap = True
for i, line in enumerate(em_lines):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    run = p.add_run()
    run.text = line
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.font.color.rgb = GRAY_DARK
    p.space_after = Pt(8)

# Complex lane
cx_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), lane_y, lane_w, lane_h)
cx_card.fill.solid()
cx_card.fill.fore_color.rgb = WHITE
cx_card.line.color.rgb = ORANGE_DARK
cx_card.line.width = Pt(2.5)
cx_card.adjustments[0] = 0.04

cx_h = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), lane_y, lane_w, Inches(0.6))
cx_h.fill.solid()
cx_h.fill.fore_color.rgb = ORANGE_DARK
cx_h.line.fill.background()

cx_h_tb = slide.shapes.add_textbox(Inches(6.8), lane_y, lane_w, Inches(0.6))
tf = cx_h_tb.text_frame
tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "COMPLEX · 9.7s TTFT"
run.font.name = "Calibri"
run.font.size = Pt(18)
run.font.bold = True
run.font.color.rgb = WHITE

cx_lines = [
    "▸  Claude Sonnet 4.5 (deep reasoning)",
    "▸  Vector top-15 + GraphRAG top-3",
    "▸  Nova Micro routes to 12 departments",
    "▸  Bedrock Guardrails enabled",
    "▸  max_tokens 1500, streaming SSE",
    "▸  Target SLA: < 15 seconds",
    "▸  PoC measured: 100% pass",
]
cx_tb = slide.shapes.add_textbox(Inches(7.1), lane_y + Inches(0.85), lane_w - Inches(0.5), lane_h - Inches(1.0))
tf = cx_tb.text_frame
tf.word_wrap = True
for i, line in enumerate(cx_lines):
    if i == 0:
        p = tf.paragraphs[0]
    else:
        p = tf.add_paragraph()
    run = p.add_run()
    run.text = line
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.font.color.rgb = GRAY_DARK
    p.space_after = Pt(8)

# Bottom: shared infrastructure
shared_y = Inches(5.7)
shared_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), shared_y, Inches(12.3), Inches(1.1))
shared_box.fill.solid()
shared_box.fill.fore_color.rgb = ORANGE_LIGHT
shared_box.line.color.rgb = ORANGE
shared_box.line.width = Pt(1.5)
shared_box.adjustments[0] = 0.1

shared_tb = slide.shapes.add_textbox(Inches(0.7), shared_y + Inches(0.1), Inches(11.9), Inches(0.9))
tf = shared_tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Shared Infrastructure (100% Singapore-Native)"
run.font.name = "Calibri"
run.font.size = Pt(15)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK
p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
run2 = p2.add_run()
run2.text = (
    "OpenSearch Serverless (vector KB)  ·  Neptune Analytics (GraphRAG)  ·  Cohere Embed Multilingual v3  ·  "
    "Bedrock Knowledge Bases  ·  Comprehend Medical (PHI mask)  ·  ElastiCache Redis (semantic cache)"
)
run2.font.name = "Calibri"
run2.font.size = Pt(12)
run2.font.color.rgb = GRAY_DARK

# ----------------------------------------------------------------------------
# SLIDE 4: SINGAPORE COMPLIANCE (45s) — KEY SLIDE
# ----------------------------------------------------------------------------
slide = add_content_slide(
    prs,
    "Singapore Healthcare Compliance: Built-In, Not Bolted-On",
    "[45s, KEY SLIDE]\n\n"
    "Đây là phần Nova Health Tech cần lưu ý nhất. Singapore có 4 quy định chính áp dụng "
    "trực tiếp cho hệ thống AI lâm sàng.\n\n"
    "Một, PDPA do PDPC quản, bảo vệ dữ liệu cá nhân bệnh nhân, yêu cầu Data Protection Officer, "
    "thông báo vi phạm trong 72 giờ. Hai, HCSA do MOH ban hành 2020 thay PHMC, bắt buộc license "
    "cho dịch vụ y tế và clinical decision support. Ba, Cybersecurity Act 2018 cho Critical "
    "Information Infrastructure trong y tế. Bốn, IMDA AI Verify framework cho AI có trách nhiệm.\n\n"
    "Tất cả deployment ở ap-southeast-1, dữ liệu bệnh nhân không bao giờ rời Singapore. "
    "AWS đã có signed BAA, ISO 27001, SOC 2 Type II, PDPA-compliant."
)

# 4 key SG regulations as prominent cards
sg_regs = [
    {
        "title": "PDPA",
        "subtitle": "Personal Data Protection Act",
        "authority": "PDPC (Personal Data Protection Commission)",
        "scope": "Patient data protection, consent, breach notification within 72 hours",
        "our_response": "Comprehend Medical PHI mask, KMS per-tenant CMK, audit trail",
        "color": ORANGE_DARK,
    },
    {
        "title": "HCSA",
        "subtitle": "Healthcare Services Act 2020",
        "authority": "MOH (Ministry of Health)",
        "scope": "Licensing for clinical decision support, replaces PHMC 1980",
        "our_response": "Decision support only with human-in-the-loop, audit ready",
        "color": ORANGE,
    },
    {
        "title": "Cybersecurity Act",
        "subtitle": "Critical Info Infrastructure 2018",
        "authority": "CSA (Cyber Security Agency)",
        "scope": "Healthcare CII protection, incident reporting, security audits",
        "our_response": "GuardDuty + Security Hub + Macie, Security Lake aggregation",
        "color": ORANGE_DARK,
    },
    {
        "title": "AI Verify",
        "subtitle": "Responsible AI Framework",
        "authority": "IMDA (Infocomm Media Development)",
        "scope": "Transparency, fairness, accountability for AI systems",
        "our_response": "chat_trace audit log, citation validator, Bedrock Guardrails",
        "color": ORANGE,
    },
]

cw = Inches(3.0)
ch = Inches(4.0)
gap = Inches(0.1)
total_w = cw * 4 + gap * 3
start_x = (SLIDE_W - total_w) / 2
y = Inches(1.4)

for i, reg in enumerate(sg_regs):
    x = start_x + i * (cw + gap)
    
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, cw, ch)
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = reg["color"]
    card.line.width = Pt(2)
    card.adjustments[0] = 0.05
    
    # Header
    header = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, cw, Inches(0.85))
    header.fill.solid()
    header.fill.fore_color.rgb = reg["color"]
    header.line.fill.background()
    
    h_tb = slide.shapes.add_textbox(x, y + Inches(0.05), cw, Inches(0.85))
    tf = h_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = reg["title"]
    run.font.name = "Calibri"
    run.font.size = Pt(20)
    run.font.bold = True
    run.font.color.rgb = WHITE
    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    run2 = p2.add_run()
    run2.text = reg["subtitle"]
    run2.font.name = "Calibri"
    run2.font.size = Pt(10)
    run2.font.color.rgb = WHITE
    
    # Body
    body_y = y + Inches(0.95)
    
    # Authority
    auth_tb = slide.shapes.add_textbox(x + Inches(0.15), body_y, cw - Inches(0.3), Inches(0.5))
    tf = auth_tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Authority"
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = ORANGE_DARK
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = reg["authority"]
    run2.font.name = "Calibri"
    run2.font.size = Pt(10)
    run2.font.color.rgb = GRAY_DARK
    
    # Scope
    scope_tb = slide.shapes.add_textbox(x + Inches(0.15), body_y + Inches(0.95), cw - Inches(0.3), Inches(1.1))
    tf = scope_tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Scope"
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = ORANGE_DARK
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = reg["scope"]
    run2.font.name = "Calibri"
    run2.font.size = Pt(10)
    run2.font.color.rgb = GRAY_DARK
    
    # Our response
    resp_tb = slide.shapes.add_textbox(x + Inches(0.15), body_y + Inches(2.1), cw - Inches(0.3), Inches(0.9))
    tf = resp_tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = "Our Implementation"
    run.font.name = "Calibri"
    run.font.size = Pt(9)
    run.font.bold = True
    run.font.color.rgb = GREEN
    p2 = tf.add_paragraph()
    run2 = p2.add_run()
    run2.text = reg["our_response"]
    run2.font.name = "Calibri"
    run2.font.size = Pt(10)
    run2.font.color.rgb = GRAY_DARK

# Bottom: data residency commitment
res_y = Inches(5.6)
res_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), res_y, Inches(12.3), Inches(1.1))
res_box.fill.solid()
res_box.fill.fore_color.rgb = ORANGE_LIGHT
res_box.line.color.rgb = ORANGE_DARK
res_box.line.width = Pt(2)
res_box.adjustments[0] = 0.1

res_tb = slide.shapes.add_textbox(Inches(0.7), res_y + Inches(0.1), Inches(11.9), Inches(0.9))
tf = res_tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Data Residency Commitment"
run.font.name = "Calibri"
run.font.size = Pt(15)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK
p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
run2 = p2.add_run()
run2.text = (
    "100% deployment in ap-southeast-1 (Singapore)  ·  Patient cleartext never leaves SG  ·  "
    "Cross-region: tokens only  ·  6-year audit retention via S3 Object Lock (HIPAA §164.530j)"
)
run2.font.name = "Calibri"
run2.font.size = Pt(12)
run2.font.color.rgb = GRAY_DARK

# ----------------------------------------------------------------------------
# SLIDE 5: PERFORMANCE & COST (45s)
# ----------------------------------------------------------------------------
slide = add_content_slide(
    prs,
    "PoC Results & Cost",
    "[45s]\n\n"
    "PoC đã chạy live trên EC2 Singapore với WHO COVID-19 guideline 198 trang. "
    "Test 20 câu hỏi thực tế, 100% pass SLA cả emergency và complex, 100% câu trả lời có citation.\n\n"
    "Cấp cứu TTFT trung bình 2.5 giây, dùng Haiku 4.5 với top-3 vector và top-2 graph. "
    "Phức tạp 9.7 giây với Sonnet 4.5 và 18 chunks context. Production thêm Reserved Tier "
    "và Prompt Caching sẽ giảm xuống đúng 2 giây spec gốc.\n\n"
    "Chi phí 600k calls một tháng: phương án Nova khoảng 2,800 USD, phương án Claude với "
    "Nova Lite distilled student khoảng 5,500 USD. Sẵn sàng demo live nếu Ban lãnh đạo quan tâm."
)

# Top: 4 key metrics
metrics = [
    ("Emergency TTFT", "2.5s", "Haiku 4.5 + dual KB", GREEN),
    ("Complex TTFT", "9.7s", "Sonnet 4.5 + Guardrails", GREEN),
    ("Answer Rate", "100%", "All grounded with citations", GREEN),
    ("SLA Pass", "100%", "20/20 test questions", GREEN),
]

m_y = Inches(1.4)
m_w = Inches(2.85)
m_h = Inches(1.4)
m_gap = Inches(0.2)
total_w = m_w * 4 + m_gap * 3
start_x = (SLIDE_W - total_w) / 2

for i, (label, value, sub, color) in enumerate(metrics):
    x = start_x + i * (m_w + m_gap)
    
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, m_y, m_w, m_h)
    card.fill.solid()
    card.fill.fore_color.rgb = WHITE
    card.line.color.rgb = ORANGE
    card.line.width = Pt(2)
    card.adjustments[0] = 0.06
    
    label_tb = slide.shapes.add_textbox(x, m_y + Inches(0.1), m_w, Inches(0.3))
    tf = label_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.color.rgb = GRAY_MED
    
    value_tb = slide.shapes.add_textbox(x, m_y + Inches(0.35), m_w, Inches(0.65))
    tf = value_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = value
    run.font.name = "Calibri"
    run.font.size = Pt(34)
    run.font.bold = True
    run.font.color.rgb = ORANGE_DARK
    
    sub_tb = slide.shapes.add_textbox(x, m_y + Inches(1.0), m_w, Inches(0.35))
    tf = sub_tb.text_frame
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = sub
    run.font.name = "Calibri"
    run.font.size = Pt(11)
    run.font.italic = True
    run.font.color.rgb = GRAY_DARK

# Cost table
cost_y = Inches(3.1)
add_text_box_func = None  # placeholder - we'll build inline
cost_label_box = slide.shapes.add_textbox(Inches(0.5), cost_y, Inches(12.3), Inches(0.4))
tf = cost_label_box.text_frame
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Monthly Cost Estimation (600,000 calls/month baseline)"
run.font.name = "Calibri"
run.font.size = Pt(15)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK

headers = ["Component", "Variant A1+ (Nova)", "Variant A2 (Claude)"]
rows = [
    ["LLM inference (emergency + complex)", "$1,540", "$5,810"],
    ["Embedding (Cohere Embed v3 SG)", "$10", "$10"],
    ["OpenSearch Serverless + Neptune Analytics", "$465", "$465"],
    ["Bedrock Guardrails + Comprehend Medical", "$360", "$360"],
    ["ElastiCache Redis + VPN + Lambda + S3", "$430", "$430"],
    ["Distillation + Nova Lite student offset", "—", "−$1,530"],
    ["TOTAL / month", "$2,805", "$5,545"],
]
add_table_simple(slide, Inches(0.5), Inches(3.6), Inches(12.3), Inches(2.6), headers, rows)

# Bottom: scale + recommendation
rec_y = Inches(6.3)
rec_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.5), rec_y, Inches(12.3), Inches(0.7))
rec_box.fill.solid()
rec_box.fill.fore_color.rgb = ORANGE_LIGHT
rec_box.line.color.rgb = ORANGE
rec_box.line.width = Pt(1)
rec_box.adjustments[0] = 0.2

rec_tb = slide.shapes.add_textbox(Inches(0.7), rec_y + Inches(0.1), Inches(11.9), Inches(0.55))
tf = rec_tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "At 3M calls/month: A1+ scales to $10,500   ·   A2 to $23,500   ·   Recommended: A1+ for cost, A2 for premium tier"
run.font.name = "Calibri"
run.font.size = Pt(12)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK

# ----------------------------------------------------------------------------
# SLIDE 6: CALL TO ACTION (15s)
# ----------------------------------------------------------------------------
slide = add_content_slide(
    prs,
    "Ready to Deploy",
    "[15s closing]\n\n"
    "Tóm lại: kiến trúc đã được PoC kiểm chứng, Singapore-native, tuân thủ PDPA HCSA sẵn, "
    "chi phí từ 2,800 USD một tháng. Lộ trình triển khai 6-10 tuần. "
    "PoC đang chạy live, có thể demo ngay. Cảm ơn quý vị."
)

# Roadmap
rm_y = Inches(1.4)
add_text_box_helper = slide.shapes.add_textbox(Inches(0.5), rm_y, Inches(12.3), Inches(0.4))
tf = add_text_box_helper.text_frame
p = tf.paragraphs[0]
run = p.add_run()
run.text = "Implementation Roadmap (6 to 10 weeks)"
run.font.name = "Calibri"
run.font.size = Pt(16)
run.font.bold = True
run.font.color.rgb = ORANGE_DARK

phases = [
    ("Wk 1-2", "Foundation", "SG provisioning, BAA, WHO+ICD-11 ingest"),
    ("Wk 3-4", "Customization", "Bedrock Distillation: Nova Lite student"),
    ("Wk 5-6", "Integration", "EHR FHIR, SharePoint, Cognito federation"),
    ("Wk 7-8", "Hardening", "Red team, Guardrails tune, load test"),
    ("Launch", "Go-Live", "All 12 departments, audit + cache live"),
]

phase_y = Inches(1.95)
phase_h = Inches(0.55)
for i, (week, name, desc) in enumerate(phases):
    y = phase_y + i * (phase_h + Inches(0.08))
    
    badge = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), y, Inches(1.5), phase_h)
    badge.fill.solid()
    badge.fill.fore_color.rgb = ORANGE
    badge.line.fill.background()
    
    badge_tb = slide.shapes.add_textbox(Inches(0.5), y, Inches(1.5), phase_h)
    tf = badge_tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = week
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.font.bold = True
    run.font.color.rgb = WHITE
    
    name_tb = slide.shapes.add_textbox(Inches(2.2), y, Inches(2.4), phase_h)
    tf = name_tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = name
    run.font.name = "Calibri"
    run.font.size = Pt(15)
    run.font.bold = True
    run.font.color.rgb = ORANGE_DARK
    
    desc_tb = slide.shapes.add_textbox(Inches(4.7), y, Inches(8.0), phase_h)
    tf = desc_tb.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    run = p.add_run()
    run.text = desc
    run.font.name = "Calibri"
    run.font.size = Pt(13)
    run.font.color.rgb = GRAY_DARK

# Bottom: live demo
demo_y = Inches(5.4)
demo_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), demo_y, Inches(10.3), Inches(1.6))
demo_box.fill.solid()
demo_box.fill.fore_color.rgb = ORANGE
demo_box.line.fill.background()
demo_box.adjustments[0] = 0.1

demo_tb = slide.shapes.add_textbox(Inches(1.7), demo_y + Inches(0.15), Inches(9.9), Inches(1.3))
tf = demo_tb.text_frame
tf.word_wrap = True
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
run = p.add_run()
run.text = "Live PoC Available Now"
run.font.name = "Calibri"
run.font.size = Pt(22)
run.font.bold = True
run.font.color.rgb = WHITE

p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.CENTER
run2 = p2.add_run()
run2.text = "http://47.130.120.152/ui/index.html"
run2.font.name = "Consolas"
run2.font.size = Pt(16)
run2.font.color.rgb = WHITE

p3 = tf.add_paragraph()
p3.alignment = PP_ALIGN.CENTER
run3 = p3.add_run()
run3.text = "Questions?"
run3.font.name = "Calibri"
run3.font.size = Pt(15)
run3.font.italic = True
run3.font.color.rgb = WHITE

prs.save(OUT_PATH)
print(f"Saved: {OUT_PATH}")
print(f"Total slides: {len(prs.slides)}")
