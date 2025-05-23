
from flask import Flask, render_template_string, request
import datetime
import pdfkit
import os

app = Flask(__name__)

# Configura wkhtmltopdf se serve (per evitare errori su Windows, imposta il percorso corretto)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

form_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Firme e Informative</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { text-align: center; }

        form {
            max-width: 1000px;
            margin: auto;
        }

        label {
            font-weight: bold;
            display: block;
            margin-top: 10px;
        }

        input[type="text"] {
            width: 100%;
            padding: 6px;
            margin-bottom: 10px;
        }

        .canvas-wrapper {
            display: flex;
            justify-content: space-around;
            margin-top: 20px;
        }

        .canvas-container {
            position: relative;
            display: inline-block;
            border: 1px solid #000;
            width: 380px;
            height: 150px;
        }

        canvas {
            width: 100%;
            height: 100%;
        }

        .clear-btn {
            position: absolute;
            top: 0;
            right: 0;
            color: red;
            font-size: 20px;
            background: transparent;
            border: none;
            cursor: pointer;
            z-index: 10;
        }

        .submit {
            display: block;
            margin: 30px auto;
            padding: 10px 30px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <h1>Firma per Specialisti</h1>
    <form method="POST">
        <label>Nome:</label>
        <input type="text" name="nome" required>

        <label>Cognome:</label>
        <input type="text" name="cognome" required>

        <label>Codice Fiscale:</label>
        <input type="text" name="codice_fiscale" required>

        <label>Luogo di nascita:</label>
        <input type="text" name="luogo_nascita" required>

        <label>Data di nascita (gg/mm/aaaa):</label>
        <input type="text" name="data_nascita" required>

        <label>Indirizzo di residenza:</label>
        <input type="text" name="indirizzo" required>

        <div class="canvas-wrapper">
            <div>
                <label>Firma Generale:</label>
                <div class="canvas-container">
                    <canvas id="signature-pad-generale"></canvas>
                    <button type="button" class="clear-btn" onclick="clearSignature('generale')">X</button>
                </div>
                <input type="hidden" name="signature_data_generale" id="signature_data_generale">
            </div>

            <div>
                <label>Firma Scattolini:</label>
                <div class="canvas-container">
                    <canvas id="signature-pad-scattolini"></canvas>
                    <button type="button" class="clear-btn" onclick="clearSignature('scattolini')">X</button>
                </div>
                <input type="hidden" name="signature_data_scattolini" id="signature_data_scattolini">
            </div>
        </div>

        <input type="submit" value="Invia" class="submit">
    </form>

    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
    <script>
        const padGenerale = new SignaturePad(document.getElementById("signature-pad-generale"));
        const padScattolini = new SignaturePad(document.getElementById("signature-pad-scattolini"));

        function clearSignature(tipo) {
            if (tipo === 'generale') padGenerale.clear();
            else if (tipo === 'scattolini') padScattolini.clear();
        }

        document.querySelector("form").addEventListener("submit", function (e) {
            if (!padGenerale.isEmpty()) {
                document.getElementById("signature_data_generale").value = padGenerale.toDataURL();
            }
            if (!padScattolini.isEmpty()) {
                document.getElementById("signature_data_scattolini").value = padScattolini.toDataURL();
            }
        });
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def form():
    if request.method == "POST":
        nome = request.form["nome"]
        cognome = request.form["cognome"]
        codice_fiscale = request.form["codice_fiscale"]
        luogo_nascita = request.form["luogo_nascita"]
        data_nascita = request.form["data_nascita"]
        indirizzo = request.form["indirizzo"]
        firma_generale = request.form["signature_data_generale"]
        firma_scattolini = request.form["signature_data_scattolini"]

        html_pdf = f"""
        <html>
        <body style='font-family: Arial;'>
            <h2>Dati Anagrafici</h2>
            <p><strong>Nome:</strong> {nome}</p>
            <p><strong>Cognome:</strong> {cognome}</p>
            <p><strong>Codice Fiscale:</strong> {codice_fiscale}</p>
            <p><strong>Luogo di Nascita:</strong> {luogo_nascita}</p>
            <p><strong>Data di Nascita:</strong> {data_nascita}</p>
            <p><strong>Indirizzo:</strong> {indirizzo}</p>
            <hr>
            <h3>Firma Generale</h3>
            <img src="{firma_generale}" style="width:300px;">
            <h3>Firma Scattolini</h3>
            <img src="{firma_scattolini}" style="width:300px;">
            <p><em>Data generazione: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}</em></p>
        </body>
        </html>
        """

        output_path = os.path.join(os.getcwd(), f"{nome}_{cognome}_modulo.pdf")
        pdfkit.from_string(html_pdf, output_path, configuration=pdfkit_config)

        return f"<h1>PDF generato correttamente!</h1><p>File salvato in: {output_path}</p><p><a href='/'>Torna indietro</a></p>"

    return render_template_string(form_template)

if __name__ == "__main__":
    app.run(debug=True)
