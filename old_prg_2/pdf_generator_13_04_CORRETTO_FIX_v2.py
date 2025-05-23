
from fpdf import FPDF
from datetime import datetime
import os
import base64
import unicodedata
import re

def sanitize_text(text):
    if not text:
        return ''
    # Normalizza i caratteri Unicode e rimuove quelli non ASCII
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "", ln=1)

    def add_text(self, text):
        # Pulisce i tag HTML base
        text = text.replace("<p>", "").replace("</p>", "
")
        text = text.replace("<br>", "
").replace("<br/>", "
").replace("<br />", "
")
        text = text.replace("<ul>", "").replace("</ul>", "")
        text = text.replace("<li>", "- ").replace("</li>", "
")

        # Regexp per <strong> e <em>
        pattern = re.compile(r'(<strong>(.*?)</strong>)|(<em>(.*?)</em>)', re.DOTALL)

        pos = 0
        for match in pattern.finditer(text):
            start, end = match.span()

            # Testo normale prima del match
            normal_text = text[pos:start]
            self.set_font("Arial", "", 12)
            for line in normal_text.split("
"):
                if line.strip():
                    self.multi_cell(0, 10, sanitize_text(line.strip()))

            if match.group(1):  # <strong>
                self.set_font("Arial", "B", 12)
                bold_text = match.group(2)
                for line in bold_text.split("
"):
                    if line.strip():
                        self.multi_cell(0, 10, sanitize_text(line.strip()))
            elif match.group(3):  # <em>
                self.set_font("Arial", "I", 12)
                italic_text = match.group(4)
                for line in italic_text.split("
"):
                    if line.strip():
                        self.multi_cell(0, 10, sanitize_text(line.strip()))

            pos = end

        # Resto del testo dopo l'ultimo match
        if pos < len(text):
            self.set_font("Arial", "", 12)
            rest = text[pos:]
            for line in rest.split("
"):
                if line.strip():
                    self.multi_cell(0, 10, sanitize_text(line.strip()))

    def add_signature(self, label, base64_data):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, sanitize_text(label), ln=1)
        if base64_data and base64_data.startswith("data:image"):
            image_data = base64.b64decode(base64_data.split(",")[1])
            image_path = f"temp_signature_{label.replace(' ', '_')}.png"
            with open(image_path, "wb") as f:
                f.write(image_data)
            self.image(image_path, w=60, h=30)
            os.remove(image_path)
        self.ln(10)

def generate_pdf(specialist, data, firme, output_dir):
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d%H%M%S")
    pdf_filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    pdf = PDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, sanitize_text(f"Modulo Informativa Privacy - {specialist['nome']}"), ln=1, align='C')
    pdf.ln(10)

    if specialist.get("usa_dati_minore"):
        intestazione = (
            f"Io sottoscritto/a {data.get('nome_genitore', '')} {data.get('cognome_genitore', '')}, CF {data.get('cf_genitore', '')},
"
            f"nato/a a {data.get('luogo_nascita_genitore', '')} il {data.get('data_nascita_genitore', '')}, residente in {data.get('residenza_genitore', '')},
"
            f"CAP {data.get('cap_genitore', '')}, telefono {data.get('telefono_genitore', '')}, email {data.get('email_genitore', '')},
"
            f"in qualità di genitore/tutore del minore {data.get('nome_minore', '')} {data.get('cognome_minore', '')}, CF {data.get('cf_minore', '')},
"
            f"nato/a a {data.get('luogo_nascita_minore', '')} il {data.get('data_nascita_minore', '')}, residente a {data.get('residenza_minore', '')}, CAP {data.get('cap_minore', '')}."
        )
        pdf.add_text(intestazione)
        pdf.ln(5)

    testo_html = specialist["testo_informativa"]
    pdf.add_text(testo_html)

    if specialist.get("consensi"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "
Consensi Informati:", ln=1)
        pdf.set_font("Arial", size=12)
        for consenso in specialist['consensi']:
            risposta = data.get(consenso["campo"], "Non specificato")
            pdf.cell(0, 10, sanitize_text(f"{consenso['label']}: {risposta}"), ln=1)

    for i, base64_data in enumerate(firme):
        pdf.add_signature(f"Firma {i+1}", base64_data)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, f"Data compilazione: {now.strftime('%d/%m/%Y %H:%M')}", ln=1)

    pdf.output(pdf_path)
    return pdf_path
