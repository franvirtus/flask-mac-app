import datetime
import base64
import os

from flask import Flask, render_template_string, request
import pdfkit

# === CONFIG ===
EMAIL_USERNAME = "privacyvirtusgroup@gmail.com"
EMAIL_PASSWORD = "smem zaak ubkm yvlc"
SHARED_FOLDER = r"C:\\Salvataggio privacy"
HOST = "0.0.0.0"
PORT = 8080

# === FLASK INIT ===
app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
current_year = datetime.datetime.now().year

# === SPECIALISTI ===
specialist_names = {
    "1": "Dott. Messineo",
    "2": "Dott.ssa Lorenzini",
    "3": "Dott. Verdi",
    "4": "Dott. Neri"
}

privacy_texts = {
    "1": "[Testo privacy Messineo]",
    "2": "[Testo privacy Lorenzini]",
    "3": "[Testo privacy Verdi]",
    "4": "[Testo privacy Neri]"
}

# === TEMPLATE HOMEPAGE ===
home_template = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Home</title></head>
<body>
<h1>Seleziona Specialista</h1>
<button onclick="location.href='/privacy/1'">Messineo</button>
<button onclick="location.href='/privacy/2'">Lorenzini</button>
<button onclick="location.href='/privacy/3'">Verdi</button>
<button onclick="location.href='/privacy/4'">Neri</button>
</body></html>
'''

# === TEMPLATE PRIVACY ===
privacy_template = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Privacy</title></head>
<body>
<h1>Modulo Informativa - {{ specialist_name }}</h1>
<div>{{ privacy_text | safe }}</div>
{% if specialist == '2' %}
<form method="get" action="/form">
  <label><input type="radio" name="consenso1" value="acconsento" required> Trattamento (A)</label><br>
  <label><input type="radio" name="consenso2" value="acconsento" required> Statistiche (C)</label><br>
  <label><input type="radio" name="consenso3" value="acconsento" required> Familiari/sanitari</label><br>
  <input type="hidden" name="specialist" value="2">
  <button type="submit">Accetto</button>
</form>
{% else %}
<form method="get" action="/form">
  <input type="hidden" name="specialist" value="{{ specialist }}">
  <button type="submit">Accetto</button>
</form>
{% endif %}
</body></html>
'''

# === TEMPLATE FORM ===
form_template = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Dati</title></head>
<body>
<h1>Inserisci i tuoi dati</h1>
<form action="/submit" method="post">
  Nome: <input name="nome" required><br>
  Cognome: <input name="cognome" required><br>
  CF: <input name="codice_fiscale" required><br>
  Residente a: <input name="residenza" required><br>
  Via: <input name="via" required><br>
  Data nascita: <input name="birth_day" size=2 required> / <input name="birth_month" size=2 required> / <input name="birth_year" size=4 required><br>
  <input type="hidden" name="specialist" value="{{ specialist }}">
  {% if specialist == '2' %}
  <input type="hidden" name="consenso1" value="{{ consenso1 }}">
  <input type="hidden" name="consenso2" value="{{ consenso2 }}">
  <input type="hidden" name="consenso3" value="{{ consenso3 }}">
  {% endif %}
  <input type="submit" value="Genera PDF">
</form>
</body></html>
'''

# === TEMPLATE CONFERMA ===
confirm_template = '''
<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Conferma</title></head>
<body>
<h1>PDF generato</h1>
<p>{{ pdf_file }}</p>
<a href="/">Torna all'inizio</a>
</body></html>
'''

@app.route('/')
def home():
    return render_template_string(home_template)

@app.route('/privacy/<specialist>')
def privacy_view(specialist):
    return render_template_string(
        privacy_template,
        specialist=specialist,
        specialist_name=specialist_names.get(specialist, "Specialista"),
        privacy_text=privacy_texts.get(specialist, "[Testo mancante]")
    )

@app.route('/form')
def show_form():
    specialist = request.args.get('specialist', '1')
    return render_template_string(
        form_template,
        specialist=specialist,
        consenso1=request.args.get('consenso1', ''),
        consenso2=request.args.get('consenso2', ''),
        consenso3=request.args.get('consenso3', '')
    )

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    cognome = request.form['cognome']
    codice_fiscale = request.form['codice_fiscale']
    residenza = request.form['residenza']
    via = request.form['via']
    nascita = f"{request.form['birth_day']}/{request.form['birth_month']}/{request.form['birth_year']}"
    specialist = request.form['specialist']
    data = datetime.datetime.now().strftime("%d/%m/%Y")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    consenso1 = request.form.get('consenso1', '')
    consenso2 = request.form.get('consenso2', '')
    consenso3 = request.form.get('consenso3', '')

    if specialist == "2":
        contenuto = f"""
        <h2>Modulo Consenso - Lorenzini</h2>
        <p>Io sottoscritto/a {nome} {cognome}, nato/a il {nascita}, residente a {residenza}, via {via},</p>
        <p>Do il consenso per il trattamento (punto A)</p>
        <ul>
            <li>Statistiche (C): <strong>{consenso2}</strong></li>
            <li>Informazioni (D): <strong>{consenso1}</strong></li>
            <li>Comunicazione a familiari/sanitari: <strong>{consenso3}</strong></li>
        </ul>
        <p>Luogo e data: Brescia, {data}</p>
        """
    else:
        contenuto = f"""
        <h2>Modulo Consenso - {specialist_names.get(specialist)}</h2>
        <p>Io sottoscritto/a {nome} {cognome}, CF: {codice_fiscale}, nato/a il {nascita}, residente a {residenza}, via {via}, acconsento al trattamento dei dati.</p>
        <p>Luogo e data: Brescia, {data}</p>
        """

    folder = os.path.join(SHARED_FOLDER, specialist_names.get(specialist, 'Specialista'))
    os.makedirs(folder, exist_ok=True)
    pdf_path = os.path.join(folder, f"{nome}_{cognome}_{timestamp}.pdf")

    html_doc = f"""<html><body>{contenuto}</body></html>"""
    pdfkit.from_string(html_doc, pdf_path, configuration=pdfkit_config)

    return render_template_string(confirm_template, pdf_file=pdf_path)

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
