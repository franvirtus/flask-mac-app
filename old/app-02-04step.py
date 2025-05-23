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
# 1) Configurazione
# ==========================
EMAIL_USERNAME = "privacyvirtusgroup@gmail.com"
EMAIL_PASSWORD = "smem zaak ubkm yvlc"  # Usa App Password, non la tua reale
SHARED_FOLDER = r"C:\\Salvataggio privacy"
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

app = Flask(__name__)
current_year = datetime.datetime.now().year

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
    "1": """1. I dati sensibili da Lei forniti verranno trattati secondo i principi di liceità...""",
    "2": """INFORMATIVA AI SENSI DELL'ART. 13 DEL REG. UE 2016/679...""",
    "3": "[Informativa Dott. Verdi da completare]",
    "4": "[Informativa Dott. Neri da completare]"
}

# ==========================
# 3) Route homepage
# ==========================
@app.route('/')
def home():
    return '''<h1>Benvenuto nell'app di gestione privacy</h1><p>Vai su /privacy/1 ad esempio</p>'''

# ==========================
# 4) Route per informativa
# ==========================
@app.route('/privacy/<specialist>')
def privacy(specialist):
    name = specialist_names.get(specialist, "Specialista")
    text = privacy_texts.get(specialist, "Informativa non trovata")
    extra = """
    <form method='get' action='/form'>
      <input type='hidden' name='specialist' value='2'>
      <label><input type='radio' name='consenso1' value='acconsento' required> Acconsento (punto A)</label><br>
      <label><input type='radio' name='consenso2' value='acconsento' required> Acconsento (punto C)</label><br>
      <label><input type='radio' name='consenso3' value='acconsento' required> Acconsento (familiari/sanitari)</label><br>
      <button type='submit'>Procedi</button>
    </form>""" if specialist == "2" else f"<a href='/form?specialist={specialist}'>Accetta e compila il modulo</a>"

    return f"""
    <h1>Modulo Informativa - {name}</h1>
    <div style='max-width:800px'>{text}</div>
    {extra}
    """

# ==========================
# 5) Route form
# ==========================
@app.route('/form')
def form():
    specialist = request.args.get('specialist', '1')
    consenso1 = request.args.get('consenso1', '')
    consenso2 = request.args.get('consenso2', '')
    consenso3 = request.args.get('consenso3', '')
    return render_template_string(open('form_template.html').read(),
                                  specialist=specialist,
                                  current_year=current_year,
                                  consenso1=consenso1,
                                  consenso2=consenso2,
                                  consenso3=consenso3)

# ==========================
# 6) Route submit + PDF
# ==========================
@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form['nome']
    cognome = request.form['cognome']
    cf = request.form['codice_fiscale']
    giorno = request.form['birth_day']
    mese = request.form['birth_month']
    anno = request.form['birth_year']
    via = request.form['via']
    residenza = request.form['residenza']
    firma = request.form['signature_data']
    specialist = request.form['specialist']
    consenso1 = request.form.get('consenso1', '')
    consenso2 = request.form.get('consenso2', '')
    consenso3 = request.form.get('consenso3', '')

    data_nascita = f"{giorno}/{mese}/{anno}"
    luogo = "Brescia"
    oggi = datetime.datetime.now().strftime('%d/%m/%Y')

    firma_tag = f"<img src='{firma}' width='200' />" if firma.startswith('data:image') else '<i>Nessuna firma</i>'

    html = f"""<h2>Dati Paziente</h2>
    <p><b>Nome:</b> {nome} {cognome}<br>
    <b>CF:</b> {cf}<br>
    <b>Nato il:</b> {data_nascita}<br>
    <b>Residente a:</b> {residenza}, via {via}<br>
    <b>Luogo e Data:</b> {luogo}, {oggi}</p>
    <p>{firma_tag}</p>
    """

    if specialist == "2":
        html += f"""
        <hr>
        <h3>Consensi:</h3>
        <ul>
            <li>Punto A: {consenso1}</li>
            <li>Punto C: {consenso2}</li>
            <li>Familiari/Sanitari: {consenso3}</li>
        </ul>"""

    folder = os.path.join(SHARED_FOLDER, specialist_names.get(specialist, 'Generico'))
    os.makedirs(folder, exist_ok=True)
    nome_file = f"{nome}_{cognome}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    percorso = os.path.join(folder, nome_file)
    pdfkit.from_string(html, percorso, configuration=pdfkit_config)

    return f"""<h1>PDF creato: {nome_file}</h1>
              <form method='post' action='/send_email'>
                <input type='email' name='destinatario' placeholder='Email' required>
                <input type='hidden' name='pdf_path' value='{percorso}'>
                <input type='submit' value='Invia PDF via email'>
              </form>
              <a href='/'>Torna alla home</a>"""

# ==========================
# 7) Invio Email
# ==========================
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
        return f"Email inviata a {to}. <a href='/'>Home</a>"
    except Exception as e:
        return f"Errore invio: {str(e)}"

# ==========================
# 8) Avvio
# ==========================
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
