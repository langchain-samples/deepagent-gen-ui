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
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

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
def generate_pdf_report(data: dict, report_title: str = "Report", description: str = "") -> dict:
    """
    Generate a PDF report from the provided data and display it in the UI.
    
    Args:
        data: Dictionary containing the data to include in the report
        report_title: Title for the report
        description: Optional description for the report
    
    Returns:
        Dictionary with PDF file data (base64 encoded)
    """
    # Create PDF buffer
    pdf_buffer = io.BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Add title
    title = Paragraph(f"<b>{report_title}</b>", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Add description if provided
    if description:
        desc = Paragraph(description, styles['Normal'])
        elements.append(desc)
        elements.append(Spacer(1, 0.2 * inch))
    
    # Add generation date
    date_text = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
    elements.append(date_text)
    elements.append(Spacer(1, 0.3 * inch))
    
    # Prepare table data from dict
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
        
        # Build table data: headers + rows
        table_data = [headers]
        for row_idx in range(max_length):
            row = [str(val_list[row_idx]) for val_list in values_lists]
            table_data.append(row)
        
        num_rows = max_length
    else:
        # Simple fallback
        table_data = [["Data"], [str(data)]]
        num_rows = 1
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
    ]))
    
    elements.append(table)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes and encode to base64
    pdf_bytes = pdf_buffer.getvalue()
    pdf_base64 = base64.b64encode(pdf_bytes).decode()
    
    # Generate filename
    filename = f"{report_title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    # Return data - middleware will handle UI message
    return {
        "data": pdf_base64,
        "filename": filename,
        "pages": 1,
        "rows": num_rows
    }

@tool
def search_movies(query: str) -> dict:
    """
    Search for movies based on a query and return a list of movies.
    
    Args:
        query: The query to search for
    """
    return {"best_movies": ["The Matrix", "The Dark Knight", "The Lord of the Rings: The Return of the King"]}


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
    tools=[generate_csv_report, generate_pdf_report, search_movies],
    subagents=[research_subagent],
    middleware=[genui_middleware],
    system_prompt="""You are a helpful reporting assistant that generates CSV and PDF reports for users.

You can:
- Delegate to the research-specialist subagent to retrieve sales data and user analytics
- Search for movies based on a query using the search_movies() tool
- Generate CSV reports with tabular data (viewable in an interactive table)
- Generate PDF reports with formatted tables (with preview and download)

When a user asks for a report:
1. Determine what type of data they need (sales, analytics, etc.)
2. Delegate to the research-specialist subagent to fetch the data
3. Once you receive the data from the subagent, use generate_csv_report() or generate_pdf_report() with the data
4. The report will automatically display with preview and download options

Be conversational and helpful. When the report is generated, let the user know what's included and highlight any interesting insights from the data."""
)
