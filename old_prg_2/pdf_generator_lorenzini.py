
from datetime import datetime
from fpdf import FPDF
import os
import tempfile
import base64

def decode_base64_to_image(base64_string):
    return base64.b64decode(base64_string.split(",")[1])

def sanitize_text(value):
    return value.strip() if isinstance(value, str) else ""

class PDF(FPDF):
    def write_html_formatted(self, html_text):
        self.set_font("DejaVu", "", 12)
        self.multi_cell(0, 10, html_text)

def generate_pdf(data, specialist, output_dir="output"):
    pdf = PDF()
    pdf.add_font("DejaVu", "", "static/fonts/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if specialist.get("nome") == "Dott.ssa Veronica Lorenzini":
        # 1. Informativa
        pdf.set_font("DejaVu", "", 12)
        testo_informativa = specialist.get("testo_informativa", "")
        pdf.multi_cell(0, 8, testo_informativa)
        pdf.ln(5)

        # 2. Frase "Io sottoscritto/a..."
        nome = sanitize_text(data.get("nome", ""))
        cognome = sanitize_text(data.get("cognome", ""))
        indirizzo = sanitize_text(data.get("indirizzo", ""))
        luogo_nascita = sanitize_text(data.get("firma_luogo", ""))
        data_nascita = sanitize_text(data.get("firma_data_nascita", ""))
        luogo = sanitize_text(data.get("firma_luogo", "")).strip()
        data_firma = sanitize_text(data.get("firma_data", "")).strip()

        testo_finale = (
            f"Io sottoscritto/a {nome} {cognome}, nato/a a {luogo_nascita} il {data_nascita}, residente a {indirizzo}, "
            f"acquisite le summenzionate informazioni fornite dal Titolare del trattamento ai sensi dell’art. 13 del Reg. UE, "
            f"e consapevole, in particolare, che il trattamento potrà riguardare dati relativi alla salute, presto il mio consenso "
            f"per il trattamento dei suddetti dati per le finalità di cui al punto 1, lett. A) dell'informativa."
        )
        pdf.multi_cell(0, 8, testo_finale)
        pdf.ln(5)

        # 3. Prima Firma
        firma1_stream = decode_base64_to_image(data.get("firma1", ""))
        if firma1_stream:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(firma1_stream)
                tmp_path = tmp_file.name
            pdf.cell(0, 10, "Firma:", ln=True)
            pdf.image(tmp_path, x=pdf.get_x(), y=pdf.get_y(), w=60)
            pdf.ln(30)
            os.remove(tmp_path)

        # 4. Consensi
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Dichiaro inoltre di:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        for consenso in specialist.get("consensi", []):
            scelta = sanitize_text(data.get(consenso["campo"], ""))
            pdf.multi_cell(0, 8, f"{consenso['label']}: {scelta}")
        pdf.ln(5)

        # 5. Seconda Firma
        firma2_stream = decode_base64_to_image(data.get("firma2", ""))
        if firma2_stream:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(firma2_stream)
                tmp_path = tmp_file.name
            pdf.cell(0, 10, "Firma:", ln=True)
            pdf.image(tmp_path, x=pdf.get_x(), y=pdf.get_y(), w=60)
            pdf.ln(30)
            os.remove(tmp_path)

        # 6. Luogo e Data
        if luogo:
            pdf.cell(0, 10, f"Luogo: {luogo}", ln=True)
        if data_firma:
            pdf.cell(0, 10, f"Data: {data_firma}", ln=True)

        # Salva PDF
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
        path = os.path.join(output_dir, filename)
        pdf.output(path)
        return path

    return None
