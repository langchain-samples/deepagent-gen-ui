"""
Report Generation DeepAgent

A supervisor agent that uses a research subagent to fetch data, then generates 
CSV and PDF reports with the data. The generated reports are displayed in the 
frontend using LangGraph's Generative UI.
"""

import base64
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, 
    PageBreak, KeepTogether, ListFlowable, ListItem
)

from langchain.tools import tool

from deepagents import create_deep_agent
from subagents import research_subagent
from ui_middleware import GenUIMiddleware


# =============================================================================
# UI GENERATION TOOLS
# =============================================================================

@tool
def generate_csv_report(data: dict, report_title: str = "Report") -> dict:
    """
    Generate a CSV report from the provided data and display it in the UI.
    
    Args:
        data: Dictionary containing the data to include in the report
        report_title: Title for the report file
    
    Returns:
        Dictionary with CSV file data (base64 encoded)
    """
    # Simple CSV generation without pandas
    csv_buffer = io.StringIO()
    
    # Handle dict data - get headers and values
    if isinstance(data, dict):
        headers = list(data.keys())
        
        # Get all values and ensure they're lists
        values_lists = []
        max_length = 0
        for key in headers:
            val = data[key]
            if isinstance(val, (list, tuple)):
                values_lists.append(list(val))
                max_length = max(max_length, len(val))
            else:
                values_lists.append([val])
                max_length = max(max_length, 1)
        
        # Pad shorter lists with empty strings
        for val_list in values_lists:
            while len(val_list) < max_length:
                val_list.append("")
        
        # Write headers
        csv_buffer.write(",".join(headers) + "\n")
        
        # Write rows
        for row_idx in range(max_length):
            row_values = [str(val_list[row_idx]) for val_list in values_lists]
            csv_buffer.write(",".join(row_values) + "\n")
        
        num_rows = max_length
        num_columns = len(headers)
    else:
        # Fallback for other data types
        csv_buffer.write("data\n")
        csv_buffer.write(str(data) + "\n")
        num_rows = 1
        num_columns = 1
        headers = ["data"]
    
    csv_string = csv_buffer.getvalue()
    
    # Encode to base64
    csv_base64 = base64.b64encode(csv_string.encode()).decode()
    
    # Generate filename
    filename = f"{report_title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.csv"
    
    # Return data - middleware will handle UI message
    return {
        "data": csv_base64,
        "filename": filename,
        "rows": num_rows,
        "columns": headers
    }


@tool
def generate_pdf_report(
    content: str | dict, 
    report_title: str = "Report", 
    subtitle: str = ""
) -> dict:
    """
    Generate a beautiful, professionally formatted PDF report with rich formatting and display it in the UI.
    
    🎨 VISUAL CAPABILITIES:
    This tool creates stunning, publication-quality PDFs with:
    - Professional header with centered title and subtitle
    - Color-coded section headers (blue) and subsections  
    - Well-formatted data tables with alternating row colors and borders
    - Automatic text formatting: bold, colored metrics ($, %), bullet lists
    - Proper spacing, margins, and typography for readability
    - Multi-page support with consistent styling
    
    📊 BEST USE CASES:
    - Business reports with multiple data sections (sales, analytics, metrics)
    - Executive summaries with key findings and tables
    - Data analysis reports combining narrative and tabular data
    - Multi-section reports (e.g., "Sales Report", "User Analytics", "Insights")
    - Any structured data that needs professional presentation
    
    📝 CONTENT FORMATTING GUIDE:
    
    For TEXT content (recommended - most flexible):
    - Use "SECTION N: Title" or "### Title" for major section headers (renders in blue, larger font)
    - Lines ending with ":" become subsection headers (e.g., "Key Findings:")
    - Create tables using pipe-separated format:
        | Header1 | Header2 | Header3 |
        | Value1  | Value2  | Value3  |
    - Use "-", "•", or "*" at line start for bullet points
    - Dollar amounts ($123,456) are automatically highlighted in green and bold
    - Percentages (45.2%) are automatically highlighted in purple and bold
    - Use **text** for bold emphasis
    - Trend arrows (↗↘) are automatically colored (green/red)
    - Empty lines create natural spacing between sections
    
    For DICT content (structured data):
    - Simple dicts become key-value tables automatically
    - For complex reports: {"sections": [{"title": "...", "content": "...", "table": [...]}]}
    
    ✨ FORMATTING TIPS:
    - Organize content with clear section headers for multi-topic reports
    - Keep table columns to 5-6 max for best readability
    - Use subsection headers (lines ending with ":") to organize metrics
    - Add context text between tables to tell the story of the data
    - Combine narrative insights with data tables for comprehensive reports
    
    Args:
        content: The report content. Can be:
                 1. Formatted text string with sections, tables, and metrics (RECOMMENDED)
                    Example: "SECTION 1: Sales Metrics\\n\\nMonthly Performance:\\n\\n| Month | Revenue | Units |\\n| Jan | $15,000 | 150 |\\n\\nKey Insight: Strong growth in Q1.\\n\\nSECTION 2: User Analytics\\n\\n| Date | Users |\\n| 2024-01 | 1,250 |"
                 2. Structured dictionary with sections
                    Example: {"sections": [{"title": "Sales", "content": "...", "table": [[...], [...]]}]}
                 3. Simple dict for quick key-value reports (auto-converts to table)
        
        report_title: Main title displayed at top of PDF (large, bold, centered)
                     Example: "Q4 2024 Business Performance Report"
        
        subtitle: Optional subtitle/description under the title (smaller, italic, centered)
                 Example: "Comprehensive Analysis of Sales and User Engagement"
    
    Returns:
        Dictionary with PDF file data (base64 encoded), filename, page count, and metadata.
        The PDF is automatically displayed in the UI for immediate viewing/download.
    
    💡 USAGE EXAMPLES:
    
    Example 1 - Multi-section business report:
        generate_pdf_report(
            content=\"\"\"SECTION 1: SALES METRICS
            
            Monthly Sales Summary:
            
            | Date | Product | Revenue | Units |
            | 2024-01 | Widget A | $15,000 | 150 |
            | 2024-02 | Widget B | $23,000 | 230 |
            
            Key Findings:
            - Total Revenue: $97,000
            - Top Product: Widget B ($42,500)
            - Growth Rate: 28% YoY
            
            SECTION 2: USER ANALYTICS
            
            Engagement Metrics:
            
            | Date | Active Users | Retention |
            | 2024-10 | 1,250 | 78.5% |
            | 2024-11 | 1,600 | 82.1% |
            
            Insights:
            - User growth: ↗ 350 users (+28%)
            - Retention improved: 78.5% → 82.1%
            \"\"\",
            report_title="Sales and User Analytics Report 2024",
            subtitle="Comprehensive Business Performance Analysis"
        )
    
    Example 2 - Simple metrics report:
        generate_pdf_report(
            content=\"\"\"Performance Summary:
            
            - Revenue: $1.2M (↗ 15%)
            - Active Users: 45,234 
            - Conversion Rate: 3.8%
            - Customer Satisfaction: 92%
            \"\"\",
            report_title="Monthly Performance Dashboard"
        )
    
    Example 3 - Quick dict-to-table:
        generate_pdf_report(
            content={"Revenue": "$1.2M", "Users": 45234, "Conversion": "3.8%"},
            report_title="Quick Metrics"
        )
    """
    # Create PDF buffer and document
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Create custom styles
    styles = getSampleStyleSheet()
    
    # Title style - larger, bold, centered
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Subtitle style
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#4a4a4a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Section header style - bold, larger, with color
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=12,
        spaceBefore=16,
        fontName='Helvetica-Bold',
        borderWidth=0,
        borderPadding=0,
        leftIndent=0,
        borderColor=colors.HexColor('#2563eb'),
        borderRadius=0
    )
    
    # Subsection style
    subsection_style = ParagraphStyle(
        'Subsection',
        parent=styles['Heading2'],
        fontSize=13,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Body text style
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=6,
        leading=14
    )
    
    # Metrics style (for key numbers)
    metric_style = ParagraphStyle(
        'Metric',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#059669'),
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    
    elements = []
    
    # Add title
    elements.append(Paragraph(report_title, title_style))
    
    # Add subtitle if provided
    if subtitle:
        elements.append(Paragraph(subtitle, subtitle_style))
    else:
        elements.append(Spacer(1, 0.2*inch))
    
    # Add generation date
    date_str = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    date_para = Paragraph(
        f'<i>Generated: {date_str}</i>', 
        ParagraphStyle('date', parent=body_style, fontSize=9, textColor=colors.grey, alignment=TA_CENTER)
    )
    elements.append(date_para)
    elements.append(Spacer(1, 0.3*inch))
    
    # Parse and format content
    if isinstance(content, str):
        elements.extend(_parse_text_content(content, section_style, subsection_style, body_style, metric_style))
    elif isinstance(content, dict):
        elements.extend(_parse_dict_content(content, section_style, subsection_style, body_style, metric_style))
    else:
        elements.append(Paragraph(str(content), body_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes and encode to base64
    pdf_bytes = pdf_buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_bytes).decode()
    
    # Generate filename
    filename = f"{report_title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    
    # Count pages estimate (rough)
    page_estimate = max(1, len(elements) // 20)
    
    return {
        "data": pdf_base64,
        "filename": filename,
        "pages": page_estimate,
        "rows": len(elements)
    }


def _parse_text_content(text: str, section_style, subsection_style, body_style, metric_style) -> list:
    """Parse formatted text content into PDF elements."""
    elements = []
    lines = text.strip().split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines (but add small spacer)
        if not line:
            i += 1
            continue
        
        # Check for section headers (SECTION X: or ###)
        if line.startswith('SECTION ') or line.startswith('###'):
            # Remove markdown symbols and emoji
            clean_line = line.replace('###', '').replace('📊', '').replace('SECTION ', 'SECTION ').strip()
            elements.append(Spacer(1, 0.15*inch))
            elements.append(Paragraph(clean_line, section_style))
            i += 1
            continue
        
        # Check for subsection (ends with colon, often bold in original)
        if line.endswith(':') and len(line) < 80 and not '|' in line:
            clean_line = line.replace('**', '').strip()
            elements.append(Paragraph(clean_line, subsection_style))
            i += 1
            continue
        
        # Check for table (contains pipe separators)
        if '|' in line:
            # Parse table
            table_lines = [line]
            i += 1
            # Collect all consecutive table lines
            while i < len(lines) and '|' in lines[i]:
                table_lines.append(lines[i].strip())
                i += 1
            
            # Create table
            table_element = _create_table_from_lines(table_lines)
            if table_element:
                elements.append(Spacer(1, 0.1*inch))
                elements.append(table_element)
                elements.append(Spacer(1, 0.15*inch))
            continue
        
        # Check for bullet points
        if line.startswith(('•', '-', '*', '✓')) and not line.startswith('---'):
            # Clean bullet and add as list item
            clean_line = line[1:].strip()
            if line.startswith('-') and len(line) > 2 and line[1] == ' ':
                clean_line = line[2:].strip()
            
            # Format metrics and bold text
            formatted_line = _format_inline_text(clean_line)
            bullet_para = Paragraph(f"• {formatted_line}", body_style)
            elements.append(bullet_para)
            i += 1
            continue
        
        # Regular paragraph - format inline text
        formatted_line = _format_inline_text(line)
        elements.append(Paragraph(formatted_line, body_style))
        i += 1
    
    return elements


def _parse_dict_content(data: dict, section_style, subsection_style, body_style, metric_style) -> list:
    """Parse dictionary content into PDF elements."""
    elements = []
    
    # Handle different dict structures
    if 'sections' in data:
        for section in data['sections']:
            if isinstance(section, dict):
                if 'title' in section:
                    elements.append(Paragraph(section['title'], section_style))
                if 'content' in section:
                    if isinstance(section['content'], str):
                        elements.extend(_parse_text_content(
                            section['content'], section_style, subsection_style, body_style, metric_style
                        ))
                    elif isinstance(section['content'], list):
                        for item in section['content']:
                            elements.append(Paragraph(str(item), body_style))
                if 'table' in section:
                    table = _create_table_from_data(section['table'])
                    if table:
                        elements.append(table)
    else:
        # Simple dict - convert to key-value table
        table_data = [['Key', 'Value']]
        for key, value in data.items():
            table_data.append([str(key), str(value)])
        
        table = Table(table_data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(_get_table_style())
        elements.append(table)
    
    return elements


def _create_table_from_lines(lines: list) -> Table:
    """Create a formatted table from text lines with pipe separators."""
    if not lines:
        return None
    
    # Parse table data
    table_data = []
    for line in lines:
        # Split by pipe and clean
        cells = [cell.strip() for cell in line.split('|')]
        # Remove empty first/last cells (from leading/trailing pipes)
        cells = [c for c in cells if c]
        
        # Skip separator lines (-----)
        if cells and all(set(cell.strip()) <= {'-', ' '} for cell in cells):
            continue
        
        if cells:
            table_data.append(cells)
    
    if not table_data or len(table_data) < 2:
        return None
    
    # Calculate column widths dynamically
    num_cols = len(table_data[0])
    available_width = 6.5 * inch
    col_width = available_width / num_cols
    col_widths = [col_width] * num_cols
    
    # Create table with styling
    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(_get_table_style())
    
    return table


def _create_table_from_data(data) -> Table:
    """Create a table from structured data."""
    if isinstance(data, list) and data:
        # Assume list of lists or list of dicts
        if isinstance(data[0], dict):
            # Convert list of dicts to table
            headers = list(data[0].keys())
            table_data = [headers]
            for row in data:
                table_data.append([str(row.get(h, '')) for h in headers])
        else:
            table_data = data
        
        table = Table(table_data, repeatRows=1)
        table.setStyle(_get_table_style())
        return table
    
    return None


def _get_table_style() -> TableStyle:
    """Get consistent table styling."""
    return TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 1), (-1, -1), 6),
        ('RIGHTPADDING', (0, 1), (-1, -1), 6),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f9ff')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1e40af')),
        
        # Valign
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])


def _format_inline_text(text: str) -> str:
    """Format inline text with bold, colors for metrics, etc."""
    # Remove emoji (they don't render well in ReportLab)
    text = ''.join(char for char in text if ord(char) < 0x1F600 or ord(char) > 0x1F64F)
    text = ''.join(char for char in text if ord(char) < 0x1F300 or ord(char) > 0x1F5FF)
    text = ''.join(char for char in text if ord(char) < 0x1F680 or ord(char) > 0x1F6FF)
    text = ''.join(char for char in text if ord(char) < 0x2600 or ord(char) > 0x26FF)
    
    # Convert markdown bold to HTML bold
    import re
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    
    # Highlight dollar amounts
    text = re.sub(r'\$([0-9,]+)', r'<b><font color="#059669">$\1</font></b>', text)
    
    # Highlight percentages
    text = re.sub(r'(\d+\.?\d*%)', r'<b><font color="#7c3aed">\1</font></b>', text)
    
    # Highlight arrows (trend indicators)
    text = text.replace('↗', '<font color="#059669">↗</font>')
    text = text.replace('↘', '<font color="#dc2626">↘</font>')
    
    return text

# =============================================================================
# SUPERVISOR AGENT
# =============================================================================

# Create GenUI middleware with tool-to-component mapping
genui_middleware = GenUIMiddleware(
    tool_to_genui_map={
        "generate_csv_report": {"component_name": "csv_preview"},
        "generate_pdf_report": {"component_name": "pdf_preview"}
    }
)

graph = create_deep_agent(
    model="anthropic:claude-haiku-4-5",
    tools=[generate_csv_report, generate_pdf_report],
    subagents=[research_subagent],
    middleware=[genui_middleware],
    system_prompt="""You are a helpful reporting assistant that generates CSV and PDF reports for users.

You can:
- Delegate to the research-specialist subagent to retrieve sales data and user analytics
- Generate CSV reports with tabular data (viewable in an interactive table)
- Generate PDF reports with formatted tables (with preview and download)

When a user asks for a report:
1. Determine what type of data they need (sales, analytics, etc.)
2. Delegate to the research-specialist subagent to fetch the data
3. Once you receive the data from the subagent, use generate_csv_report() or generate_pdf_report() with the data
4. The report will automatically display with preview and download options in the UI

Be conversational and helpful. When the report is generated, let the user know what's included and highlight any interesting insights from the data."""
)
