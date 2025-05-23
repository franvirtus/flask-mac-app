from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from specialists_config import specialists
from pdf_generator_10_05 import generate_pdf
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

app = Flask(__name__)
app.secret_key = "secret"

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
            14: {"nome": "Dott. Buizza"},
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
            6: {"nome": "Dott.ssa Chiara Morelli"},
            7: {"nome": "Dott.ssa Morelli"}
        }
    else:
        specialists = {}

    return render_template("area.html", area=area.replace('_', ' ').title(), specialists=specialists)


@app.route("/")
def home():
    return render_template("home_13_04.html")

@app.route("/privacy/<specialist_id>", methods=["GET"])
def show_form(specialist_id):
    specialist = specialists.get(specialist_id)
    # se c’è ma enabled==False, lo faccio diventare “non definito”
    if specialist and not specialist.get("enabled", True):
        specialist = None

    return render_template(
        "form_unico.html",
        specialist_id=specialist_id,
        specialist=specialist
    )
@app.route("/submit/<specialist_id>", methods=["POST"])
def submit_form(specialist_id):
    # Importante: Assicurarsi che specialist_id sia una stringa
    specialist = specialists.get(specialist_id)
    if not specialist:
        return "Specialista non trovato", 404

    data = dict(request.form)
    data["timestamp"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Gestione firme
    for i in range(specialist["firme"]):
        firma_key = f"firma{i+1}"
        if not request.form.get(firma_key):
            flash("Tutte le firme sono obbligatorie")
            return redirect(url_for("show_form", specialist_id=specialist_id))
        # Salva la firma in data
        data[firma_key] = request.form.get(firma_key)

    # Generazione PDF - corretta l'ordine dei parametri
    pdf_path = generate_pdf(data, specialist, specialist_id, OUTPUT_DIR)
    
    pdf_filename = f"{specialist['nome'].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

    # Ritorna il file corretto (salvato su disco)
# Mostra pagina di conferma
    return render_template(
        "conferma.html",
        path_pdf=pdf_path,
        nome_file=pdf_filename
        )


@app.route("/send_email", methods=["POST"])
def send_email():
    destinatario = request.form.get("email")
    pdf_path = request.form.get("pdf_path")
    pdf_name = request.form.get("pdf_name") or os.path.basename(pdf_path)

    if not destinatario or not os.path.exists(pdf_path):
        return "Errore: email mancante o file PDF non trovato", 400

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

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login("privacyvirtusgroup@gmail.com", "smem zaak ubkm yvlc")
            smtp.sendmail(msg["From"], msg["To"], msg.as_string())

        return render_template("conferma.html", destinatario=destinatario, path_pdf=pdf_path, nome_file=pdf_name)


    except Exception as e:
        return f"Errore nell'invio email: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
