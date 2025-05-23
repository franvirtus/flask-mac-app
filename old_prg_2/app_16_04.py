from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from specialists_config import specialists
from pdf_generator_16_04 import generate_pdf
import os
import base64
import io
import datetime

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
    return render_template("home_13_04.html", specialists=specialists)

@app.route("/privacy/<specialist_id>", methods=["GET"])
def show_form(specialist_id):
    specialist = specialists.get(specialist_id)

    return render_template("form_unico.html", specialist_id=specialist_id, specialist=specialist)

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


if __name__ == "__main__":
    app.run(debug=True, port=5050)
