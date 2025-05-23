from fpdf import FPDF
from io import BytesIO
import base64
import tempfile
import os
import re

def sanitize_text(text):
    replacements = {
        "“": '"', "”": '"',
        "‘": "'", "’": "'",
        "–": "-", "—": "-",
        "…": "...",
        "\u2013": "-", "\u2014": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "..."
    }
    for wrong, right in replacements.items():
        text = text.replace(wrong, right)
    return text

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Modulo Privacy", ln=True, align="C")

    def add_multiline_text(self, text):
        self.set_font("Arial", "", 11)
        for line in text.split("\n"):
            self.multi_cell(0, 8, sanitize_text(line.strip()))
            self.ln(1)

    def add_field(self, label, value):
        self.set_font("Arial", "B", 11)
        self.cell(50, 8, f"{label}:", ln=0)
        self.set_font("Arial", "", 11)
        self.cell(0, 8, sanitize_text(value), ln=True)

    def add_signature(self, label, image_base64):
        self.set_font("Arial", "B", 11)
        self.cell(0, 10, f"{label}:", ln=True)
        try:
            image_data = base64.b64decode(image_base64.split(",")[1])
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(image_data)
                tmp_file.flush()
                self.image(tmp_file.name, x=self.get_x(), y=self.get_y(), w=60)
            os.unlink(tmp_file.name)
            self.ln(30)
        except Exception:
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, f"Errore nella {label.lower()}", ln=True)
            self.set_text_color(0, 0, 0)

def generate_pdf(specialist, specialist_id, data, firme, output_dir="output"):
    pdf = PDF()
    pdf.add_page()

    # Campi aggiuntivi
    for campo in specialist.get("campi_aggiuntivi", []):
        valore = data.get(campo, "")
        pdf.add_field(campo.replace("_", " ").capitalize(), valore)

    # Testo informativa
    pdf.ln(3)
    testo_informativa = specialist.get("testo_informativa", "")
    pdf.add_multiline_text(testo_informativa)

    # Consensi
    consensi = specialist.get("consensi", [])
    if consensi:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "Consensi:", ln=True)
        for consenso in consensi:
            campo = consenso["campo"]
            label = consenso["label"]
            valore = data.get(campo, "Non specificato")
            pdf.add_field(label, valore)

    # Dichiarazioni finali personalizzate
    dichiarazioni = specialist.get("dichiarazioni_finali", [])
    if dichiarazioni:
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "Dichiarazioni finali:", ln=True)
        pdf.set_font("Arial", "", 11)
        for testo in dichiarazioni:
            pdf.add_multiline_text(testo)

    # Luogo e data
    if specialist.get("usa_data_luogo"):
        pdf.ln(5)
        luogo = data.get("firma_luogo", "")
        data_firma = data.get("firma_data", "")
        pdf.add_field("Luogo", luogo)
        pdf.add_field("Data", data_firma)

    # Firme
    for i, firma_b64 in enumerate(firme):
        pdf.add_signature(f"Firma {i + 1}", firma_b64)

    # Salvataggio
    os.makedirs(output_dir, exist_ok=True)
    timestamp = data.get("timestamp", "data")
    timestamp_clean = re.sub(r"[\/\\\:\*\?\"\<\>\|]", "_", timestamp)
    filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp_clean}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)

    return filepath
