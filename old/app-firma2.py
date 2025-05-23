import datetime
import base64
import json
import os

from flask import Flask, render_template_string, request
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ==========================
# 1) Carica la configurazione
# ==========================
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

EMAIL_USERNAME = config_data.get("EMAIL_USERNAME", "default@example.com")
EMAIL_PASSWORD = config_data.get("EMAIL_PASSWORD", "defaultpassword")
SHARED_FOLDER = config_data.get("SHARED_FOLDER", r"C:\Salvataggio privacy")
HOST = config_data.get("HOST", "0.0.0.0")
PORT = config_data.get("PORT", 5000)

# ==========================
# 2) Dizionari
# ==========================
specialist_names = {
    "1": "Dott_Rossi",
    "2": "Dott_Bianchi",
    "3": "Dott_Verdi",
    "4": "Dott_Neri"
}

privacy_texts = {
    "1": "[Informativa Dott. Rossi da inserire qui]",
    "2": "[Informativa Dott. Bianchi da inserire qui]",
    "3": "[Informativa Dott. Verdi da inserire qui]",
    "4": "[Informativa Dott. Neri da inserire qui]"
}

# ==========================
# 3) Inizializza Flask e pdfkit
# ==========================
app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Definisci l'anno corrente per i menu a tendina
current_year = datetime.datetime.now().year

# ==========================
# 4) Template Homepage ("/") con logo
# ==========================
home_template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Seleziona lo Specialista</title>
  <style>
    body {
      text-align: center;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
    }
    h1 {
      margin-bottom: 20px;
    }
    button {
      margin: 10px;
      padding: 10px 20px;
      font-size: 1.2em;
      cursor: pointer;
    }
    img {
      display: block;
      margin: 0 auto 20px auto;
      width: 150px;
    }
  </style>
</head>
<body>
  <!-- Logo visibile solo in homepage -->
  <img src="/static/logo.png" alt="Logo">
  <h1>Seleziona lo Specialista</h1>
  <button onclick="window.location.href='/privacy/1'">Dott. Rossi</button>
  <button onclick="window.location.href='/privacy/2'">Dott. Bianchi</button>
  <button onclick="window.location.href='/privacy/3'">Dott. Verdi</button>
  <button onclick="window.location.href='/privacy/4'">Dott. Neri</button>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(home_template)

# ==========================
# 5) Template Privacy ("/privacy/<specialist>")
# ==========================
privacy_template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Modulo Informativa - {{ specialist_name }}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    h1 { margin-bottom: 20px; text-align: center; }
    .content { max-width: 800px; margin: 0 auto; line-height: 1.6; }
    button {
      display: block;
      margin: 30px auto;
      padding: 10px 20px;
      font-size: 1.2em;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1>Modulo Informativa - {{ specialist_name }}</h1>
  <div class="content">
    <p>{{ privacy_text }}</p>
    <button onclick="window.location.href='/form?specialist={{ specialist }}'">Accetto</button>
  </div>
</body>
</html>
'''

@app.route('/privacy/<specialist>')
def privacy_view(specialist):
    spec_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    text = privacy_texts.get(specialist, "[Informativa da inserire qui]")
    return render_template_string(
        privacy_template,
        specialist_name=spec_name,
        privacy_text=text,
        specialist=specialist
    )

# ==========================
# 6) Template Form ("/form")
# ==========================
form_template = r'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Inserisci i tuoi dati</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        padding: 20px;
        text-align: center;
      }
      h1 { margin-bottom: 20px; }
      form {
        display: inline-block;
        text-align: left;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 8px;
      }
      label {
        display: block;
        margin-top: 10px;
        font-weight: bold;
      }
      input, select {
        font-size: 1em;
        padding: 5px;
        width: 300px;
        max-width: 100%%;
        margin-bottom: 10px;
        display: block;
      }
      input[type="submit"] {
        margin-top: 20px;
        font-size: 1.2em;
        padding: 10px 20px;
        display: block;
        margin: 20px auto 0 auto;
      }
      /* Canvas firma */
      #signature-pad {
        border: 1px solid #000;
        width: 300px;
        height: 100px;
      }
      .canvas-container {
        position: relative;
        display: inline-block;
      }
      .clear-btn {
        position: absolute;
        top: 0;
        right: 0;
        color: red;
        font-size: 18px;
        background: transparent;
        border: none;
        padding: 2px;
        cursor: pointer;
      }
      /* Stile date menù a tendina */
      .date-select.day { width: 50px; display: inline-block; }
      .date-select.month { width: 60px; display: inline-block; }
      .date-select.year { width: 80px; display: inline-block; }
      .date-sep { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Inserisci i tuoi dati</h1>
    <form action="/submit" method="post">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>
        
        <label for="cognome">Cognome:</label>
        <input type="text" id="cognome" name="cognome" required>
        
        <label for="codice_fiscale">Codice Fiscale (16 caratteri):</label>
        <input type="text" id="codice_fiscale" name="codice_fiscale" required pattern="^[A-Za-z0-9]{16}$" title="Inserisci 16 caratteri alfanumerici">
        
        <label>Data di nascita:</label>
        <div style="display: inline-block;">
          <!-- Giorno -->
          <select name="birth_day" class="date-select day" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>gg</option>
            {% for d in range(1, 32) %}
              <option value="{{ d }}">{{ '%02d'|format(d) }}</option>
            {% endfor %}
          </select>
          <span class="date-sep">/</span>
          <!-- Mese -->
          <select name="birth_month" class="date-select month" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>mm</option>
            {% for m in range(1, 13) %}
              <option value="{{ m }}">{{ '%02d'|format(m) }}</option>
            {% endfor %}
          </select>
          <span class="date-sep">/</span>
          <!-- Anno decrescente -->
          <select name="birth_year" class="date-select year" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>aaaa</option>
            {% for y in range(current_year, 1899, -1) %}
              <option value="{{ y }}">{{ y }}</option>
            {% endfor %}
          </select>
        </div>
        
        <!-- Sezione firma -->
        <label>Firma (usa la tavoletta o il dito):</label>
        <div class="canvas-container">
          <canvas id="signature-pad"></canvas>
          <button type="button" class="clear-btn" onclick="clearSignature()" title="Cancella firma">X</button>
        </div>
        <input type="hidden" id="signature_data" name="signature_data">
        
        <!-- Campo nascosto per passare lo specialista -->
        <input type="hidden" name="specialist" value="{{ specialist }}">
        
        <input type="submit" value="Invia">
    </form>
    
    <!-- Libreria Signature Pad -->
    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
    <script>
      var canvas = document.getElementById('signature-pad');
      var signaturePad = new SignaturePad(canvas);
      
      function clearSignature() {
        signaturePad.clear();
      }
      
      document.querySelector('form').addEventListener('submit', function(e) {
        if (!signaturePad.isEmpty()) {
          var dataURL = signaturePad.toDataURL();
          document.getElementById('signature_data').value = dataURL;
        } else {
          document.getElementById('signature_data').value = "";
        }
      });
    </script>
</body>
</html>
'''

@app.route('/form')
def show_form():
    specialist = request.args.get('specialist', '1')
    return render_template_string(form_template, specialist=specialist, current_year=current_year)

# ==========================
# 7) Template Conferma ("/confirm")
# ==========================
confirm_template = r'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Documento generato</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      label { display: block; margin-top: 10px; }
      input { font-size: 1em; padding: 5px; width: 100%%; max-width: 300px; }
      input[type="submit"] { margin-top: 20px; font-size: 1.2em; padding: 10px 20px; }
      a { display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Grazie, {{ nome }} {{ cognome }}!</h1>
    <p>Il tuo PDF è stato generato con successo: <strong>{{ pdf_file }}</strong>.</p>
    <hr>
    <h2>Invia il PDF via Email</h2>
    <form action="/send_email" method="post">
        <label for="destinatario">Inserisci l'indirizzo email a cui inviare il PDF:</label>
        <input type="email" id="destinatario" name="destinatario" required>
        <input type="hidden" name="pdf_file" value="{{ pdf_file }}">
        <input type="hidden" name="specialist" value="{{ specialist }}">
        <input type="hidden" name="nome" value="{{ nome }}">
        <input type="hidden" name="cognome" value="{{ cognome }}">
        <input type="submit" value="Invia Email">
    </form>
    <a href="/">Chiudi e torna all'inizio</a>
</body>
</html>
'''

# ==========================
# 8) Rotta /submit: genera PDF senza logo
# ==========================
@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    codice_fiscale = request.form.get('codice_fiscale', '').strip()
    
    birth_day = request.form.get('birth_day', '').strip()
    birth_month = request.form.get('birth_month', '').strip()
    birth_year = request.form.get('birth_year', '').strip()
    data_nascita = f"{birth_day}/{birth_month}/{birth_year}"
    
    specialist = request.form.get('specialist', '1').strip()
    firma_data = request.form.get('signature_data', '')

    # Controllo CF
    if len(codice_fiscale) != 16:
        return f'''
        <h1>Errore</h1>
        <p>Il codice fiscale deve contenere esattamente 16 caratteri.</p>
        <p><a href="/form?specialist={specialist}">Torna al form</a></p>
        '''

    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    specialist_folder = os.path.join(SHARED_FOLDER, folder_name)
    os.makedirs(specialist_folder, exist_ok=True)

    filename_pdf = f"{nome}_{cognome}_{timestamp_str}.pdf"
    pdf_path = os.path.join(specialist_folder, filename_pdf)

    if firma_data.startswith("data:image/png;base64,"):
        firma_img_tag = f'<img src="{firma_data}" alt="Firma" style="width:200px;"/>'
    else:
        firma_img_tag = "<p><em>Nessuna firma</em></p>"

    # Recupera testo informativa (se vuoi mostrarlo nel PDF)
    informativa = privacy_texts.get(specialist, "[Informativa da inserire qui]")

    # Costruisci PDF senza logo e riferimenti aziendali
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Documento - {nome} {cognome}</title>
    </head>
    <body>
        <div style="text-align: justify; line-height:1.6;">
            <h1 style="text-align:center;">Informativa {specialist_names.get(specialist, '')}</h1>
            <p>{informativa}</p>
            <hr>
            <h2>Dati Utente</h2>
            <p>Nome: {nome}</p>
            <p>Cognome: {cognome}</p>
            <p>Codice Fiscale: {codice_fiscale}</p>
            <p>Data di nascita: {data_nascita}</p>
            <p>Data compilazione: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
            <hr>
            <h2>Firma</h2>
            {firma_img_tag}
        </div>
    </body>
    </html>
    """

    pdfkit.from_string(pdf_html, pdf_path, configuration=pdfkit_config)

    return render_template_string(
        confirm_template,
        nome=nome,
        cognome=cognome,
        pdf_file=filename_pdf,
        specialist=specialist
    )

# ==========================
# 9) Rotta /send_email: invia PDF via email
# ==========================
@app.route('/send_email', methods=['POST'])
def send_email():
    destinatario = request.form.get('destinatario', '').strip()
    pdf_file = request.form.get('pdf_file', '').strip()
    specialist = request.form.get('specialist', '1').strip()
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()

    folder_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    pdf_full_path = os.path.join(SHARED_FOLDER, folder_name, pdf_file)

    if not os.path.exists(pdf_full_path):
        return f"<h1>Errore: il file {pdf_full_path} non esiste sul server</h1>"

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = EMAIL_USERNAME
    PASSWORD = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = f"Documento firmato: {nome} {cognome}"

    corpo = f"Ciao,\nin allegato il PDF firmato da {nome} {cognome}.\n\nSaluti."
    msg.attach(MIMEMultipart('alternative'))
    msg.get_payload()[0].set_payload(corpo)

    with open(pdf_full_path, 'rb') as f:
        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(f.read())
    encoders.encode_base64(parte)
    parte.add_header('Content-Disposition', f'attachment; filename=\"{pdf_file}\"')
    msg.attach(parte)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"""
        <h1>Email inviata con successo a {destinatario}!</h1>
        <p><a href="/">Torna all'inizio</a></p>
        """
    except Exception as e:
        return f"<h1>Errore durante l'invio email:</h1><p>{str(e)}</p>"

# ==========================
# 10) Avvio dell'app
# ==========================
if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)
