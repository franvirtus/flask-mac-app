from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify
from specialists_config import specialists
from pdf_generator_16_04 import generate_pdf
import os
import base64
import io
import datetime
import smtplib
from email.message import EmailMessage

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.mime.text import MIMEText
import logging

app = Flask(__name__)
app.secret_key = "secret"

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route('/home_13_04')
def home_13_04():
    return render_template('home_13_04.html')  # Nuova versione

@app.route("/area/<area>")
def area_page(area):
    if area == "nutrizione":
        specialists = {
            1: {"nome": "Dott. Gaetano Messineo"},
            7: {"nome": "Dott. Buizza"},
            8: {"nome": "Dott. Cucchi"},
            9: {"nome": "Dott. Nicolini"}
        }
    elif area == "osteopatia_pediatrica":
        specialists = {
        2: {"nome": "Dott.ssa Veronica Lorenzini"}
        }
    elif area == "osteopatia":
        specialists = {
        10: {"nome": "Dott. Tognazzi"}
        }
    elif area == "fisioterapia":
        specialists = {
        11: {"nome": "Dott. Mosconi"}
        }
    elif area == "ortottica":
        specialists = {
        12: {"nome": "Dott. Strano"}
        }
    elif area == "massoterapia":
        specialists = {
        13: {"nome": "Dott. Lorenzo Quaresima"}
        }
    elif area == "logopedia":
        specialists = {
        4: {"nome": "Dott.ssa Serioli"}
        }
    elif area == "ostetricia":
        specialists = {
        3: {"nome": "Dott.ssa Scattolini"}
        }
    elif area == "chinesiologia":
        specialists = {
            5: {"nome": "Dott. Luca Taesi"},
            6: {"nome": "Dott.ssa Chiara Morelli"}
        }
    else:
        specialists = {}

    return render_template("area.html", area=area.replace('_', ' ').title(), specialists=specialists)

@app.route("/")
def home():
    return render_template("home_13_04.html")

@app.route("/privacy/<specialist_id>", methods=["GET"])
def show_form(specialist_id):
    try:
        # Converti l'ID in intero per il lookup
        specialist_id_int = int(specialist_id)
        specialist = specialists.get(specialist_id_int)
        
        logger.debug(f"Accesso alla privacy dello specialista ID: {specialist_id_int}")
        logger.debug(f"Specialista trovato: {specialist is not None}")
        
        if not specialist:
            logger.error(f"Specialista non trovato con ID: {specialist_id_int}")
            flash("Specialista non trovato")
            return redirect(url_for("home"))
            
        return render_template("form_unico.html", specialist_id=specialist_id, specialist=specialist)
    except Exception as e:
        logger.error(f"Errore nella visualizzazione del form: {str(e)}")
        flash(f"Si è verificato un errore: {str(e)}")
        return redirect(url_for("home"))

@app.route("/submit/<specialist_id>", methods=["POST"])
def submit_form(specialist_id):
    try:
        # Converti l'ID in intero per il lookup
        specialist_id_int = int(specialist_id)
        specialist = specialists.get(specialist_id_int)
        
        if not specialist:
            logger.error(f"Specialista non trovato con ID: {specialist_id_int}")
            return "Specialista non trovato", 404

        data = dict(request.form)
        data["timestamp"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        # Gestione firme
        for i in range(specialist.get("firme", 0)):
            firma_key = f"firma{i+1}"
            if not request.form.get(firma_key):
                flash("Tutte le firme sono obbligatorie")
                return redirect(url_for("show_form", specialist_id=specialist_id))
            # Salva la firma in data
            data[firma_key] = request.form.get(firma_key)

        # Generazione PDF
        pdf_path = generate_pdf(data, specialist, specialist_id, OUTPUT_DIR)
        
        pdf_filename = os.path.basename(pdf_path)

        # Mostra pagina di conferma
        return render_template(
            "conferma.html",
            path_pdf=pdf_path,
            nome_file=pdf_filename
        )
    except Exception as e:
        logger.error(f"Errore nella generazione del PDF: {str(e)}")
        flash(f"Si è verificato un errore: {str(e)}")
        return redirect(url_for("show_form", specialist_id=specialist_id))

@app.route("/download_pdf/<path:pdf_path>")
def download_pdf(pdf_path):
    return send_file(pdf_path, as_attachment=True)

@app.route("/send_email", methods=["POST"])
def send_email():
    destinatario = request.form.get("email")
    pdf_path = request.form.get("pdf_path")
    
    logger.debug(f"Richiesta invio email ricevuta: {destinatario}, {pdf_path}")
    
    if not destinatario:
        flash("Inserisci un indirizzo email valido")
        return redirect(url_for("home"))
        
    if not pdf_path or not os.path.exists(pdf_path):
        logger.error(f"File non trovato: {pdf_path}")
        flash("File PDF non trovato")
        return redirect(url_for("home"))
    
    pdf_name = os.path.basename(pdf_path)

    try:
        # Costruzione messaggio email
        msg = MIMEMultipart()
        msg["From"] = "privacyvirtusgroup@gmail.com"
        msg["To"] = destinatario
        msg["Subject"] = "Modulo Informativa Privacy"
        msg.attach(MIMEText("In allegato trovi il modulo firmato.", "plain"))

        # Allegato PDF
        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={pdf_name}")
            msg.attach(part)

        # Utilizzo di SMTP_SSL con porto 465
        logger.debug("Tentativo di connessione a smtp.gmail.com")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            logger.debug("Connessione stabilita, tentativo di login")
            smtp.login("privacyvirtusgroup@gmail.com", "smem zaak ubkm yvlc")
            logger.debug("Login riuscito, invio email")
            smtp.sendmail(msg["From"], msg["To"], msg.as_string())
            logger.debug("Email inviata con successo")

        flash(f"Email inviata con successo a {destinatario}!")
        return redirect(url_for("home"))

    except Exception as e:
        logger.error(f"Errore nell'invio email: {str(e)}")
        flash(f"Errore nell'invio email: {str(e)}")
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5050)
