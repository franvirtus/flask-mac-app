from fpdf import FPDF
from datetime import datetime
import os
import base64
import unicodedata
import re

def sanitize_text(text):
    if not text:
        return ''
    substitutions = {
        '\u2018': "'", '\u2019': "'",
        '\u201c': '"', '\u201d': '"',
        '\u00a0': ' ',
    }
    for char, replacement in substitutions.items():
        text = text.replace(char, replacement)
    return unicodedata.normalize('NFKC', text)

def html_to_blocks(text):
    # Mantiene grassetti e corsivi, converte <br>, <li>, ecc.
    text = text.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    text = text.replace("<ul>", "").replace("</ul>", "")
    text = text.replace("<li>", "- ").replace("</li>", "\n")
    text = text.replace("<p>", "").replace("</p>", "\n")
    return text.split("\n")

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_left_margin(18)
        self.set_right_margin(12)
        self.add_page()
        self.set_font("Arial", size=12)

    def write_block(self, text):
        bold = False
        italic = False

        while '<' in text and '>' in text:
            pre, tag, rest = text.partition('<')
            tag, _, post = rest.partition('>')
            content = sanitize_text(pre.strip())
            if content:
                self.set_font("Arial", "BI" if bold and italic else
                              "B" if bold else
                              "I" if italic else "")
                self.multi_cell(0, 7, content, align="J")

            if tag == "strong":
                bold = True
            elif tag == "/strong":
                bold = False
            elif tag == "em":
                italic = True
            elif tag == "/em":
                italic = False

            text = post

        # Any remaining text
        if text.strip():
            self.set_font("Arial", "BI" if bold and italic else
                          "B" if bold else
                          "I" if italic else "")
            self.multi_cell(0, 7, sanitize_text(text.strip()), align="J")

def generate_pdf(specialist, data, firme, output_dir):
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    pdf_filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    pdf = PDF()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Modulo Informativa Privacy - {specialist['nome']}", ln=True, align="C")
    pdf.ln(10)

    blocks = html_to_blocks(specialist["testo_informativa"])
    for block in blocks:
        if block.strip():
            pdf.write_block(block.strip())
            pdf.ln(2)
        else:
            pdf.ln(3)

    # Firme
    for i, firma in enumerate(firme):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Firma {i+1}", ln=True)
        if firma and firma.startswith("data:image"):
            image_data = base64.b64decode(firma.split(",")[1])
            image_path = f"temp_firma_{i}.png"
            with open(image_path, "wb") as f:
                f.write(image_data)
            pdf.image(image_path, w=60, h=30)
            os.remove(image_path)
        pdf.ln(10)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Data compilazione: {now.strftime('%d/%m/%Y %H:%M')}", ln=True)

    pdf.output(pdf_path)
    return pdf_path
