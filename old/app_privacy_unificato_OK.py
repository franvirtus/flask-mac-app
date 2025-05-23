import datetime
import base64
import os

from flask import Flask, render_template_string, request
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ==========================
# 1) Parametri interni
# ==========================
EMAIL_USERNAME = "privacyvirtusgroup@gmail.com"
EMAIL_PASSWORD = "smem zaak ubkm yvlc"
SHARED_FOLDER = r"C:\\Salvataggio privacy"
HOST = "0.0.0.0"
PORT = 8080

# ==========================
# 2) Dizionari
# ==========================
specialist_names = {
    "1": "Dott. Messineo",
    "2": "Dott.ssa Lorenzini",
    "3": "Dott. Verdi",
    "4": "Dott. Neri"
}

privacy_texts = {
    "1": """<p>1. I dati sensibili da Lei forniti verranno trattati... [OMESSO PER BREVITÀ]</p>""",
    "2": """<p>INFORMATIVA AI SENSI DELL'ART. 13 DEL REG. UE 2016/679...</p>""",
    "3": "[Informativa Dott. Verdi da inserire qui]",
    "4": "[Informativa Dott. Neri da inserire qui]"
}

# ==========================
# 3) Inizializza Flask e pdfkit
# ==========================
app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

current_year = datetime.datetime.now().year

# ==========================
# 4) Homepage con tasti
# ==========================
home_template = '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Seleziona lo Specialista</title></head>
<body>
  <h1>Seleziona lo Specialista</h1>
  <button onclick="window.location.href='/privacy/1'">Dott. Messineo</button>
  <button onclick="window.location.href='/privacy/2'">Dott.ssa Lorenzini</button>
  <button onclick="window.location.href='/privacy/3'">Dott. Verdi</button>
  <button onclick="window.location.href='/privacy/4'">Dott. Neri</button>
</body></html>
'''

@app.route('/')
def home():
    return render_template_string(home_template)

# ==========================
# 5) Pagina privacy + consenso Lorenzini
# ==========================
privacy_template = '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Informativa {{ specialist_name }}</title></head>
<body>
  <h1>Informativa {{ specialist_name }}</h1>
  <div>{{ privacy_text|safe }}</div>
  {% if specialist == '2' %}
  <form action="/form" method="get">
    <p><input type="radio" name="consenso1" value="acconsento" required> Acconsento al trattamento (punto A)</p>
    <p><input type="radio" name="consenso2" value="acconsento" required> Acconsento alle finalità (punto C)</p>
    <p><input type="radio" name="consenso3" value="acconsento" required> Acconsento comunicazione dati a familiari / sanitari</p>
    <input type="hidden" name="specialist" value="2">
    <button type="submit">Accetto</button>
  </form>
  {% else %}
  <a href="/form?specialist={{ specialist }}"><button>Accetto</button></a>
  {% endif %}
</body>
</html>
'''

@app.route('/privacy/<specialist>')
def privacy_view(specialist):
    return render_template_string(
        privacy_template,
        specialist_name=specialist_names.get(specialist, 'Specialista'),
        privacy_text=privacy_texts.get(specialist, ''),
        specialist=specialist
    )

# ==========================
# 6) Form dati utente (valida specialist = 1 o 2)
# ==========================
form_template = '''
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Modulo dati</title></head>
<body>
  <h1>Inserisci i tuoi dati</h1>
  <form action="/submit" method="post">
    <input name="nome" placeholder="Nome" required><br>
    <input name="cognome" placeholder="Cognome" required><br>
    <input name="codice_fiscale" placeholder="Codice Fiscale" required maxlength="16"><br>
    <input name="birth_day" placeholder="Giorno" required size="2">
    <input name="birth_month" placeholder="Mese" required size="2">
    <input name="birth_year" placeholder="Anno" required size="4"><br>
    <input type="hidden" name="specialist" value="{{ specialist }}">
    {% if specialist == '2' %}
      <input type="hidden" name="consenso1" value="acconsento">
      <input type="hidden" name="consenso2" value="acconsento">
      <input type="hidden" name="consenso3" value="acconsento">
    {% endif %}
    <input type="submit" value="Invia">
  </form>
</body></html>
'''

@app.route('/form')
def show_form():
    specialist = request.args.get("specialist", "1")
    return render_template_string(form_template, specialist=specialist)

# ==========================
# 7) Submit + genera PDF
# ==========================
@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    cognome = request.form['cognome']
    codice_fiscale = request.form['codice_fiscale']
    birth_day = request.form['birth_day']
    birth_month = request.form['birth_month']
    birth_year = request.form['birth_year']
    specialist = request.form['specialist']

    data_nascita = f"{birth_day}/{birth_month}/{birth_year}"
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    consenso1 = request.form.get("consenso1", "")
    consenso2 = request.form.get("consenso2", "")
    consenso3 = request.form.get("consenso3", "")

    text_privacy = privacy_texts.get(specialist, "")
    folder = os.path.join(SHARED_FOLDER, specialist_names.get(specialist, 'Specialista'))
    os.makedirs(folder, exist_ok=True)
    filename = f"{nome}_{cognome}_{timestamp}.pdf"
    pdf_path = os.path.join(folder, filename)

    html = f"""
    <html><body>
    <h1>Informativa {specialist_names.get(specialist)}</h1>
    <p>{text_privacy}</p><hr>
    <p>Io sottoscritto/a {nome} {cognome}, CF {codice_fiscale}, nato/a il {data_nascita},
    dopo avere letto l'informativa, do il consenso al trattamento.</p>
    """
    if specialist == "2":
        html += f"""
        <h2>Dichiarazioni specifiche</h2>
        <p>Consenso A: {consenso1}</p>
        <p>Consenso C: {consenso2}</p>
        <p>Consenso comunicazione: {consenso3}</p>
        """
    html += f"<p>Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</p></body></html>"

    pdfkit.from_string(html, pdf_path, configuration=pdfkit_config)
    return f"<h1>PDF generato: {filename}</h1><a href='/'>Torna alla Home</a>"

# ==========================
# 8) Avvio server
# ==========================
if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)

