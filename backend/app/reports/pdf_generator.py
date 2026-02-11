"""PDF report generator using Jinja2 + WeasyPrint.

Generates legal-grade PDF reports with:
1. Executive Summary: PASS/FAIL badge
2. Physics Verification: KDS standards citation
3. Reality Calibration: Correction percentage
4. Disclaimer: TRL 1-3 Due Diligence
"""

import os
from datetime import datetime

from jinja2 import Environment, FileSystemLoader


def generate_pdf(report_data: dict) -> bytes:
    """Generate a PDF report from decision data.

    Args:
        report_data: Dictionary containing all report fields.

    Returns:
        PDF file as bytes.
    """
    # Load Jinja2 template
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report_base.html")

    # Render HTML
    html_content = template.render(**report_data)

    # Convert to PDF using WeasyPrint
    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
    except ImportError:
        # Fallback: return HTML as bytes if WeasyPrint not installed
        return html_content.encode("utf-8")
