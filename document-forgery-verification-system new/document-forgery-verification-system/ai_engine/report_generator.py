from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Table
import datetime
import os

def generate_report(output_path, filename, status, confidence, ela_score, extracted_text):

    doc = SimpleDocTemplate(output_path)
    elements = []

    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>Document Verification Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Document Name:", filename],
        ["Verification Status:", status],
        ["Confidence:", f"{confidence}%"],
        ["ELA Score:", str(ela_score)],
        ["Generated On:", str(datetime.datetime.now())]
    ]

    table = Table(data)
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(Paragraph("<b>Extracted Text Preview:</b>", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(extracted_text[:1000], styles["Normal"]))

    doc.build(elements)