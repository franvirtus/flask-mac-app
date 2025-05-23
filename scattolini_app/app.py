
from flask import Flask, render_template_string, request
import os
import datetime
import base64
import pdfkit

SAVE_FOLDER = r"C:\ScattoliniPrivacyPDF"
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

app = Flask(__name__)

form_html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Modulo Privacy - Scattolini</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        label { display: block; margin-top: 10px; }
        input, select { width: 100%%; padding: 5px; margin-top: 5px; }
        .canvas-container { border: 1px solid #000; width: 400px; height: 150px; position: relative; }
        canvas { width: 100%%; height: 100%%; }
        .clear-btn { position: absolute; top: 5px; right: 5px; background: red; color: white; border: none; padding: 5px; cursor: pointer; }
        .submit-btn { margin-top: 20px; font-size: 16px; }
    </style>
</head>
<body>
    <h1>Modulo Privacy - Dott.ssa Scattolini</h1>
    <form method="post" action="/submit" onsubmit="prepareSignature()">
        <label>Nome:</label>
        <input type="text" name="nome" required>
        <label>Cognome:</label>
        <input type="text" name="cognome" required>
        <label>Data di nascita:</label>
        <input type="date" name="data_nascita" required>
        <label>Luogo di nascita:</label>
        <input type="text" name="luogo_nascita" required>
        <label>Indirizzo di residenza:</label>
        <input type="text" name="indirizzo" required>
        <label>Codice Fiscale:</label>
        <input type="text" name="cf" required pattern="^[A-Za-z0-9]{16}$">

        <label>Acconsento al trattamento dei miei dati personali:</label>
        <label><input type="radio" name="consenso" value="Acconsento" required> Acconsento</label>
        <label><input type="radio" name="consenso" value="Non Acconsento" required> Non Acconsento</label>

        <label>Autorizzo la comunicazione a:</label>
        <input type="text" name="comunicazione_a" placeholder="Es: Medico, famigliare, ecc.">

        <h3>Firma grafica</h3>
        <div class="canvas-container">
            <canvas id="signature-pad"></canvas>
            <button type="button" class="clear-btn" onclick="clearPad()">X</button>
        </div>
        <input type="hidden" name="firma_base64" id="firma_base64">

        <h3>Consenso verbale (se impossibilitato a firmare)</h3>
        <label>Data:</label>
        <input type="date" name="data_verbale">
        <label>Firma operatore:</label>
        <input type="text" name="firma_verbale">

        <button type="submit" class="submit-btn">Genera PDF</button>
    </form>

    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
    <script>
        const canvas = document.getElementById("signature-pad");
        const signaturePad = new SignaturePad(canvas);

        function clearPad() {
            signaturePad.clear();
        }

        function prepareSignature() {
            if (!signaturePad.isEmpty()) {
                document.getElementById("firma_base64").value = signaturePad.toDataURL();
            }
        }
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(form_html)

@app.route('/submit', methods=['POST'])
def submit():
    os.makedirs(SAVE_FOLDER, exist_ok=True)

    nome = request.form['nome']
    cognome = request.form['cognome']
    data_nascita = request.form['data_nascita']
    luogo_nascita = request.form['luogo_nascita']
    indirizzo = request.form['indirizzo']
    cf = request.form['cf']
    consenso = request.form['consenso']
    comunicazione_a = request.form['comunicazione_a']
    firma_base64 = request.form['firma_base64']
    data_verbale = request.form['data_verbale']
    firma_verbale = request.form['firma_verbale']

    data_creazione = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{cognome}_{nome}_{timestamp}.pdf"
    filepath = os.path.join(SAVE_FOLDER, filename)

    firma_html = f'<img src="{firma_base64}" width="300"/>' if firma_base64 else "<p><i>Firma non acquisita</i></p>"
    verbale_html = ""
    if data_verbale and firma_verbale:
        verbale_html = f"<p><strong>Consenso verbale il {data_verbale}, firmato da:</strong> {firma_verbale}</p>"

    html = f'''
    <html>
    <head><meta charset="utf-8"><title>Modulo PDF</title></head>
    <body style="font-family: Arial; font-size: 14px;">
        <h2 style="text-align:center;">Informativa Privacy - Dott.ssa Linda Scattolini</h2>
        <p><strong>Nome:</strong> {nome} {cognome}</p>
        <p><strong>Data di nascita:</strong> {data_nascita} a {luogo_nascita}</p>
        <p><strong>Indirizzo:</strong> {indirizzo}</p>
        <p><strong>Codice Fiscale:</strong> {cf}</p>
        <p><strong>Consenso:</strong> {consenso}</p>
        <p><strong>Comunicazione a:</strong> {comunicazione_a}</p>
        <p><strong>Data:</strong> {data_creazione}</p>
        <h3>Firma</h3>
        {firma_html}
        {verbale_html}
    </body>
    </html>
    '''

    pdfkit.from_string(html, filepath, configuration=pdfkit_config)
    return f"<h1>PDF generato con successo!</h1><p>Salvato in: {filepath}</p>"

if __name__ == '__main__':
    app.run(debug=True, port=8080)
