# =============================================================================
# SLIDE 6: LangChain + LangGraph in the PoC
# =============================================================================
slide = new_slide(prs)
slide_title(slide, 'LangChain + LangGraph in the PoC')

BLUE         = RGBColor(0x21, 0x96, 0xF3)
BLUE_LIGHT   = RGBColor(0xE3, 0xF2, 0xFD)
PURPLE       = RGBColor(0x7B, 0x1F, 0xA2)
PURPLE_LIGHT = RGBColor(0xF3, 0xE5, 0xF5)

lg_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(1.1), Inches(6.0), Inches(3.2))
bordered(lg_card, BLUE_LIGHT, BLUE, line_pt=2)
lg_hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(1.1), Inches(6.0), Inches(0.5))
solid(lg_hdr, BLUE)
add_text(slide, Inches(0.5), Inches(1.1), Inches(6.0), Inches(0.5),
         'LangGraph  -  State Machine Orchestration', size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text(slide, Inches(0.7), Inches(1.72), Inches(5.6), Inches(0.45),
         'Defines the request pipeline as a directed graph of nodes + edges. '
         'Each node is a processing step; edges are conditional transitions.',
         size=10.5, color=GRAY_DARK)

code_bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.7), Inches(2.25), Inches(5.6), Inches(1.8))
bordered(code_bg, RGBColor(0xF5, 0xF5, 0xF5), GRAY_LIGHT, line_pt=0.75, radius=0.0)

code_lines = [
    'from langgraph.graph import END, StateGraph',
    '',
    'g = StateGraph(ChatState)',
    'g.add_node("phi_mask",  _node_phi_mask)',
    'g.add_node("pick_lane", _node_pick_lane)',
    'g.add_node("retrieve",  _node_retrieve)',
    'g.add_node("generate",  _node_generate)',
    'g.add_conditional_edges("cache_lookup",',
    '    _branch_on_lane,',
    '    {"emergency": "emergency_agent",',
    '     "complex":   "route_department"})',
    'graph = g.compile()',
]
for i, line in enumerate(code_lines):
    tb = slide.shapes.add_textbox(Inches(0.85), Inches(2.32 + i * 0.13), Inches(5.3), Inches(0.14))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    run = p.add_run(); run.text = line
    run.font.name = 'Courier New'; run.font.size = Pt(8.5)
    run.font.color.rgb = BLUE if (line.startswith('from') or line.startswith('g.') or line.startswith('graph')) else GRAY_DARK

lc_card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(6.8), Inches(1.1), Inches(6.0), Inches(3.2))
bordered(lc_card, PURPLE_LIGHT, PURPLE, line_pt=2)
lc_hdr = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.1), Inches(6.0), Inches(0.5))
solid(lc_hdr, PURPLE)
add_text(slide, Inches(6.8), Inches(1.1), Inches(6.0), Inches(0.5),
         'LangChain  -  Text Splitting + Cache', size=14, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

add_text(slide, Inches(7.0), Inches(1.72), Inches(5.6), Inches(0.45),
         'Used for two specific utilities: semantic text splitting during ingestion, '
         'and the Redis semantic cache layer.',
         size=10.5, color=GRAY_DARK)

lc_items = [
    ('langchain-text-splitters',
     'SemanticChunker for clinical trial PDFs\n(max 512 tokens, 80th percentile breakpoint)'),
    ('langchain-community',
     'Redis cache integration (SHA-256 key in PoC,\nvector similarity in production)'),
    ('langchain-core',
     'Base types and interfaces used by LangGraph'),
]
for i, (pkg, desc) in enumerate(lc_items):
    y = Inches(2.28 + i * 0.65)
    pkg_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.0), y, Inches(5.6), Inches(0.58))
    bordered(pkg_bg, WHITE, PURPLE, line_pt=1.2, radius=0.08)
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(7.0), y, Inches(0.06), Inches(0.58))
    solid(acc, PURPLE)
    add_text(slide, Inches(7.15), y + Inches(0.04), Inches(2.0), Inches(0.25),
             pkg, size=9.5, bold=True, color=PURPLE)
    add_text(slide, Inches(7.15), y + Inches(0.28), Inches(5.3), Inches(0.28),
             desc, size=9, italic=True, color=GRAY_DARK)

flow_bg = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(4.45), Inches(12.3), Inches(2.1))
bordered(flow_bg, ORANGE_LIGHT, ORANGE, line_pt=1.5)
add_text(slide, Inches(0.7), Inches(4.52), Inches(12.0), Inches(0.38),
         'LangGraph State Machine: Full Node Graph (PoC)', size=13, bold=True, color=ORANGE_DARK)

nodes = [
    ('phi_mask',        Inches(0.65),  Inches(5.0),  ORANGE),
    ('pick_lane',       Inches(2.05),  Inches(5.0),  ORANGE),
    ('cache_lookup',    Inches(3.45),  Inches(5.0),  ORANGE),
    ('emergency_agent', Inches(2.05),  Inches(5.72), BLUE),
    ('route_dept',      Inches(4.85),  Inches(5.72), BLUE),
    ('retrieve',        Inches(6.25),  Inches(5.0),  GREEN),
    ('generate',        Inches(7.85),  Inches(5.0),  GREEN),
    ('cache_write',     Inches(9.45),  Inches(5.0),  ORANGE),
    ('END',             Inches(11.05), Inches(5.0),  GRAY_MED),
]
node_w = Inches(1.25); node_h = Inches(0.45)
for name, nx, ny, color in nodes:
    n = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, nx, ny, node_w, node_h)
    n.fill.solid(); n.fill.fore_color.rgb = color; n.line.fill.background()
    n.adjustments[0] = 0.15
    tb = slide.shapes.add_textbox(nx, ny, node_w, node_h)
    tf = tb.text_frame; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    run = p.add_run(); run.text = name
    run.font.name = 'Courier New'; run.font.size = Pt(8.5)
    run.font.bold = True; run.font.color.rgb = WHITE

add_text(slide, Inches(3.45), Inches(5.5), Inches(1.5), Inches(0.22),
         'emergency', size=8, italic=True, color=BLUE)
add_text(slide, Inches(3.45), Inches(5.65), Inches(1.5), Inches(0.22),
         'complex', size=8, italic=True, color=BLUE)

note = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(0.5), Inches(6.65), Inches(12.3), Inches(0.38))
solid(note, ORANGE); note.adjustments[0] = 0.2
add_text(slide, Inches(0.7), Inches(6.69), Inches(11.9), Inches(0.32),
         'LangGraph = orchestration (state machine).  '
         'LangChain = utilities (text splitting, cache).  '
         'Neither replaces Bedrock Agents for tool calling.',
         size=11, bold=True, color=WHITE, align=PP_ALIGN.CENTER)

print('  Slide 6 (LangChain + LangGraph): done')
