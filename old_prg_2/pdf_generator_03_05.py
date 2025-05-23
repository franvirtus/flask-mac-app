from fpdf import FPDF
import base64
from io import BytesIO
import os
from datetime import datetime
import tempfile
from bs4 import BeautifulSoup

def clean_html(raw_html):
    return BeautifulSoup(raw_html, "html.parser").get_text()

def sanitize_text(text):
    """Rimuove caratteri non compatibili con latin-1 e simboli non visibili."""
    replacements = {
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\xa0': ' ',    # Non-breaking space
        '<br>': '\n',
        '<p>': '\n',
    }
    # Verifica che il testo sia una stringa
    if not isinstance(text, str):
        return ""
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='ignore').decode('latin-1')

class PDF(FPDF):
    def header(self):
        self.set_font("DejaVu", size=10)
        self.cell(0, 10, "", ln=True)

    def write_html_formatted(self, html_text):
        # Verifica che html_text sia una stringa
        if not isinstance(html_text, str):
            return
            
        lines = sanitize_text(html_text).split("\n")
        for line in lines:
            if "<b>" in line and "</b>" in line:
                parts = line.split("<b>")
                for part in parts:
                    if "</b>" in part:
                        bold_text, rest = part.split("</b>", 1)
                        self.set_font("DejaVu", "B", 12)
                        self.multi_cell(0, 8, bold_text.strip())
                        self.set_font("DejaVu", "", 12)
                        if rest.strip():
                            self.multi_cell(0, 8, rest.strip())
                    else:
                        self.multi_cell(0, 8, part.strip())
            else:
                self.multi_cell(0, 8, line.strip())

def decode_base64_to_image(signature_data):
    if not isinstance(signature_data, str):
        return BytesIO(b"")  # Restituisce un BytesIO vuoto in caso di errore
    try:
        image_data = base64.b64decode(signature_data.split(",")[1])
        return BytesIO(image_data)
    except (IndexError, ValueError):
        return BytesIO(b"")  # Gestisce errori di formato

def generate_pdf(data, specialist, specialist_id, output_dir="output"):
    # Verifica che specialist_id sia una stringa
    if not isinstance(specialist_id, str):
        specialist_id = str(specialist_id)
        
    pdf = PDF()
    pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'static/fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    luogo = ""
    data_firma = ""


    # Titolo
    pdf.set_font("DejaVu", "B", 14)
    title = f"Modulo Informativa Privacy – {specialist['nome']}"
    pdf.cell(0, 10, sanitize_text(title), ln=True, align="C")
    pdf.ln(10)


# Se è Morelli, inseriamo i dati Genitore e Minore
    if specialist["nome"] == "Dott.ssa Chiara Morelli":
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Dati Genitore - Tutore:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, f"Io sottoscritto: {sanitize_text(data.get('genitore_nome', ''))}")
        pdf.multi_cell(0, 8, f"Codice Fiscale: {sanitize_text(data.get('genitore_cf', ''))}")
        pdf.multi_cell(0, 8, f"Nato a: {sanitize_text(data.get('genitore_luogo_nascita', ''))}")
        pdf.multi_cell(0, 8, f"Data di nascita: {sanitize_text(data.get('genitore_data_nascita', ''))}")
        pdf.multi_cell(0, 8, f"Residente in: {sanitize_text(data.get('genitore_indirizzo', ''))} - CAP: {sanitize_text(data.get('genitore_cap', ''))}")
        pdf.multi_cell(0, 8, f"Telefono: {sanitize_text(data.get('genitore_tel', ''))}")
        pdf.multi_cell(0, 8, f"Email: {sanitize_text(data.get('genitore_email', ''))}")
        pdf.ln(5)

        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "Dati del Minore:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, f"Nome: {sanitize_text(data.get('minore_nome', ''))}")
        pdf.multi_cell(0, 8, f"Codice Fiscale: {sanitize_text(data.get('minore_cf', ''))}")
        pdf.multi_cell(0, 8, f"Nato a: {sanitize_text(data.get('minore_luogo_nascita', ''))}")
        pdf.multi_cell(0, 8, f"Data di nascita: {sanitize_text(data.get('minore_data_nascita', ''))}")
        pdf.multi_cell(0, 8, f"Residente in: {sanitize_text(data.get('minore_indirizzo', ''))} - CAP: {sanitize_text(data.get('minore_cap', ''))}")
        pdf.ln(5)


# SOLO per Morelli: inseriamo testo informativa e dichiarazioni
    if specialist["nome"] == "Dott.ssa Chiara Morelli":
        pdf.set_font("DejaVu", "", 12)
        pdf.ln(5)
        testo = specialist.get("testo_informativa", "")
        testo_pulito = clean_html(testo)
        pdf.multi_cell(0, 8, sanitize_text(testo_pulito))
        pdf.ln(5)
    
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, "DICHIARAZIONI:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 8, "Dichiaro di essere stato informato in modo chiaro, comprensibile ed esauriente su:")
        pdf.multi_cell(0, 8, "- La tipologia delle sedute chinesiologiche proposte")
        pdf.multi_cell(0, 8, "- I benefici attesi e le possibili conseguenze")
        pdf.multi_cell(0, 8, "- Gli eventuali effetti collaterali e i rischi")
        pdf.multi_cell(0, 8, "- I comportamenti da adottare")
        consenso_email = data.get("consenso_email", "")
        consenso_sms = data.get("consenso_sms", "")
        pdf.multi_cell(0, 8, f"Invio materiale informativo via email: {consenso_email}")
        pdf.multi_cell(0, 8, f"Invio SMS relativi ad appuntamenti: {consenso_sms}")
        pdf.ln(5)
    # Testo informativa
    # SOLO per altri specialisti: mostra l'informativa subito
    if specialist.get("nome") == "Dott.ssa Veronica Lorenzini":
    # 1. Informativa
        pdf.set_font("DejaVu", "", 12)
        pdf.write_html_formatted(specialist.get("testo_informativa", ""))
        pdf.ln(5)

    elif "testo_informativa" in specialist:
        pdf.set_font("DejaVu", "", 12)
        testo_generico = specialist.get("testo_informativa", "")
        testo_pulito = clean_html(testo_generico)
        pdf.multi_cell(0, 8, sanitize_text(testo_pulito))
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

    # 3. Firma 1
        firma1_stream = decode_base64_to_image(data.get("firma1", ""))
        if firma1_stream.getbuffer().nbytes > 0:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file.write(firma1_stream.read())
                tmp_path = tmp_file.name
            pdf.cell(0, 10, "Firma:", ln=True)
            pdf.image(tmp_path, x=pdf.get_x(), y=pdf.get_y(), w=60)
            pdf.ln(30)
            os.remove(tmp_path)

    # 4. Consensi con intestazione modificata
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "Dichiaro inoltre di:", ln=True)
    pdf.set_font("DejaVu", "", 12)
    for consenso in specialist.get("consensi", []):
        scelta = sanitize_text(data.get(consenso["campo"], ""))
        pdf.multi_cell(0, 8, f"{consenso['label']}: {scelta}")
    pdf.ln(5)

    # 5. Firma 2
    firma2_stream = decode_base64_to_image(data.get("firma2", ""))
    if firma2_stream.getbuffer().nbytes > 0:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            tmp_file.write(firma2_stream.read())
            tmp_path = tmp_file.name
        pdf.cell(0, 10, "Firma:", ln=True)
        pdf.image(tmp_path, x=pdf.get_x(), y=pdf.get_y(), w=60)
        pdf.ln(30)
        os.remove(tmp_path)

    # 6. Luogo e data
    if luogo:
        pdf.cell(0, 10, f"Luogo: {luogo}", ln=True)
    if data_firma:
        pdf.cell(0, 10, f"Data: {data_firma}", ln=True)

      # Evita la stampa doppia sotto

# Firme
       
    for i in range(specialist.get("firme", 0)):
        key = f"firma{i + 1}"
        if key in data:
            try:
                img_stream = decode_base64_to_image(data[key])
                
                # Verifica che la firma non sia vuota
                if img_stream.getbuffer().nbytes == 0:
                    raise ValueError("Firma vuota")

                # Salva temporaneamente la firma su disco
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                    tmp_file.write(img_stream.read())
                    tmp_file_path = tmp_file.name

                # Inserisce la firma nel PDF
                pdf.ln(5)
                etichette_firme = specialist.get("etichette_firme", [])
                etichetta = etichette_firme[i] if i < len(etichette_firme) else f"Firma {i + 1}:"
                pdf.cell(0, 10, etichetta, ln=True)

                pdf.image(tmp_file_path, x=pdf.get_x(), y=pdf.get_y(), w=60)
                pdf.ln(30)

                # Rimuove il file temporaneo
                os.remove(tmp_file_path)

            except Exception as e:
                pdf.cell(0, 10, f"Errore nella firma {i + 1}: {str(e)}", ln=True)
        else:
            pdf.cell(0, 10, f"Firma {i + 1} mancante o vuota", ln=True)

    # Salvataggio
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
    path = os.path.join(output_dir, filename)
    pdf.output(path)

    return path
