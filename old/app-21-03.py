import datetime
import base64

import json
import os

# Costruisci il percorso del file config.json nella stessa cartella di app.py
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)

# Estrai le variabili di configurazione dal file
EMAIL_USERNAME = config_data.get("EMAIL_USERNAME", "default@example.com")
EMAIL_PASSWORD = config_data.get("EMAIL_PASSWORD", "defaultpassword")
SHARED_FOLDER = config_data.get("SHARED_FOLDER", r"C:\Salvataggio privacy")
HOST = config_data.get("HOST", "0.0.0.0")
PORT = config_data.get("PORT", 5000)



from flask import Flask, render_template_string, request
import pdfkit

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Carichiamo il logo in base64
logo_path = "logo.png"
with open(logo_path, "rb") as f:
    image_data = f.read()
encoded_image = base64.b64encode(image_data).decode('utf-8')

app = Flask(__name__)

# Configurazione pdfkit
config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Template della pagina iniziale ("/")
privacy_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>Informativa sulla Privacy - Virtus</title>
    <meta charset="utf-8">
    <style>
      body {
        margin: 0;
        padding: 0;
        font-family: Arial, sans-serif;
      }
      .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
      }
      .logo {
        display: block;
        margin: 0 auto;
        width: 150px;
      }
      h1 {
        text-align: center;
        margin-top: 20px;
      }
      .contact-info {
        text-align: center;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
      }
      .informativa-text {
        text-align: justify;
        line-height: 1.6;
      }
      button {
        display: block;
        margin: 20px auto;
        font-size: 1.2em;
        padding: 10px 20px;
        cursor: pointer;
      }
    </style>
</head>
<body>
  <div class="container">
    <img src="/static/logo.png" alt="Logo" class="logo">
    <h1>Informativa sulla Privacy</h1>
    <div class="contact-info">
      Nutrizione e terapia dello sport<br>
      Via Montello 79 – 25128 Brescia<br>
      Tel. 3518899843<br>
      Email: info@virtusbrixia.com
    </div>
    <div class="informativa-text">
      <p>
        Ai sensi dell’art. 13 del Regolamento UE 679/16, in relazione ai dati personali che La riguardano e che saranno oggetto del trattamento, La informiamo di quanto segue. <br>
 
1. I dati sensibili da Lei forniti verranno trattati secondo i principi di liceità, correttezza, adeguatezza ed in generale nei limiti di quanto previsto dal Regolamento per le finalità di consulenza, anamnesi e redazione di una corretta alimentazione connesse all’assolvimento dell’incarico professionale da Lei conferito; <br>
2. Il trattamento sarà effettuato sia manualmente che avvalendosi di strumenti elettronici; <br>
3. Il conferimento dei dati è obbligatorio per potere assolvere all’incarico conferito per le finalità di cui al punto 1 e l'eventuale rifiuto a fornire tali dati comporta l’impossibilità di dare esecuzione al contratto e quindi l’impossibilità di fornirLe la prestazione sanitaria richiesta e la relativa assistenza. <br>
4. I dati in nessun caso saranno oggetto di diffusione e saranno comunicati esclusivamente a soggetti autorizzati ed al professionista esterno che, in qualità di responsabile del trattamento, cura la contabilità dello Studio. In quest’ultimo caso i dati comunicati saranno quelli strettamente necessari per assolvere agli obblighi contabili e fiscali; <br>
5. Le fatture relative alle prestazioni sanitarie rese, verranno inviate al Sistema Tessera Sanitaria per la predisposizione del Suo Modello 730 precompilato. Qualora volesse opporsi a tale invio, potrà comunicarlo oralmente al Titolare stesso, il quale provvederà ad annotare l’opposizione sulla Sua fattura; <br>
6. Il titolare del trattamento è il Dott. Gaetano Messineo con sede legale in Via Montello, 79 Brescia BS e studio in Via Corfù, 71 -25124 Brescia; <br>
7. In ogni momento potrà esercitare i Suoi diritti nei confronti del titolare del trattamento, quali il diritto di accesso ai dati personali e la rettifica o la cancellazione degli stessi o la limitazione del trattamento che La riguardano o il diritto di opporsi al loro trattamento, oltre al diritto alla portabilità dei dati; ed in generale tutti i diritti previsti dal Regolamento. <br>
8. Al fine di tutelare i diritti di cui al punto precedente, potrà proporre reclamo all’Autorità Garante per la Protezione dei dati personali; <br>
9. Il Suoi dati verranno conservati per il tempo necessario per il raggiungimento delle finalità di cui al punto 1 ed in ogni caso, per assolvere agli obblighi imposti dalle normative sanitarie; <br>
10.Il consenso prestato con la sottoscrizione del presente modulo è in ogni momento revocabile. L’esercizio del diritto di revoca non pregiudica le prestazioni già rese. <br>


      </p>
    </div>
    <button onclick="window.location.href='/form'">Accetto</button>
  </div>
</body>
</html>
'''

# Template del form ("/form")
form_template = '''
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
      h1 {
        margin-bottom: 20px;
      }
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
      input {
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
        <input
            type="text"
            id="codice_fiscale"
            name="codice_fiscale"
            required
            pattern="^[A-Za-z0-9]{16}$"
            title="Inserisci 16 caratteri alfanumerici"
        >

        <label for="data_nascita">Data di nascita:</label>
        <input type="date" id="data_nascita" name="data_nascita" required>

        <input type="submit" value="Invia">
    </form>
</body>
</html>
'''

# Template di conferma ("/confirm")
confirm_template = '''
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
        <input type="hidden" name="nome" value="{{ nome }}">
        <input type="hidden" name="cognome" value="{{ cognome }}">

        <input type="submit" value="Invia Email">
    </form>

    <a href="/">Chiudi e torna all'inizio</a>
</body>
</html>
'''

@app.route('/')
def privacy():
    return render_template_string(privacy_template)

@app.route('/form')
def show_form():
    return render_template_string(form_template)

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    codice_fiscale = request.form.get('codice_fiscale', '').strip()
    data_nascita = request.form.get('data_nascita', '').strip()

    # Controllo CF
    if len(codice_fiscale) != 16:
        return '''
        <h1>Errore</h1>
        <p>Il codice fiscale deve contenere esattamente 16 caratteri.</p>
        <p><a href="/form">Torna al form</a></p>
        '''

    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Documento - {nome} {cognome}</title>
    </head>
    <body>
        <!-- Logo centrato -->
        <img src="data:image/png;base64,{encoded_image}" 
             alt="Logo" 
             style="width:150px; display:block; margin:0 auto;" />

        <!-- Contatti -->
        <div style="text-align:center; margin-top: 10px;">
          Nutrizione e terapia dello sport<br>
          Via Montello 79 – 25128 Brescia<br>
          Tel. 3518899843<br>
          Email: info@virtusbrixia.com
        </div>

        <div style="text-align: justify; line-height:1.6;">
            <h1 style="text-align:center;">Informativa sulla Privacy</h1>
            <p>
               Ai sensi dell’art. 13 del Regolamento UE 679/16, in relazione ai dati personali che La riguardano e che saranno oggetto del trattamento, La informiamo di quanto segue. <br>
 
1. I dati sensibili da Lei forniti verranno trattati secondo i principi di liceità, correttezza, adeguatezza ed in generale nei limiti di quanto previsto dal Regolamento per le finalità di consulenza, anamnesi e redazione di una corretta alimentazione connesse all’assolvimento dell’incarico professionale da Lei conferito; <br>
2. Il trattamento sarà effettuato sia manualmente che avvalendosi di strumenti elettronici; <br>
3. Il conferimento dei dati è obbligatorio per potere assolvere all’incarico conferito per le finalità di cui al punto 1 e l'eventuale rifiuto a fornire tali dati comporta l’impossibilità di dare esecuzione al contratto e quindi l’impossibilità di fornirLe la prestazione sanitaria richiesta e la relativa assistenza. <br>
4. I dati in nessun caso saranno oggetto di diffusione e saranno comunicati esclusivamente a soggetti autorizzati ed al professionista esterno che, in qualità di responsabile del trattamento, cura la contabilità dello Studio. In quest’ultimo caso i dati comunicati saranno quelli strettamente necessari per assolvere agli obblighi contabili e fiscali; <br>
5. Le fatture relative alle prestazioni sanitarie rese, verranno inviate al Sistema Tessera Sanitaria per la predisposizione del Suo Modello 730 precompilato. Qualora volesse opporsi a tale invio, potrà comunicarlo oralmente al Titolare stesso, il quale provvederà ad annotare l’opposizione sulla Sua fattura; <br>
6. Il titolare del trattamento è il Dott. Gaetano Messineo con sede legale in Via Montello, 79 Brescia BS e studio in Via Corfù, 71 -25124 Brescia; <br>
7. In ogni momento potrà esercitare i Suoi diritti nei confronti del titolare del trattamento, quali il diritto di accesso ai dati personali e la rettifica o la cancellazione degli stessi o la limitazione del trattamento che La riguardano o il diritto di opporsi al loro trattamento, oltre al diritto alla portabilità dei dati; ed in generale tutti i diritti previsti dal Regolamento. <br>
8. Al fine di tutelare i diritti di cui al punto precedente, potrà proporre reclamo all’Autorità Garante per la Protezione dei dati personali; <br>
9. Il Suoi dati verranno conservati per il tempo necessario per il raggiungimento delle finalità di cui al punto 1 ed in ogni caso, per assolvere agli obblighi imposti dalle normative sanitarie; <br>
10.Il consenso prestato con la sottoscrizione del presente modulo è in ogni momento revocabile. L’esercizio del diritto di revoca non pregiudica le prestazioni già rese. <br>
            </p>
            <hr>
            <h2>Dati Utente</h2>
            <p>Nome: {nome}</p>
            <p>Cognome: {cognome}</p>
            <p>Codice Fiscale: {codice_fiscale}</p>
            <p>Data di nascita: {data_nascita}</p>
            <p>Data compilazione: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </div>
    </body>
    </html>
    """

    shared_folder = SHARED_FOLDER
    filename_pdf = f"{nome}_{cognome}_{timestamp_str}.pdf"
    pdf_path = os.path.join(shared_folder, filename_pdf)

    pdfkit.from_string(pdf_html, pdf_path, configuration=config)

    return render_template_string(
        confirm_template,
        nome=nome,
        cognome=cognome,
        pdf_file=filename_pdf
    )

@app.route('/send_email', methods=['POST'])
def send_email():
    destinatario = request.form.get('destinatario', '').strip()
    pdf_file = request.form.get('pdf_file', '').strip()
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()

    if not os.path.exists(pdf_file):
        return f"<h1>Errore: il file {pdf_file} non esiste sul server</h1>"

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = "senseiblogger@gmail.com"
    PASSWORD = "midw hacd gnec rzbq"

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = f"Documento firmato: {nome} {cognome}"

    corpo = f"Ciao,\nin allegato il PDF firmato da {nome} {cognome}.\n\nSaluti."
    msg.attach(MIMEBase('text', 'plain', _charset='utf-8'))
    msg.get_payload()[-1].set_payload(corpo)

    with open(pdf_file, 'rb') as f:
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

if __name__ == '__main__':
    app.run(debug=True,  host=HOST, port=PORT)
