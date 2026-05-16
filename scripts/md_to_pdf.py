"""Convert markdown Q&A files to PDF using ReportLab."""
import re
import pathlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Colors
ORANGE = HexColor('#FF6B35')
ORANGE_DARK = HexColor('#CC4F1F')
ORANGE_LIGHT = HexColor('#FFE8DA')
GRAY_DARK = HexColor('#2C3E50')
GRAY_MED = HexColor('#646464')
GRAY_LIGHT = HexColor('#F5F5F5')

def build_styles():
    styles = getSampleStyleSheet()
    custom = {
        'Title': ParagraphStyle('Title', fontName='Helvetica-Bold', fontSize=22,
            textColor=ORANGE_DARK, spaceAfter=6, alignment=TA_CENTER),
        'Subtitle': ParagraphStyle('Subtitle', fontName='Helvetica', fontSize=13,
            textColor=GRAY_MED, spaceAfter=12, alignment=TA_CENTER),
        'H1': ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=16,
            textColor=ORANGE_DARK, spaceBefore=18, spaceAfter=6,
            borderPad=4, backColor=ORANGE_LIGHT,
            leftIndent=0, rightIndent=0),
        'H2': ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=13,
            textColor=ORANGE_DARK, spaceBefore=14, spaceAfter=4),
        'H3': ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=11,
            textColor=ORANGE_DARK, spaceBefore=10, spaceAfter=3),
        'Q': ParagraphStyle('Q', fontName='Helvetica-Bold', fontSize=10.5,
            textColor=GRAY_DARK, spaceBefore=8, spaceAfter=2,
            leftIndent=0),
        'A_label': ParagraphStyle('A_label', fontName='Helvetica-Bold', fontSize=10,
            textColor=ORANGE, spaceBefore=2, spaceAfter=1),
        'Body': ParagraphStyle('Body', fontName='Helvetica', fontSize=9.5,
            textColor=GRAY_DARK, spaceAfter=4, leading=14,
            alignment=TA_JUSTIFY),
        'Code': ParagraphStyle('Code', fontName='Courier', fontSize=8.5,
            textColor=GRAY_DARK, backColor=GRAY_LIGHT,
            leftIndent=12, rightIndent=12, spaceBefore=4, spaceAfter=4,
            leading=12),
        'Bullet': ParagraphStyle('Bullet', fontName='Helvetica', fontSize=9.5,
            textColor=GRAY_DARK, leftIndent=16, spaceAfter=2, leading=13),
        'HR': ParagraphStyle('HR', spaceBefore=4, spaceAfter=4),
        'TOC': ParagraphStyle('TOC', fontName='Helvetica', fontSize=9.5,
            textColor=GRAY_DARK, leftIndent=8, spaceAfter=2),
    }
    return custom

def escape_xml(text):
    """Escape XML special chars for ReportLab."""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def parse_inline(text):
    """Convert inline markdown to ReportLab XML."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    # Code
    text = re.sub(r'`(.+?)`', r'<font name="Courier" size="8">\1</font>', text)
    return text

def md_to_flowables(md_text, styles):
    """Convert markdown text to ReportLab flowables."""
    flowables = []
    lines = md_text.split('\n')
    i = 0
    in_code = False
    code_lines = []
    
    while i < len(lines):
        line = lines[i]
        
        # Code block
        if line.strip().startswith('```'):
            if not in_code:
                in_code = True
                code_lines = []
            else:
                in_code = False
                code_text = '\n'.join(code_lines)
                code_text = escape_xml(code_text)
                # Split into lines for display
                for cl in code_text.split('\n'):
                    if cl.strip():
                        flowables.append(Paragraph(cl, styles['Code']))
                flowables.append(Spacer(1, 4))
                code_lines = []
            i += 1
            continue
        
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        
        # Headings
        if line.startswith('# ') and not line.startswith('## '):
            text = escape_xml(line[2:].strip())
            text = parse_inline(text)
            flowables.append(Paragraph(text, styles['Title']))
            i += 1
            continue
        
        if line.startswith('## ') and not line.startswith('### '):
            text = escape_xml(line[3:].strip())
            text = parse_inline(text)
            flowables.append(Spacer(1, 8))
            flowables.append(HRFlowable(width='100%', thickness=2, color=ORANGE))
            flowables.append(Paragraph(text, styles['H1']))
            i += 1
            continue
        
        if line.startswith('### '):
            text = escape_xml(line[4:].strip())
            text = parse_inline(text)
            # Check if it's a Q line
            if re.match(r'Q\d+\.', text):
                flowables.append(Paragraph(text, styles['Q']))
            else:
                flowables.append(Paragraph(text, styles['H2']))
            i += 1
            continue
        
        if line.startswith('#### '):
            text = escape_xml(line[5:].strip())
            text = parse_inline(text)
            flowables.append(Paragraph(text, styles['H3']))
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            flowables.append(HRFlowable(width='100%', thickness=0.5, color=ORANGE_LIGHT))
            flowables.append(Spacer(1, 2))
            i += 1
            continue
        
        # Table
        if line.strip().startswith('|'):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i])
                i += 1
            # Parse table
            rows = []
            for tl in table_lines:
                if re.match(r'\|[-: |]+\|', tl):
                    continue  # separator row
                cells = [c.strip() for c in tl.strip('|').split('|')]
                rows.append(cells)
            if rows:
                # Build table
                max_cols = max(len(r) for r in rows)
                # Pad rows
                rows = [r + [''] * (max_cols - len(r)) for r in rows]
                # Convert to paragraphs
                table_data = []
                for ri, row in enumerate(rows):
                    table_row = []
                    for ci, cell in enumerate(row):
                        cell_text = escape_xml(cell)
                        cell_text = parse_inline(cell_text)
                        if ri == 0:
                            p = Paragraph(cell_text, ParagraphStyle('TC',
                                fontName='Helvetica-Bold', fontSize=8.5,
                                textColor=white, alignment=TA_CENTER))
                        else:
                            p = Paragraph(cell_text, ParagraphStyle('TB',
                                fontName='Helvetica', fontSize=8.5,
                                textColor=GRAY_DARK))
                        table_row.append(p)
                    table_data.append(table_row)
                
                col_width = (A4[0] - 3*cm) / max_cols
                t = Table(table_data, colWidths=[col_width]*max_cols,
                         repeatRows=1)
                ts = TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), ORANGE),
                    ('TEXTCOLOR', (0,0), (-1,0), white),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, ORANGE_LIGHT]),
                    ('GRID', (0,0), (-1,-1), 0.5, ORANGE_LIGHT),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('TOPPADDING', (0,0), (-1,-1), 4),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 4),
                    ('LEFTPADDING', (0,0), (-1,-1), 6),
                    ('RIGHTPADDING', (0,0), (-1,-1), 6),
                ])
                t.setStyle(ts)
                flowables.append(t)
                flowables.append(Spacer(1, 6))
            continue
        
        # Bullet list
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            text = escape_xml(line.strip()[2:])
            text = parse_inline(text)
            flowables.append(Paragraph(u'\u2022 ' + text, styles['Bullet']))
            i += 1
            continue
        
        # Numbered list
        m = re.match(r'^(\d+)\.\s+(.+)', line.strip())
        if m:
            text = escape_xml(m.group(2))
            text = parse_inline(text)
            flowables.append(Paragraph(f'{m.group(1)}. {text}', styles['Bullet']))
            i += 1
            continue
        
        # **A.** answer label
        if line.strip().startswith('**A.**'):
            rest = line.strip()[6:].strip()
            flowables.append(Paragraph('<b>A.</b>', styles['A_label']))
            if rest:
                rest = escape_xml(rest)
                rest = parse_inline(rest)
                flowables.append(Paragraph(rest, styles['Body']))
            i += 1
            continue
        
        # Blockquote
        if line.strip().startswith('> '):
            text = escape_xml(line.strip()[2:])
            text = parse_inline(text)
            flowables.append(Paragraph(text, ParagraphStyle('BQ',
                fontName='Helvetica-Oblique', fontSize=9,
                textColor=GRAY_MED, leftIndent=20, spaceAfter=3)))
            i += 1
            continue
        
        # Empty line
        if not line.strip():
            flowables.append(Spacer(1, 3))
            i += 1
            continue
        
        # Regular paragraph
        text = escape_xml(line.strip())
        text = parse_inline(text)
        if text:
            flowables.append(Paragraph(text, styles['Body']))
        i += 1
    
    return flowables


def add_page_number(canvas, doc):
    """Add page number footer."""
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(GRAY_MED)
    page_num = canvas.getPageNumber()
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f'Nova Health Tech · Clinical GenAI Assistant · Page {page_num}')
    canvas.setStrokeColor(ORANGE_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(1.5*cm, 1.5*cm, A4[0]-1.5*cm, 1.5*cm)
    canvas.restoreState()


def convert_md_to_pdf(md_path, pdf_path, title):
    print(f'Converting {md_path} -> {pdf_path}')
    
    md_text = pathlib.Path(md_path).read_text(encoding='utf-8')
    styles = build_styles()
    
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        leftMargin=1.5*cm,
        rightMargin=1.5*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=title,
        author='Nova Health Tech',
        subject='Clinical GenAI Assistant',
    )
    
    flowables = md_to_flowables(md_text, styles)
    
    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    size = pathlib.Path(pdf_path).stat().st_size
    print(f'  Done: {size:,} bytes ({size//1024} KB)')


# Convert both files
convert_md_to_pdf(
    'docs/Client_QA_500_Questions.md',
    'docs/Client_QA_500_Questions.pdf',
    'Nova Health Tech - 500 Client Q&A (English)'
)

convert_md_to_pdf(
    'docs/Client_QA_500_Tieng_Viet.md',
    'docs/Client_QA_500_Tieng_Viet.pdf',
    'Nova Health Tech - 500 Cau hoi & Tra loi (Tieng Viet)'
)

print('All done.')
