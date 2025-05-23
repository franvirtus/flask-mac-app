from fpdf import FPDF
import base64
from io import BytesIO
import os
from datetime import datetime
import tempfile
from bs4 import BeautifulSoup

def pulisci_html(html_grezzo):
    """
    Rimuove tutti i tag HTML e restituisce solo il testo.
    """
    return BeautifulSoup(html_grezzo, "html.parser").get_text()

def sanitizza_testo(testo):
    """
    Sostituisce caratteri non compatibili con latin-1, gestisce spazi 
    e a capo, e torna una stringa pulita.
    """
    sostituzioni = {
        '\u2013': '-',  # en dash
        '\u2014': '-',  # em dash
        '\u2018': "'",  # virgolette singole
        '\u2019': "'",
        '\u201c': '"',  # virgolette doppie
        '\u201d': '"',
        '\xa0': ' ',    # spazio non interrompibile
        '<br>': '\n',
        '<p>': '\n',
    }
    if not isinstance(testo, str):
        return ""
    for vecchio, nuovo in sostituzioni.items():
        testo = testo.replace(vecchio, nuovo)
    return testo.encode('latin-1', errors='ignore').decode('latin-1')

class PDF(FPDF):
    def header(self):
        # intestazione vuota, riserva uno spazio di 10pt
        self.set_font("DejaVu", size=10)
        self.cell(0, 10, "", ln=True)

    def scrivi_testo_html(self, html):
        """
        Scompone il testo HTML in righe, mantiene <b>…</b> come grassetto.
        """
        if not isinstance(html, str):
            return
        righe = sanitizza_testo(html).split("\n")
        for riga in righe:
            if "<b>" in riga and "</b>" in riga:
                parti = riga.split("<b>")
                for parte in parti:
                    if "</b>" in parte:
                        grassetto, resto = parte.split("</b>", 1)
                        self.set_font("DejaVu", "B", 12)
                        self.multi_cell(0, 8, grassetto.strip())
                        self.set_font("DejaVu", "", 12)
                        if resto.strip():
                            self.multi_cell(0, 8, resto.strip())
                    else:
                        self.multi_cell(0, 8, parte.strip())
            else:
                self.multi_cell(0, 8, riga.strip())

def decodifica_base64_in_immagine(dati_firma):
    """
    Estrae la parte base64 di una dataURL e la converte in BytesIO.
    """
    if not isinstance(dati_firma, str):
        return BytesIO(b"")
    try:
        header, b64 = dati_firma.split(",", 1)
        img = base64.b64decode(b64)
        return BytesIO(img)
    except Exception:
        return BytesIO(b"")

def generate_pdf(dati, specialista, id_specialista, cartella_output="output"):
    """
    Genera un PDF a partire dai dati del form e dalla configurazione dello specialista.
    """
    # Assicuriamoci che id_specialista sia stringa
    id_specialista = str(id_specialista)

    pdf = PDF()
    pdf.add_font('DejaVu', '', 'static/fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'static/fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', '', 12)
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)

    # Lettura campi comuni
    luogo      = sanitizza_testo(dati.get("firma_luogo", ""))
    data_firma = sanitizza_testo(dati.get("firma_data", ""))
    tutore     = sanitizza_testo(dati.get("tutore", ""))
    paziente   = sanitizza_testo(dati.get("paziente", ""))

    # Intestazione titolo
    pdf.set_font("DejaVu", "B", 14)
    titolo = f"Modulo Informativa Privacy – {specialista['nome']}"
    pdf.cell(0, 10, sanitizza_testo(titolo), ln=True, align="C")
    pdf.ln(8)

    # BLOCCO SPECIFICO: Dott.ssa Chiara Morelli
    if specialista["nome"] == "Dott.ssa Chiara Morelli":
        # Dati Genitore/Tutore
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "Dati Genitore – Tutore:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 6, f"Io sottoscritto/a: {sanitizza_testo(dati.get('genitore_nome',''))}")
        pdf.multi_cell(0, 6, f"Codice Fiscale: {sanitizza_testo(dati.get('genitore_cf',''))}")
        pdf.multi_cell(0, 6, f"Nato/a a: {sanitizza_testo(dati.get('genitore_luogo_nascita',''))} il {sanitizza_testo(dati.get('genitore_data_nascita',''))}")
        pdf.multi_cell(0, 6, f"Residente in: {sanitizza_testo(dati.get('genitore_indirizzo',''))} – CAP {sanitizza_testo(dati.get('genitore_cap',''))}")
        pdf.multi_cell(0, 6, f"Tel: {sanitizza_testo(dati.get('genitore_tel',''))} – Email: {sanitizza_testo(dati.get('genitore_email',''))}")
        pdf.ln(4)

        # Dati del Minore
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "Dati del Minore:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 6, f"Nome: {sanitizza_testo(dati.get('minore_nome',''))}")
        pdf.multi_cell(0, 6, f"Codice Fiscale: {sanitizza_testo(dati.get('minore_cf',''))}")
        pdf.multi_cell(0, 6, f"Nato/a a: {sanitizza_testo(dati.get('minore_luogo_nascita',''))} il {sanitizza_testo(dati.get('minore_data_nascita',''))}")
        pdf.multi_cell(0, 6, f"Residente in: {sanitizza_testo(dati.get('minore_indirizzo',''))} – CAP {sanitizza_testo(dati.get('minore_cap',''))}")
        pdf.ln(6)

        # Informativa e dichiarazioni
        pdf.set_font("DejaVu", "", 12)
        testo_inf = pulisci_html(specialista.get("testo_informativa",""))
        pdf.multi_cell(0, 6, sanitizza_testo(testo_inf))
        pdf.ln(6)

        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "DICHIARAZIONI:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 6, "- Ho ricevuto informazioni in modo chiaro e comprensibile sulle sedute")
        pdf.multi_cell(0, 6, "- Autorizzo invio materiale informativo via email: " + sanitizza_testo(dati.get("consenso_email","")))
        pdf.multi_cell(0, 6, "- Autorizzo invio SMS per conferma appuntamenti: " + sanitizza_testo(dati.get("consenso_sms","")))
        pdf.ln(6)

    # BLOCCO SPECIFICO: Dott.ssa Veronica Lorenzini
    elif specialista["nome"] == "Dott.ssa Veronica Lorenzini":
        # 1. Informativa
        pdf.set_font("DejaVu", "", 12)
        pdf.scrivi_testo_html(specialista.get("testo_informativa",""))
        pdf.ln(6)

        # 2. Firma Modulo Privacy
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "Firma Modulo Privacy", ln=True, align="C")
        pdf.ln(4)

    # BLOCCO GENERICO per gli altri specialisti
    else:
        if "testo_informativa" in specialista:
            pdf.set_font("DejaVu", "", 12)
            testo_gen = pulisci_html(specialista["testo_informativa"])
            pdf.multi_cell(0, 6, sanitizza_testo(testo_gen))
            pdf.ln(6)

    # ——————————————————————————————————————————
    # CONSENSI (sempre presente, anche per Serioli)
    if specialista.get("consensi"):
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 8, "Dichiaro inoltre di:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        for c in specialista["consensi"]:
            scelta = sanitizza_testo(dati.get(c["campo"], ""))
            pdf.multi_cell(0, 6, f"{scelta} {c['label']}")
        pdf.ln(6)

    # LUOGO e DATA
    if luogo:
        pdf.cell(0, 8, f"Luogo: {luogo}", ln=True)
    if data_firma:
        pdf.cell(0, 8, f"Data: {data_firma}", ln=True)
    pdf.ln(6)

    # INFINE: Inserimento delle firme grafiche
    posizioni = specialista.get("signature_positions", [])
    totale    = specialista.get("firme", 0)
    for i in range(totale):
        chiave_firma = f"firma{i+1}"
        chiave_etichetta = f"firma_label{i+1}"
        dati_firma = dati.get(chiave_firma, "")
        if not dati_firma:
            continue
        # decodifica e salvataggio temporaneo
        img_bytes = base64.b64decode(dati_firma.split(",",1)[1])
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(img_bytes); tmp.close()
        x, y = posizioni[i] if i < len(posizioni) else (pdf.l_margin + (i+1)*(pdf.w - pdf.l_margin - pdf.r_margin)/(totale+1), pdf.get_y())
        # etichetta
        etichetta = dati.get(chiave_etichetta) or specialista["etichette_firme"][i]
        pdf.set_xy(x, y-6)
        pdf.set_font("DejaVu", "B", 10)
        pdf.cell(0,5, sanitizza_testo(etichetta))
        # immagine firma
        pdf.image(tmp.name, x=x, y=y, w=60)
        os.remove(tmp.name)
        pdf.ln(30)

    # SALVA file
    os.makedirs(cartella_output, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    nome_file = f"{specialista['nome'].replace(' ','_')}_{ts}.pdf"
    percorso = os.path.join(cartella_output, nome_file)
    pdf.output(percorso)

    return percorso
