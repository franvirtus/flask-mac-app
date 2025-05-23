import os
import datetime
import base64
import smtplib
from flask import Flask, request, render_template_string
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pdfkit

# ========================
# CONFIGURAZIONE
# ========================
EMAIL_USERNAME = "privacyvirtusgroup@gmail.com"
EMAIL_PASSWORD = "smem zaak ubkm yvlc"
SHARED_FOLDER = r"C:\\Salvataggio privacy"
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")
PORT = 8080

# ========================
# APP E DATI
# ========================
app = Flask(__name__)
specialist_names = {
    "1": "Dott. Messineo",
    "2": "Dott.ssa Lorenzini",
    "3": "Dott. Verdi",
    "4": "Dott. Neri"
}
privacy_texts = {
    "1": """Informativa Messineo...""",
    "2": """Informativa Lorenzini...""",
    "3": """Informativa Verdi...""",
    "4": """Informativa Neri..."""
}

# ========================
# HOME
# ========================
@app.route('/')
def home():
    buttons = ''.join([
        f'<button onclick="window.location.href=\'/privacy/{k}\'">{v}</button><br>'
        for k, v in specialist_names.items()
    ])
    return render_template_string(f"""
        <h1>Benvenuto nell'app di gestione privacy</h1>
        <img src='/static/logo.png' width='150'><br>
        <p>Via Montello 79, Brescia - info@virtusbrixia.com</p>
        <hr>
        {buttons}
    """)

# ========================
# PRIVACY PAGE
# ========================
@app.route('/privacy/<specialist>')
def privacy(specialist):
    spec_name = specialist_names.get(specialist, "Specialista")
    text = privacy_texts.get(specialist, "Informativa non disponibile.")

    extra = """<form method='get' action='/form'>
    <label><input type='radio' name='consenso1' value='acconsento' required> Acconsento al trattamento (punto A)</label><br>
    <label><input type='radio' name='consenso2' value='acconsento' required> Acconsento alle finalità statistiche (punto C)</label><br>
    <label><input type='radio' name='consenso3' value='acconsento' required> Acconsento comunicazione dati a familiari / sanitari</label><br>
    <input type='hidden' name='specialist' value='2'>
    <input type='submit' value='Continua'>
    </form>""" if specialist == "2" else f"<a href='/form?specialist={specialist}'><button>Accetto</button></a>"

    return render_template_string(f"""
        <h1>Modulo Informativa - {spec_name}</h1>
        <div style='max-width:800px;margin:auto;text-align:left;'>
        <p>{text}</p>
        {extra}
        </div>
    """)

# ========================
# FORM DATI E FIRMA
# ========================
@app.route('/form')
def form():
    specialist = request.args.get('specialist', '1')
    consenso1 = request.args.get('consenso1', '')
    consenso2 = request.args.get('consenso2', '')
    consenso3 = request.args.get('consenso3', '')

    return render_template_string(f"""
        <h1>Inserisci i tuoi dati</h1>
        <form action='/submit' method='post'>
            Nome: <input name='nome' required><br>
            Cognome: <input name='cognome' required><br>
            Residente a: <input name='residenza' required><br>
            Via: <input name='via' required><br>
            Codice Fiscale: <input name='codice_fiscale' pattern='[A-Za-z0-9]{{16}}' required><br>
            Data di nascita: <input name='data_nascita' placeholder='gg/mm/aaaa' required><br>
            Firma: <input name='firma' placeholder='(base64 png)' required><br>
            <input type='hidden' name='specialist' value='{specialist}'>
            <input type='hidden' name='consenso1' value='{consenso1}'>
            <input type='hidden' name='consenso2' value='{consenso2}'>
            <input type='hidden' name='consenso3' value='{consenso3}'>
            <input type='submit'>
        </form>
    """)

# ========================
# SUBMIT: CREA PDF
# ========================
@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    cognome = request.form['cognome']
    residenza = request.form['residenza']
    via = request.form['via']
    codice_fiscale = request.form['codice_fiscale']
    data_nascita = request.form['data_nascita']
    firma_data = request.form['firma']
    specialist = request.form['specialist']
    consenso1 = request.form.get('consenso1', '')
    consenso2 = request.form.get('consenso2', '')
    consenso3 = request.form.get('consenso3', '')
    data = datetime.datetime.now().strftime('%d/%m/%Y')

    sig = f"<img src='{firma_data}' width='200'>" if firma_data.startswith("data:image") else "Firma non disponibile"

    folder_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    path_folder = os.path.join(SHARED_FOLDER, folder_name)
    os.makedirs(path_folder, exist_ok=True)
    filename = f"{nome}_{cognome}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(path_folder, filename)

    if specialist == "2":
        html = f"""
        <h1>Modulo Consenso - {nome} {cognome}</h1>
        <p>Nato/a il {data_nascita}, residente a {residenza}, via {via}</p>
        <p><strong>Firma:</strong> {sig}</p>
        <p>Consenso statistica: {consenso2} <br> Consenso informativo: {consenso1} <br> Comunicazione dati: {consenso3}</p>
        <p>Data: {data}</p>
        """
    else:
        text = privacy_texts.get(specialist, '')
        html = f"""
        <h1>Informativa {specialist_names.get(specialist)}</h1>
        <p>{text}</p>
        <hr>
        <p>Io sottoscritto {nome} {cognome}, CF {codice_fiscale}, nato/a il {data_nascita}, residente a {residenza}, via {via}, acconsento al trattamento dei dati.</p>
        <p><strong>Firma:</strong><br>{sig}</p>
        <p>Data: {data}</p>
        """

    pdfkit.from_string(html, path, configuration=pdfkit_config)
    return render_template_string(f"""
        <h1>Grazie, {nome}!</h1>
        <p>PDF generato: <strong>{filename}</strong></p>
        <form action='/send_email' method='post'>
            Email destinatario: <input name='destinatario' required><br>
            <input type='hidden' name='pdf_path' value='{path}'>
            <input type='submit' value='Invia PDF via email'>
        </form>
        <a href='/'>Torna alla home</a>
    """)

# ========================
# EMAIL
# ========================
@app.route('/send_email', methods=['POST'])
def send_email():
    to = request.form['destinatario']
    path = request.form['pdf_path']
    filename = os.path.basename(path)

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to
    msg['Subject'] = f"Documento firmato: {filename}"

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(open(path, 'rb').read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
    msg.attach(part)

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"<h1>Email inviata a {to}</h1><a href='/'>Torna alla home</a>"
    except Exception as e:
        return f"<h1>Errore invio: {e}</h1>"

# ========================
# AVVIO
# ========================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=PORT)
