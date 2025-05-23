from fpdf import FPDF
import base64
from io import BytesIO
from datetime import datetime
import os

def sanitize_text(text):
    replacements = {
        "<br>": "\n", "<br/>": "\n", "<br />": "\n",
        "’": "'", "“": '"', "”": '"', "–": "-", "…": "...",
        "‘": "'", "—": "-", "•": "-", "´": "'", "\xa0": " "
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "Modulo Privacy", ln=True, align="C")
        self.ln(5)

def generate_pdf(specialist, specialist_id, data, firme, output_dir):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "", 12)

    # Titolo specialista
    pdf.set_font("Arial", "B", 14)
    pdf.multi_cell(0, 10, sanitize_text(specialist.get("nome", "")))
    pdf.ln(5)
    pdf.set_font("Arial", "", 12)

    # Testo informativa
    testo = specialist.get("testo_informativa") or specialist.get("testo", "")
    pdf.multi_cell(0, 8, sanitize_text(testo))
    pdf.ln(5)

    # Dati anagrafici
    campi_personali = [
        "nome", "cognome", "data_nascita", "codice_fiscale", "cf",
        "indirizzo", "residente", "nato_a"
    ]
    dati_presenti = [campo for campo in campi_personali if campo in data]
    if dati_presenti:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Dati del paziente:", ln=True)
        pdf.set_font("Arial", "", 11)
        for campo in dati_presenti:
            label = campo.replace("_", " ").capitalize()
            valore = data.get(campo, "")
            pdf.cell(0, 8, f"{label}: {sanitize_text(valore)}", ln=True)
        pdf.ln(5)

    # Consensi speciali
    if "consensi" in specialist:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Consensi specifici:", ln=True)
        pdf.set_font("Arial", "", 11)
        for consenso in specialist["consensi"]:
            campo = consenso.get("campo")
            label = consenso.get("label", campo.replace("_", " ").capitalize())
            valore = data.get(campo, "")
            pdf.cell(0, 8, f"{label}: {sanitize_text(valore)}", ln=True)
        pdf.ln(5)

    if specialist_id == "1":
        pdf.ln(10)
        pdf.set_font("Helvetica", "", 12)
    
        firma_nome = data.get("firma_nome", "")
        firma_luogo = data.get("firma_luogo", "")
        firma_data_nascita = data.get("firma_data_nascita", "")
        firma_data = data.get("firma_data", "")

        pdf.multi_cell(0, 10,
        f"Il/La sottoscritto/a {firma_nome}, nato a {firma_luogo} il {firma_data_nascita},\n"
        "dopo avere letto la superiore informativa, dà il consenso al trattamento dei dati "
        "che lo riguardano per le finalità ivi indicate.\n\n"
        f"Data: {firma_data}        Firma leggibile: ____________________________"
    )


    # Firme
    pdf.set_font("Arial", "B", 12)
    for idx, firma_b64 in enumerate(firme, start=1):
        if firma_b64:
            try:
                imgdata = base64.b64decode(firma_b64.split(",")[1])
                img = BytesIO(imgdata)
                pdf.cell(0, 10, f"Firma {idx}:", ln=True)
                pdf.image(img, type="PNG", w=60)
                pdf.ln(10)
            except Exception as e:
                pdf.cell(0, 10, f"Errore nella firma {idx}", ln=True)

    # Salvataggio
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath
