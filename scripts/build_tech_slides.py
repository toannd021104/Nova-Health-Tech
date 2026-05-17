"""Build technology explanation slides + RAG vs Fine-tuning comparison slide."""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Theme colors
ORANGE       = RGBColor(0xFF, 0x6B, 0x35)
ORANGE_DARK  = RGBColor(0xCC, 0x4F, 0x1F)
ORANGE_LIGHT = RGBColor(0xFF, 0xE8, 0xDA)
GRAY_DARK    = RGBColor(0x2C, 0x3E, 0x50)
GRAY_MED     = RGBColor(0x64, 0x64, 0x64)
GRAY_LIGHT   = RGBColor(0xCB, 0xD5, 0xE1)
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
RED          = RGBColor(0xC0, 0x39, 0x2B)
RED_LIGHT    = RGBColor(0xFE, 0xF2, 0xF2)
GREEN        = RGBColor(0x27, 0xAE, 0x60)
BLUE         = RGBColor(0x21, 0x96, 0xF3)
BLUE_LIGHT   = RGBColor(0xE3, 0xF2, 0xFD)
PURPLE       = RGBColor(0x7B, 0x1F, 0xA2)
PURPLE_LIGHT = RGBColor(0xF3, 0xE5, 0xF5)

SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

prs = Presentation()
prs.slide_width  = SLIDE_W
prs.slide_height = SLIDE_H


def new_slide(prs):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.fill.solid(); bg.fill.fore_color.rgb = WHITE; bg.line.fill.background()
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.12))
    bar.fill.solid(); bar.fill.fore_color.rgb = ORANGE; bar.line.fill.background()
    ft = s.shapes.add_textbox(Inches(0.5), Inches(7.1), Inches(12.3), Inches(0.28))
    tf = ft.text_frame; p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT
    run = p.add_run()
    run.text = "Nova Health Tech  \u00b7  Clinical GenAI Assistant  \u00b7  AWS Singapore"
    run.font.name = "Calibri"; run.font.size = Pt(9)
    run.font.italic = True; run.font.color.rgb = GRAY_MED
    return s


def slide_title(slide, text):
    tb = slide.shapes.add_textbox(Inches(0.5), Inches(0.22), Inches(12.3), Inches(0.65))
    tf = tb.text_frame; tf.margin_left = 0; tf.margin_top = 0
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.LEFT
    run = p.add_run(); run.text = text
    run.font.name = "Calibri"; run.font.size = Pt(28)
    run.font.bold = True; run.font.color.rgb = ORANGE_DARK
    ul = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
                                 Inches(0.5), Inches(0.92), Inches(len(text)*0.18), Inches(0.04))
    ul.fill.solid(); ul.fill.fore_color.rgb = ORANGE; ul.line.fill.background()


def add_text(slide, left, top, width, height, text, size=11, bold=False,
             color=None, align=PP_ALIGN.LEFT, italic=False, wrap=True):
    color = color or GRAY_DARK
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.word_wrap = wrap
    p = tf.paragraphs[0]; p.alignment = align
    run = p.add_run(); run.text = text
    run.font.name = "Calibri"; run.font.size = Pt(size)
    run.font.bold = bold; run.font.italic = italic
    run.font.color.rgb = color
    return tb


def card(slide, left, top, width, height, fill, border, radius=0.06, border_pt=1.5):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    s.fill.solid(); s.fill.fore_color.rgb = fill
    s.line.color.rgb = border; s.line.width = Pt(border_pt)
    s.adjustments[0] = radius
    return s


def header_card(slide, left, top, width, height, title, fill_color, text_color=None):
    text_color = text_color or WHITE
    h = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    h.fill.solid(); h.fill.fore_color.rgb = fill_color; h.line.fill.background()
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = title
    run.font.name = "Calibri"; run.font.size = Pt(13)
    run.font.bold = True; run.font.color.rgb = text_color


def bullet_list(slide, left, top, width, items, size=10.5, color=None,
                bullet_color=None, spacing=0.32):
    color = color or GRAY_DARK
    bullet_color = bullet_color or ORANGE
    for i, item in enumerate(items):
        tb = slide.shapes.add_textbox(left, top + Inches(i * spacing), width, Inches(spacing))
        tf = tb.text_frame; tf.word_wrap = True
        p = tf.paragraphs[0]
        b = p.add_run(); b.text = "\u25b8 "
        b.font.name = "Calibri"; b.font.size = Pt(size)
        b.font.bold = True; b.font.color.rgb = bullet_color
        t = p.add_run(); t.text = item
        t.font.name = "Calibri"; t.font.size = Pt(size)
        t.font.color.rgb = color


# =============================================================================
# SLIDE 1: Knowledge Base Vector Store
# =============================================================================
slide = new_slide(prs)
slide_title(slide, "Knowledge Base: Vector Store")

# Concept box (left)
card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(5.5), BLUE_LIGHT, BLUE, radius=0.05)
header_card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), "What is a Vector Store?", BLUE)

add_text(slide, Inches(0.7), Inches(1.7), Inches(5.4), Inches(1.2),
    "Text is converted into numbers (vectors) that capture meaning. "
    "Similar concepts end up close together in this mathematical space. "
    "When a doctor asks a question, the system finds the most similar chunks instantly.",
    size=11, color=GRAY_DARK)

# How it works steps
steps = [
    ("1", "Ingest", "PDF/API source parsed into text chunks"),
    ("2", "Embed", "Cohere Embed v3 converts each chunk to 1024-dim vector"),
    ("3", "Index", "OpenSearch Serverless stores vectors + metadata"),
    ("4", "Query", "Doctor's question embedded, nearest chunks retrieved"),
    ("5", "Rank", "Top-K chunks passed to LLM as grounding context"),
]
for i, (num, title, desc) in enumerate(steps):
    y = Inches(3.0 + i * 0.62)
    badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), y, Inches(0.42), Inches(0.42))
    badge.fill.solid(); badge.fill.fore_color.rgb = BLUE; badge.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.7), y, Inches(0.42), Inches(0.42))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = num
    run.font.name = "Calibri"; run.font.size = Pt(12)
    run.font.bold = True; run.font.color.rgb = WHITE
    add_text(slide, Inches(1.25), y, Inches(1.0), Inches(0.42), title,
             size=11, bold=True, color=BLUE)
    add_text(slide, Inches(2.3), y, Inches(3.8), Inches(0.42), desc, size=10.5, color=GRAY_DARK)

# Right: AWS vs Alibaba specs
card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(2.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(0.5), "AWS with Claude", ORANGE)
aws_items = [
    "OpenSearch Serverless (Singapore-native)",
    "Cohere Embed Multilingual v3 (1024-dim)",
    "Multi-strategy chunking: hierarchical (WHO), semantic (trials)",
    "Hybrid kNN + BM25 search",
    "No reranker in SG (production gap)",
]
bullet_list(slide, Inches(6.8), Inches(1.72), Inches(5.8), aws_items, size=10.5, bullet_color=ORANGE)

card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(2.85), PURPLE_LIGHT, PURPLE, radius=0.05)
header_card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(0.5), "Alibaba Cloud", PURPLE)
ali_items = [
    "OpenSearch Vector Search HA (dual-zone, Singapore)",
    "text-embedding-v4 (1024-dim) + tongyi-vision (1152-dim)",
    "Hierarchical chunking: parent 1500 / child 300, 15% overlap",
    "Hybrid BM25 + HNSW via Reciprocal Rank Fusion",
    "qwen3-rerank: top-20 \u2192 top-5 (available in SG)",
]
bullet_list(slide, Inches(6.8), Inches(4.37), Inches(5.8), ali_items, size=10.5, bullet_color=PURPLE)

print("  Slide 1 (Vector Store): done")

# =============================================================================
# SLIDE 2: GraphRAG
# =============================================================================
slide = new_slide(prs)
slide_title(slide, "GraphRAG: Knowledge Graph-Augmented Retrieval")

# Left: concept
card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(5.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), "Why GraphRAG?", ORANGE)

add_text(slide, Inches(0.7), Inches(1.72), Inches(5.4), Inches(1.1),
    "Vector search finds similar text. But clinical reasoning often requires "
    "multi-hop connections: Drug A \u2192 treats Condition B \u2192 contraindicated with Drug C. "
    "GraphRAG captures these entity relationships explicitly.",
    size=11, color=GRAY_DARK)

# Graph concept visual (simple boxes + arrows)
# Entity nodes
entities = [
    (Inches(1.0), Inches(3.1), "Drug:\nCorticosteroid"),
    (Inches(3.2), Inches(2.7), "Condition:\nSevere COVID-19"),
    (Inches(3.2), Inches(3.8), "Guideline:\nWHO 2024"),
    (Inches(1.0), Inches(4.3), "Drug:\nBaricitinib"),
]
for ex, ey, elabel in entities:
    e = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ex, ey, Inches(1.8), Inches(0.65))
    e.fill.solid(); e.fill.fore_color.rgb = ORANGE
    e.line.fill.background(); e.adjustments[0] = 0.15
    tb = slide.shapes.add_textbox(ex, ey, Inches(1.8), Inches(0.65))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = elabel
    run.font.name = "Calibri"; run.font.size = Pt(9)
    run.font.bold = True; run.font.color.rgb = WHITE

# Relation labels
rels = [
    (Inches(2.0), Inches(2.95), "treats"),
    (Inches(2.0), Inches(4.15), "treats"),
    (Inches(3.4), Inches(3.35), "cited by"),
]
for rx, ry, rlabel in rels:
    add_text(slide, rx, ry, Inches(1.0), Inches(0.3), rlabel,
             size=9, italic=True, color=ORANGE_DARK, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.7), Inches(5.1), Inches(5.4), Inches(0.5),
    "Entity nodes + relation edges enable multi-hop reasoning across clinical knowledge.",
    size=10, italic=True, color=GRAY_MED)

# Right: AWS vs Alibaba
card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(2.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(0.5), "AWS with Claude", ORANGE)
aws_graph = [
    "Neptune Analytics (managed graph DB, Singapore)",
    "Claude 3 Haiku extracts entities + relations at ingest",
    "1,863 Entity nodes + 826 Chunk nodes (PoC, 1 WHO PDF)",
    "Bedrock KB GraphRAG: SEMANTIC search (HYBRID not available)",
    "Complex lane only: top-3 graph hits merged with top-15 vector",
]
bullet_list(slide, Inches(6.8), Inches(1.72), Inches(5.8), aws_graph, size=10.5, bullet_color=ORANGE)

card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(2.85), PURPLE_LIGHT, PURPLE, radius=0.05)
header_card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(0.5), "Alibaba Cloud", PURPLE)
ali_graph = [
    "AnalyticDB for PostgreSQL 7.0 + adbpg_graphrag extension",
    "3-zone HA in Singapore, 4-core 32GB vector-optimized",
    "Drug \u2192 condition \u2192 intervention \u2192 guideline nodes",
    "treats, contraindicates, cites relations",
    "Complex lane: parallel vector + graph retrieval",
]
bullet_list(slide, Inches(6.8), Inches(4.37), Inches(5.8), ali_graph, size=10.5, bullet_color=PURPLE)

print("  Slide 2 (GraphRAG): done")


# =============================================================================
# SLIDE 3: Multi-Agent Architecture
# =============================================================================
slide = new_slide(prs)
slide_title(slide, "Multi-Agent Architecture")

# Left: concept
card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(5.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), "Why Multiple Agents?", ORANGE)

add_text(slide, Inches(0.7), Inches(1.72), Inches(5.4), Inches(1.0),
    "A single general AI gives generic answers. Specialty agents are trained "
    "with department-specific context, terminology, and protocols. "
    "A router agent classifies the question and dispatches to the right specialist.",
    size=11, color=GRAY_DARK)

# Agent topology diagram
# Router
router = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(2.0), Inches(2.9), Inches(2.0), Inches(0.55))
router.fill.solid(); router.fill.fore_color.rgb = ORANGE_DARK; router.line.fill.background()
router.adjustments[0] = 0.1
tb = slide.shapes.add_textbox(Inches(2.0), Inches(2.9), Inches(2.0), Inches(0.55))
tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run = p.add_run(); run.text = "Router Agent\n(Nova Micro / Qwen Flash)"
run.font.name = "Calibri"; run.font.size = Pt(9); run.font.bold = True
run.font.color.rgb = WHITE

# Specialty agents
specialties = [
    (Inches(0.6), Inches(4.1), "Emergency\nHaiku 4.5"),
    (Inches(1.7), Inches(4.1), "Cardiology\nSonnet 4.5"),
    (Inches(2.8), Inches(4.1), "Infectious\nDisease"),
    (Inches(3.9), Inches(4.1), "Oncology"),
    (Inches(5.0), Inches(4.1), "+36 more\nspecialties"),
]
for sx, sy, slabel in specialties:
    sp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, sx, sy, Inches(0.95), Inches(0.65))
    sp.fill.solid(); sp.fill.fore_color.rgb = ORANGE; sp.line.fill.background()
    sp.adjustments[0] = 0.1
    tb = slide.shapes.add_textbox(sx, sy, Inches(0.95), Inches(0.65))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = slabel
    run.font.name = "Calibri"; run.font.size = Pt(8); run.font.bold = True
    run.font.color.rgb = WHITE

# Side-channel agents
add_text(slide, Inches(0.7), Inches(5.0), Inches(5.4), Inches(0.35),
    "Side-channel agents (auto-invoked):", size=10, bold=True, color=ORANGE_DARK)
side_agents = ["Clinical Pharmacy (on any prescribing question)",
               "Radiology (when image attached)"]
bullet_list(slide, Inches(0.7), Inches(5.38), Inches(5.4), side_agents, size=10, spacing=0.28)

# Right: AWS vs Alibaba
card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(2.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(0.5), "AWS with Claude", ORANGE)
aws_agents = [
    "Bedrock Agents: managed tool-calling runtime",
    "40 specialty agents + 1 emergency + 1 router",
    "Router: Nova Micro (JSON mode, 150-200ms)",
    "Emergency: Claude Haiku 4.5 (direct, no router)",
    "Complex: Claude Sonnet 4.5 per specialty",
    "Vision: Sonnet 4.5 (Radiology, image input)",
]
bullet_list(slide, Inches(6.8), Inches(1.72), Inches(5.8), aws_agents, size=10.5, bullet_color=ORANGE)

card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(2.85), PURPLE_LIGHT, PURPLE, radius=0.05)
header_card(slide, Inches(6.6), Inches(3.75), Inches(6.2), Inches(0.5), "Alibaba Cloud", PURPLE)
ali_agents = [
    "Model Studio Agent Applications (per department)",
    "40 Agent apps + 1 emergency Workflow Application",
    "Router: Qwen3.5-Flash JSON mode (150-200ms)",
    "Emergency: Qwen3.5-Flash (deterministic DAG)",
    "Complex: 60% Qwen3-8B student / 40% Qwen3.5-Plus",
    "Vision: Qwen3-VL-Plus (Radiology, forced on image)",
]
bullet_list(slide, Inches(6.8), Inches(4.37), Inches(5.8), ali_agents, size=10.5, bullet_color=PURPLE)

print("  Slide 3 (Multi-Agent): done")

# =============================================================================
# SLIDE 4: Agentic RAG
# =============================================================================
slide = new_slide(prs)
slide_title(slide, "Agentic RAG: Tools + Retrieval in a Loop")

# Left: concept
card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(5.5), ORANGE_LIGHT, ORANGE, radius=0.05)
header_card(slide, Inches(0.5), Inches(1.1), Inches(5.8), Inches(0.5), "Standard RAG vs Agentic RAG", ORANGE)

add_text(slide, Inches(0.7), Inches(1.72), Inches(5.4), Inches(0.55),
    "Standard RAG: retrieve once, generate once. Fixed pipeline.",
    size=11, bold=False, color=GRAY_DARK)
add_text(slide, Inches(0.7), Inches(2.32), Inches(5.4), Inches(0.55),
    "Agentic RAG: LLM decides which tools to call, in what order, "
    "based on the question. Can call multiple sources, iterate.",
    size=11, bold=False, color=GRAY_DARK)

# 4 tools
tools = [
    ("kb_retrieve", "Vector + Graph KB", "Semantic search on WHO, trials, protocols", ORANGE),
    ("graph_retrieve", "Neptune / AnalyticDB", "Multi-hop entity traversal", ORANGE_DARK),
    ("icd11_lookup", "WHO ICD-11 API", "Live disease classification + synonyms", ORANGE),
    ("pubmed_search", "NCBI E-utilities", "Real-time research literature (query-time)", ORANGE_DARK),
]
for i, (tool_name, source, desc, color) in enumerate(tools):
    y = Inches(3.0 + i * 0.72)
    tc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(0.7), y, Inches(5.2), Inches(0.62))
    tc.fill.solid(); tc.fill.fore_color.rgb = WHITE
    tc.line.color.rgb = color; tc.line.width = Pt(1.5); tc.adjustments[0] = 0.1
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), y, Inches(0.07), Inches(0.62))
    acc.fill.solid(); acc.fill.fore_color.rgb = color; acc.line.fill.background()
    add_text(slide, Inches(0.9), y + Inches(0.05), Inches(1.5), Inches(0.3),
             tool_name, size=10, bold=True, color=color)
    add_text(slide, Inches(0.9), y + Inches(0.33), Inches(1.5), Inches(0.25),
             source, size=9, italic=True, color=GRAY_MED)
    add_text(slide, Inches(2.5), y + Inches(0.15), Inches(3.3), Inches(0.35),
             desc, size=10, color=GRAY_DARK)

# Right: how it works
card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(5.5), WHITE, ORANGE, radius=0.05)
header_card(slide, Inches(6.6), Inches(1.1), Inches(6.2), Inches(0.5), "How Agentic RAG Works (Complex Lane)", ORANGE)

steps_agentic = [
    ("1", "Doctor asks complex question", ORANGE),
    ("2", "Router classifies department", ORANGE_DARK),
    ("3", "Specialty agent receives question", ORANGE),
    ("4", "Agent calls kb_retrieve (vector + graph)", ORANGE_DARK),
    ("5", "Agent optionally calls icd11_lookup for synonyms", ORANGE),
    ("6", "Agent optionally calls pubmed_search for latest evidence", ORANGE_DARK),
    ("7", "Agent synthesizes all results into grounded answer", ORANGE),
    ("8", "Citation validator checks every [n] reference", ORANGE_DARK),
]
for i, (num, step_text, color) in enumerate(steps_agentic):
    y = Inches(1.72 + i * 0.58)
    badge = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(6.8), y, Inches(0.38), Inches(0.38))
    badge.fill.solid(); badge.fill.fore_color.rgb = color; badge.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(6.8), y, Inches(0.38), Inches(0.38))
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = num
    run.font.name = "Calibri"; run.font.size = Pt(10); run.font.bold = True
    run.font.color.rgb = WHITE
    add_text(slide, Inches(7.3), y + Inches(0.04), Inches(5.3), Inches(0.38),
             step_text, size=10.5, color=GRAY_DARK)

print("  Slide 4 (Agentic RAG): done")


# =============================================================================
# SLIDE 5: RAG vs Fine-tuning Comparison (AWS vs Alibaba)
# =============================================================================
slide = new_slide(prs)
slide_title(slide, "RAG vs Fine-tuning: Knowledge Update Strategy")

# Subtitle
add_text(slide, Inches(0.5), Inches(1.0), Inches(12.3), Inches(0.35),
    "How each version handles periodic updates: WHO guidelines, PubMed, clinical trial reports",
    size=12, italic=True, color=GRAY_MED)

# ── Column headers ────────────────────────────────────────────────────────────
# Dimension column
add_text(slide, Inches(0.5), Inches(1.5), Inches(2.5), Inches(0.45),
    "Dimension", size=13, bold=True, color=ORANGE_DARK)
ul = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.95), Inches(2.5), Inches(0.03))
ul.fill.solid(); ul.fill.fore_color.rgb = ORANGE; ul.line.fill.background()

# AWS header
aws_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(3.2), Inches(1.45), Inches(4.5), Inches(0.55))
aws_hdr.fill.solid(); aws_hdr.fill.fore_color.rgb = ORANGE
aws_hdr.line.fill.background(); aws_hdr.adjustments[0] = 0.1
tb = slide.shapes.add_textbox(Inches(3.2), Inches(1.45), Inches(4.5), Inches(0.55))
tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run = p.add_run(); run.text = "AWS with Claude"
run.font.name = "Calibri"; run.font.size = Pt(14); run.font.bold = True
run.font.color.rgb = WHITE

# Alibaba header
ali_hdr = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(8.0), Inches(1.45), Inches(4.8), Inches(0.55))
ali_hdr.fill.solid(); ali_hdr.fill.fore_color.rgb = PURPLE
ali_hdr.line.fill.background(); ali_hdr.adjustments[0] = 0.1
tb = slide.shapes.add_textbox(Inches(8.0), Inches(1.45), Inches(4.8), Inches(0.55))
tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
run = p.add_run(); run.text = "Alibaba Cloud"
run.font.name = "Calibri"; run.font.size = Pt(14); run.font.bold = True
run.font.color.rgb = WHITE

# ── Comparison rows ───────────────────────────────────────────────────────────
rows = [
    (
        "WHO Guidelines\n(monthly update)",
        "RAG only\nEventBridge cron \u2192 S3 \u2192 BDA parse \u2192 Cohere embed \u2192 OpenSearch upsert\nCache invalidated by source tag. No model retrain.",
        "RAG only\nCloudOps Scheduler \u2192 OSS \u2192 DocMind parse \u2192 text-embedding-v4 \u2192 OpenSearch upsert\nTair cache flushed by source tag. No model retrain.",
        GREEN,
    ),
    (
        "PubMed\n(real-time)",
        "RAG tool (query-time)\npubmed_search tool called by agent on demand\nNCBI E-utilities, 24h result cache\nNever ingested into KB",
        "RAG tool (query-time)\npubmed_search tool called by agent on demand\nNCBI E-utilities, 3 req/s free tier\nNever ingested into KB",
        GREEN,
    ),
    (
        "Clinical Trial\nReports (weekly)",
        "RAG only\nSharePoint Graph webhook \u2192 S3 \u2192 PHI mask \u2192 BDA parse\n\u2192 Cohere embed \u2192 OpenSearch upsert\nWeekly reconciliation + real-time webhook",
        "RAG only\nSharePoint Graph webhook \u2192 OSS \u2192 SDDP PHI mask \u2192 DocMind parse\n\u2192 text-embedding-v4 \u2192 OpenSearch upsert\nWeekly reconciliation + real-time webhook",
        GREEN,
    ),
    (
        "Clinical Tone\n& Phrasing",
        "Fine-tuning (quarterly)\nBedrock Model Distillation: Sonnet 4.5 \u2192 Nova Lite student\nSFT on de-identified invocation logs\nStudent serves 40% of complex traffic",
        "Fine-tuning (quarterly)\nPAI SFT + LoRA on Qwen3-8B\nDPO monthly on clinician preference pairs\nGRPO ad-hoc for tool-calling\nStudent serves 60% of complex traffic",
        ORANGE,
    ),
    (
        "ICD-11 Codes\n(daily)",
        "RAG (daily delta)\nEventBridge 02:00 SGT \u2192 WHO OAuth2 API \u2192 S3 \u2192 embed \u2192 upsert\nicd11_lookup tool for query-time expansion",
        "RAG (daily delta)\nCloudOps Scheduler 02:00 SGT \u2192 WHO OAuth2 API \u2192 OSS \u2192 embed \u2192 upsert\nicd11_lookup tool for query-time expansion",
        GREEN,
    ),
]

row_h = Inches(0.88)
start_y = Inches(2.1)

for i, (dim, aws_text, ali_text, indicator) in enumerate(rows):
    y = start_y + i * (row_h + Inches(0.04))
    bg_color = ORANGE_LIGHT if i % 2 == 0 else WHITE

    # Dimension cell
    dim_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), y, Inches(2.5), row_h)
    dim_bg.fill.solid(); dim_bg.fill.fore_color.rgb = bg_color
    dim_bg.line.color.rgb = GRAY_LIGHT; dim_bg.line.width = Pt(0.5)
    add_text(slide, Inches(0.6), y + Inches(0.1), Inches(2.3), row_h - Inches(0.2),
             dim, size=10.5, bold=True, color=GRAY_DARK)

    # AWS cell
    aws_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(3.2), y, Inches(4.5), row_h)
    aws_bg.fill.solid(); aws_bg.fill.fore_color.rgb = bg_color
    aws_bg.line.color.rgb = GRAY_LIGHT; aws_bg.line.width = Pt(0.5)
    add_text(slide, Inches(3.3), y + Inches(0.06), Inches(4.3), row_h - Inches(0.12),
             aws_text, size=9.5, color=GRAY_DARK)

    # Alibaba cell
    ali_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(8.0), y, Inches(4.8), row_h)
    ali_bg.fill.solid(); ali_bg.fill.fore_color.rgb = bg_color
    ali_bg.line.color.rgb = GRAY_LIGHT; ali_bg.line.width = Pt(0.5)
    add_text(slide, Inches(8.1), y + Inches(0.06), Inches(4.6), row_h - Inches(0.12),
             ali_text, size=9.5, color=GRAY_DARK)

    # Indicator dot
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(2.85), y + Inches(0.32), Inches(0.22), Inches(0.22))
    dot.fill.solid(); dot.fill.fore_color.rgb = indicator; dot.line.fill.background()

# Legend
add_text(slide, Inches(0.5), Inches(6.65), Inches(12.3), Inches(0.35),
    "\u25cf Green = RAG (no model retrain, updates in minutes-hours)   "
    "\u25cf Orange = Fine-tuning (tone/format only, quarterly, ~$15-40/run)",
    size=10, color=GRAY_MED, align=PP_ALIGN.CENTER)

# Key insight box
insight = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(7.0), Inches(12.3), Inches(0.38))
insight.fill.solid(); insight.fill.fore_color.rgb = ORANGE
insight.line.fill.background(); insight.adjustments[0] = 0.2
add_text(slide, Inches(0.7), Inches(7.04), Inches(11.9), Inches(0.32),
    "Key insight: RAG handles all factual updates (WHO, PubMed, trials). "
    "Fine-tuning is ONLY for tone, phrasing, and clinical vocabulary. Never for facts.",
    size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

print("  Slide 5 (RAG vs Fine-tuning): done")

# =============================================================================
# Save
# =============================================================================
out = "docs/Technology_Explanation_Slides.pptx"
prs.save(out)
size = Path(out).stat().st_size
print(f"\nSaved: {out}  ({size:,} bytes)")
print(f"Total slides: {len(prs.slides)}")
