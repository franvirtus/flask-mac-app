from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from specialists_config import specialists
from pdf_generator_13_04_CORRETTO_OK import generate_pdf
import os
import base64
import io
import datetime

app = Flask(__name__)
app.secret_key = "secret"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/")
def home():
    return render_template("home.html", specialists=specialists)

@app.route("/privacy/<specialist_id>", methods=["GET"])
def show_form(specialist_id):
    specialist = specialists.get(specialist_id)
    if not specialist:
        return "Specialista non trovato", 404
    return render_template("form_unico.html", specialist_id=specialist_id, specialist=specialist)

@app.route("/submit/<specialist_id>", methods=["POST"])
def submit_form(specialist_id):
    specialist = specialists.get(specialist_id)
    if not specialist:
        return "Specialista non trovato", 404

    data = dict(request.form)
    data["timestamp"] = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Gestione firme
    firme = []
    for i in range(specialist["firme"]):
        firma = request.form.get(f"firma{i+1}")
        if not firma:
            flash("Tutte le firme sono obbligatorie")
            return redirect(url_for("show_form", specialist_id=specialist_id))
        firme.append(firma)

    # Generazione PDF
    pdf_filename = f"{specialist['nome'].replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf_path = generate_pdf(specialist, data, firme, OUTPUT_DIR)

    # Ritorna il file corretto (salvato su disco)
    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=pdf_filename
    )


    # Invio email (placeholder)
    # send_email(specialist['email'], pdf_path)

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=pdf_filename
    )


    


if __name__ == "__main__":
    app.run(debug=True, port=5050)
