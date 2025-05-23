from fpdf import FPDF
import base64
from io import BytesIO
import os
from datetime import datetime
import tempfile

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
        self.set_font("Arial", size=10)
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
                        self.set_font("Arial", "B", 12)
                        self.multi_cell(0, 8, bold_text.strip())
                        self.set_font("Arial", "", 12)
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
    pdf.set_font('DejaVu', '', 12)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    

    # Titolo
    pdf.set_font("Arial", "B", 14)
    title = f"Modulo Informativa Privacy – {specialist['nome']}"
    pdf.cell(0, 10, sanitize_text(title), ln=True, align="C")
    pdf.ln(10)

    # Testo informativa
    # SOLO per altri specialisti: mostra l'informativa subito
    if specialist["nome"] != "Dott.ssa Chiara Morelli":
        pdf.set_font("Arial", size=12)
        pdf.write_html_formatted(specialist.get("testo_informativa", ""))
        pdf.ln(5)


    # Dati paziente
    if specialist.get("campi_aggiuntivi"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Dati del paziente:", ln=True)
        pdf.set_font("Arial", "", 12)
        for campo in specialist["campi_aggiuntivi"]:
            valore = sanitize_text(data.get(campo, ""))
            pdf.multi_cell(0, 8, f"{campo.replace('_', ' ').capitalize()}: {valore}")
        pdf.ln(3)
        # Se è Morelli, stampa qui l'informativa (dopo i dati del minore)
    if specialist["nome"] == "Dott.ssa Chiara Morelli":
        pdf.set_font("Arial", size=12)
        testo = specialist.get("testo_informativa", "")
        pdf.multi_cell(0, 8, testo)
        pdf.ln(5)


    # Consensi
    if specialist.get("consensi"):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Consensi:", ln=True)
        pdf.set_font("Arial", "", 12)
        for consenso in specialist["consensi"]:
            scelta = sanitize_text(data.get(consenso["campo"], ""))
            pdf.multi_cell(0, 8, f"{consenso['label']}: {scelta}")
        pdf.ln(3)

    # Blocco finale personalizzato
    if specialist.get("dichiarazione_finale_blocco", {}).get("attivo"):
        template = specialist["dichiarazione_finale_blocco"].get("template", "")
        
        # Verifica che i campi siano presenti prima di formattare
        nome = sanitize_text(data.get("firma_nome", ""))
        cognome = sanitize_text(data.get("firma_cognome", ""))
        luogo = sanitize_text(data.get("firma_luogo", ""))
        data_nascita = sanitize_text(data.get("firma_data_nascita", ""))
        
        try:
            testo = template.format(
                nome=nome,
                cognome=cognome,
                luogo=luogo,
                data_nascita=data_nascita
            )
            pdf.ln(5)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, sanitize_text(testo))
        except KeyError as e:
            # Gestisce errori di formattazione
            pdf.multi_cell(0, 8, f"Errore nella formattazione della dichiarazione: {str(e)}")

    # Luogo e Data
    if specialist.get("usa_data_luogo"):
        luogo = sanitize_text(data.get("firma_luogo", "")).strip()
        data_firma = sanitize_text(data.get("firma_data", "")).strip()

        if luogo:
            pdf.cell(0, 10, f"Luogo: {luogo}", ln=True)
        if data_firma:
            pdf.cell(0, 10, f"Data: {data_firma}", ln=True)


    # Firme
    # Firme
    import tempfile

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
                pdf.cell(0, 10, f"Firma {i + 1}:", ln=True)
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
