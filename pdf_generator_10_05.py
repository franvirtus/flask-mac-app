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
    # Leggo subito i campi Luogo e Data dal form, per tutti gli specialisti
    luogo      = sanitize_text(data.get("firma_luogo", ""))
    data_firma = sanitize_text(data.get("firma_data", ""))
    tutore   = sanitize_text(data.get("tutore", ""))
    paziente = sanitize_text(data.get("paziente", ""))
    salutation = sanitize_text(data.get("salutation", ""))
    full_name  = sanitize_text(data.get("full_name", ""))



    # Titolo
    pdf.set_font("DejaVu", "B", 14)
    title = f"Modulo Informativa Privacy – {specialist['nome']}"
    pdf.cell(0, 10, sanitize_text(title), ln=True, align="C")
    pdf.ln(10)


# Se è Morelli, inseriamo i dati Genitore e Minore
    if specialist["nome"] == "Dott.ssa Chiara Morelli":
        pdf.set_font("DejaVu", "B", 12)
        gen_nome   = sanitize_text(data.get("genitore_nome", ""))
        gen_cf     = sanitize_text(data.get("genitore_cf", ""))
        gen_luogo  = sanitize_text(data.get("genitore_luogo_nascita", ""))
        gen_dn     = sanitize_text(data.get("genitore_data_nascita", ""))
        gen_res    = sanitize_text(data.get("genitore_indirizzo", ""))
        gen_cap    = sanitize_text(data.get("genitore_cap", ""))

        pdf.multi_cell(
            0, 8,
            f"Io sottoscritto: {gen_nome} Codice Fiscale {gen_cf}, nato a {gen_luogo} il {gen_dn}, "
            f"residente in {gen_res} – CAP {gen_cap}"
        )
        pdf.ln(5)

        min_nome  = sanitize_text(data.get("minore_nome", ""))
        min_cf    = sanitize_text(data.get("minore_cf", ""))
        min_luogo = sanitize_text(data.get("minore_luogo_nascita", ""))
        min_dn    = sanitize_text(data.get("minore_data_nascita", ""))
        min_res   = sanitize_text(data.get("minore_indirizzo", ""))
        min_cap   = sanitize_text(data.get("minore_cap", ""))

        pdf.multi_cell(
            0, 8,
            f"Minore: {min_nome} Codice Fiscale {min_cf}, nato a {min_luogo} il {min_dn}, "
            f"residente in {min_res} – CAP {min_cap}"
        )
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
    elif specialist.get("nome") == "Dott.ssa Veronica Lorenzini":
    # 1. Informativa
        pdf.cell(0, 8, f"Gentile {salutation} {full_name}", ln=True)
        pdf.set_font("DejaVu", "", 12)
        pdf.write_html_formatted(specialist.get("testo_informativa", ""))
        pdf.ln(5)

    elif "testo_informativa" in specialist:
        pdf.set_font("DejaVu", "", 12)
        testo_generico = specialist.get("testo_informativa", "")
        testo_pulito = clean_html(testo_generico)
        pdf.multi_cell(0, 8, sanitize_text(testo_pulito))
        pdf.ln(5)

    

    # 2. Dichiarazione finale configurata da specialists_config
    decl = specialist.get("dichiarazione_finale_blocco", {})
    if decl.get("attivo", False):
        # — nome e cognome (per Lorenzini: firma_nome è un unico campo, splittalo o leggi tutto)
        raw_nome = data.get("firma_nome", "")
        parts    = raw_nome.strip().split(" ", 1)
        nome     = sanitize_text(parts[0]) if parts else ""
        cognome  = sanitize_text(parts[1]) if len(parts)>1 else ""

        # — luogo_nascita & alias luogo
        luogo_nascita = sanitize_text(data.get("firma_luogo_nascita", ""))
        #luogo         = luogo_nascita

        # — data di nascita  
        data_nascita  = sanitize_text(data.get("firma_data_nascita", ""))

        # — indirizzo (solo per chi ce l’ha)
        indirizzo     = sanitize_text(data.get("indirizzo", ""))
        if decl.get("pagina_nuova", False):
           pdf.add_page()
        # format: includo TUTTE le chiavi usate nei template
        testo = decl["template"].format(
            nome=nome,
            cognome=cognome,
            luogo_nascita=luogo_nascita,   # <--- qui
            luogo=luogo,
            #firma_luogo=firma_luogo,# <--- alias per eventuali template legacy
            data_nascita=data_nascita,
            indirizzo=indirizzo,
            tutore=tutore,
            paziente=paziente
        )

        pdf.multi_cell(0, 8, sanitize_text(testo))
        pdf.ln(9)
                # 2.a Data di presa visione (solo per chi ce l’ha)
      #  data_vis = sanitize_text(data.get("firma_data", ""))
      #  if data_vis:
       #     pdf.cell(0, 8, f"Data presa visione: {data_vis}", ln=True)
        #    pdf.ln(5)

    
        

# 4. Consensi (solo se presenti)
    pdf.ln()
    if specialist.get("new_page_for_signatures", False):
        pdf.add_page()
    if specialist.get("consensi"):
        pdf.set_font("DejaVu", "B", 12)
        if specialist["nome"] != "Dott.ssa Serioli":
            pdf.ln(20)
            pdf.cell(0, 10, "Dichiaro inoltre di:", ln=True)
        pdf.set_font("DejaVu", "", 12)
        for consenso in specialist["consensi"]:
            scelta = sanitize_text(data.get(consenso["campo"], ""))
            frase = f"{scelta} {consenso['label']}"
            pdf.multi_cell(0, 8, frase)
            pdf.ln(1)
    
    # 6. Luogo e data
    firma_luogo = sanitize_text(data.get("firma_luogo", ""))
    if firma_luogo:
        pdf.cell(0, 10, f"Luogo: {firma_luogo}", ln=True)
    if data_firma:
        pdf.cell(0, 10, f"Data: {data_firma}", ln=True)


    # ——— Inizio inserimento firme ———
    positions = specialist.get("signature_positions", [])
    num       = specialist.get("firme", 0)

    # Calcolo fallback spacing per gli altri specialisti
    usable  = pdf.w - pdf.l_margin - pdf.r_margin
    spacing = (usable / (num + 1)) if num else 0

    for i in range(num):
        sig_key = f"firma{i+1}"
        lab_key = f"firma_label{i+1}"
        sig_data = data.get(sig_key, "")
        if not sig_data:
            continue

        # 1) Decodifica Data-URL → PNG temporaneo
        header, b64 = sig_data.split(",", 1)
        img_bytes   = base64.b64decode(b64)
        tmp         = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        tmp.write(img_bytes); tmp.close()
        img_path    = tmp.name

        # 2) Scegli X,Y in base allo specialista
        if i < len(positions):
            # Scattolini: posizioni fisse nella stessa pagina
            x, y = positions[i]
        else:
            # Tutti gli altri: fallback equidistante
            x = pdf.l_margin + spacing * (i + 1)
            y = pdf.get_y()

        # 3) Etichetta subito sopra la firma
        pdf.set_xy(x, y - 6)
        pdf.set_font("DejaVu", "B", 10)
        label = data.get(lab_key) or specialist["etichette_firme"][i]
        pdf.cell(60, 5, sanitize_text(label), ln=0)

        # 4) Stampa l’immagine della firma
        pdf.image(img_path, x=x, y=y, w=60)

        # 5) Pulizia
        os.remove(img_path)
        pdf.ln(2)

    # ——— Fine inserimento firme ———

# Se siamo nel template di Scattolini (specialist_id == "3"), stampiamo i valori dinamici:
    if specialist_id == "3":
    # 1) Presa visione
    # 20 mm dal margine superiore
        y0 = pdf.t_margin 
        pdf.set_xy(pdf.l_margin, y0)

        # 1) Presa visione
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Per presa visione: " + data.get("presa_visione_data", ""), ln=True)

    # 2) Primo blocco ruolo
        mapping_ruolo = {
        "paziente": "Paziente",
        "tutore": "ADS/tutore/esercente responsabilità genitoriale",
        "persona_riferimento": "Persona di riferimento"
        }
        mapping_ruolo2 = {
        "paziente2": "Paziente",
        "tutore2": "ADS/tutore/esercente responsabilità genitoriale",
        "persona_riferimento2": "Persona di riferimento"
        }
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(90, 8, "Il sottoscritto in qualità di: ", ln=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, mapping_ruolo.get(data.get("ruolo"), ""), ln=1)

    # Autorizzazione
        raw = data.get("autorizzazione", "").lower()    # es. "si" o "no"
        mapping = {
            "autorizza":       "Autorizza",
            "non autorizza":   "Non autorizza",
            "si":               "Autorizza",
            "no":               "Non autorizza"
        }
        auth_label = mapping.get(raw, data.get("autorizzazione", ""))
        pdf.ln(2)
        #pdf.set_font("Arial", "B", 12)
        #pdf.cell(40, 8, "Autorizzazione: ", ln=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(40, 8, auth_label, ln=1)

    # 3) Destinatari info
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 8, "la Dott.ssa Linda Scattolini a fornire informazioni riguardanti il proprio stato di salute a:")
        pdf.set_font("Arial", "", 12)
        pdf.cell(40, 8, "Medico di Medicina Generale dott./dott.ssa " + data.get("medico_generale", ""), ln=1)
        pdf.cell(40, 8, "Medico specialista dott./dott.ssa "      + data.get("medico_specialista", ""), ln=1)
        pdf.cell(40, 8, "Al/alla Sig./Sig.ra "                   + data.get("al_sig", ""), ln=1)

        # Linea orizzontale
        y = pdf.get_y() + 4
        pdf.line(10, y, 200, y)

        # 4) Seconda sezione ruolo + data
        pdf.ln(6)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(90, 8, "Il sottoscritto in qualità di: ", ln=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, mapping_ruolo2.get(data.get("ruolo2"), ""), ln=1)

        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 8, "Data: ", ln=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(40, 8, data.get("seconda_data", ""), ln=1)

        # 5) Acquisizione verbale + data
        pdf.ln(4)
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(80, 8, "Acquisizione verbale del consenso per impossibilità fisica alla firma")
        pdf.ln(2)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(40, 8, "Data: ", ln=0)
        pdf.set_font("Arial", "", 12)
        pdf.cell(40, 8, data.get("verbale_data", ""), ln=1)


    # Salvataggio
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{specialist['nome'].replace(' ', '_')}_{timestamp}.pdf"
    path = os.path.join(output_dir, filename)
    pdf.output(path)

    return path
