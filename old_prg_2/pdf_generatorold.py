from fpdf import FPDF
import base64
import os
from html import unescape

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        
    def add_text(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, text)

    def add_signature(self, title, base64_img, index):
        self.ln(5)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, title, ln=1)
        if base64_img:
            image_bytes = base64.b64decode(base64_img.split(",")[1])
            temp_filename = f"temp_signature_{index}.png"
            with open(temp_filename, "wb") as f:
                f.write(image_bytes)
            self.image(temp_filename, w=60)
            os.remove(temp_filename)


genitore_text = (
    f'Io sottoscritto/a {data.get("nome_genitore", "")}, CF {data.get("cf_genitore", "")}, '
    f'nato/a a {data.get("luogo_nascita_genitore", "")} il {data.get("data_nascita_genitore", "")}, '
    f'residente a {data.get("residenza_genitore", "")}, CAP {data.get("cap_genitore", "")}, '
    f'telefono {data.get("telefono_genitore", "")}, email {data.get("email_genitore", "")}, '
    f'in qualità di genitore/tutore del minore'
)

minore_text = (
    f'{data.get("nome_minore", "")}, CF {data.get("cf_minore", "")}, '
    f'nato/a a {data.get("luogo_nascita_minore", "")} il {data.get("data_nascita_minore", "")}, '
    f'residente a {data.get("residenza_minore", "")}, CAP {data.get("cap_minore", "")}.'
)

pdf.multi_cell(0, 10, genitore_text)
pdf.ln(3)
pdf.multi_cell(0, 10, minore_text)


def generate_pdf(specialist, data, firme, output_dir, filename):
    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    if specialist["nome"] == "Dott.ssa Chiara Morelli":
        pdf.set_font("Arial", "B", 12)
        pdf.ln(10)
        pdf.multi_cell(0, 10, "MODULO DI CONSENSO INFORMATO ALLE SEDUTE DI CHINESIOLOGIA ED", align="C")
        pdf.multi_cell(0, 10, "AUTORIZZAZIONE AL TRATTAMENTO DEI DATI PERSONALI E RELATIVI ALLA SALUTE", align="C")
        pdf.multi_cell(0, 10, "INFORMATIVA RELATIVA AL TRATTAMENTO DEI DATI PERSONALI", align="C")
        pdf.multi_cell(0, 10, "AI SENSI DELL'ART. 13 REGOLAMENTO (UE) 2016/679 (GDPR)", align="C")

        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, f"Io sottoscritto/a {data.get('genitore_nome', '')}, CF {data.get('genitore_cf', '')}, nato/a a {data.get('genitore_luogo_nascita', '')} il {data.get('genitore_data_nascita', '')}, residente a {data.get('genitore_indirizzo', '')} CAP {data.get('genitore_cap', '')}, telefono {data.get('genitore_tel', '')}, email {data.get('genitore_email', '')}, in qualità di genitore/tutore del minore {data.get('minore_nome', '')}, CF {data.get('minore_cf', '')}, nato/a a {data.get('minore_luogo_nascita', '')} il {data.get('minore_data_nascita', '')}, residente a {data.get('minore_indirizzo', '')}, CAP {data.get('minore_cap', '')}.")

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "DICHIARO:", ln=1)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, "- di essere stato informato riguardo gli obiettivi dell'intervento di chinesiologia... [testo completo qui]")
        pdf.multi_cell(0, 10, "- di essere stato informato che l'intervento non sostituisce l'intervento medico... [continua testo]")

        pdf.ln(3)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "DICHIARO INOLTRE:", ln=1)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 10, "- di essere a conoscenza della possibilità di revocare il consenso in qualsiasi momento...")

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, "CONSENSI FINALI:", ln=1)
        pdf.set_font("Arial", "", 11)
        consenso1 = data.get("consenso_chinesiologia", "Non specificato")
        consenso2 = data.get("consenso_privacy", "Non specificato")
        pdf.cell(0, 10, f"1. Trattamento dei dati per chinesiologia: {consenso1}", ln=1)
        pdf.cell(0, 10, f"2. Trattamento dei dati personali: {consenso2}", ln=1)

    testo_html = specialist["testo_informativa"]
    testo_pulito = testo_html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    testo_pulito = unescape(testo_pulito).replace("’", "'").encode("latin-1", "ignore").decode("latin-1")
    pdf.add_text(testo_pulito)

    if specialist["nome"] != "Dott. Gaetano Messineo":
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Dati del paziente:", ln=1)
        pdf.set_font("Arial", "", 11)
        for key, value in data.items():
            if key.startswith("consenso") or key.startswith("firma") or key in ["timestamp", "data_compilazione"]:
                continue
            pdf.cell(0, 10, f"{key.capitalize()}: {value}", ln=1)

    if specialist.get("consensi"):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Consensi informati:", ln=1)
        pdf.set_font("Arial", "", 11)
        for consenso in specialist["consensi"]:
            risposta = data.get(consenso["campo"], "Non specificato")
            pdf.cell(0, 10, f"{consenso['label']}: {risposta}", ln=1)

    if specialist["nome"] == "Dott. Gaetano Messineo":
        nome = data.get("nome", "")
        cognome = data.get("cognome", "")
        indirizzo = data.get("indirizzo", "")
        codice_fiscale = data.get("codice_fiscale", "")
        data_nascita = data.get("data_nascita", "")

        pdf.ln(10)
        pdf.set_font("Arial", "B", 11)
        pdf.multi_cell(0, 10,
            f"""Il/la sottoscritto/a {nome} {cognome}, residente in {indirizzo}, Codice Fiscale: {codice_fiscale}, nato/a il {data_nascita}
dopo avere letto la superiore informativa, dà il consenso al trattamento dei dati che lo riguardano per le finalità ivi indicate.""")

    pdf.ln(10)
    for i, firma in enumerate(firme):
        pdf.add_signature(f"Firma {i+1}", firma, i+1)

    pdf_path = os.path.join(output_dir, filename)
    pdf.output(pdf_path)

    return pdf_path
