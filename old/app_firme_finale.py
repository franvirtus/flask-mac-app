
from flask import Flask, render_template_string, request
import datetime
import os
import pdfkit

app = Flask(__name__)

SAVE_FOLDER = "pdf_firmati"
os.makedirs(SAVE_FOLDER, exist_ok=True)

pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Firme Multiple</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { text-align: center; }
        .canvas-wrapper { display: flex; justify-content: space-around; margin-top: 20px; }
        .canvas-container {
            position: relative;
            display: inline-block;
            border: 1px solid #000;
            width: 380px;
            height: 150px;
        }
        canvas { width: 100%; height: 100%; }
        .clear-btn {
            position: absolute;
            top: 0; right: 0;
            color: red; font-size: 20px;
            background: transparent; border: none;
            cursor: pointer; z-index: 10;
        }
    </style>
</head>
<body>
    <h1>Firma per Specialisti</h1>
    <form method="post">
        <div class="canvas-wrapper">
            <div>
                <label for="signature-pad-generale">Firma Generale:</label><br>
                <div class="canvas-container">
                    <canvas id="signature-pad-generale"></canvas>
                    <button type="button" class="clear-btn" onclick="clearSignature('generale')">X</button>
                </div>
                <input type="hidden" name="signature_data_generale" id="signature_data_generale">
            </div>
            <div>
                <label for="signature-pad-scattolini">Firma Scattolini:</label><br>
                <div class="canvas-container">
                    <canvas id="signature-pad-scattolini"></canvas>
                    <button type="button" class="clear-btn" onclick="clearSignature('scattolini')">X</button>
                </div>
                <input type="hidden" name="signature_data_scattolini" id="signature_data_scattolini">
            </div>
        </div>
        <br><br>
        <div style="text-align: center;">
            <input type="submit" value="Invia">
        </div>
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
def index():
    if request.method == "POST":
        sig1 = request.form.get("signature_data_generale", "")
        sig2 = request.form.get("signature_data_scattolini", "")

        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SAVE_FOLDER, f"firme_{now}.pdf")

        firma1 = f'<img src="{sig1}" width="300"/>' if sig1.startswith("data:image") else "Nessuna firma generale"
        firma2 = f'<img src="{sig2}" width="300"/>' if sig2.startswith("data:image") else "Nessuna firma Scattolini"

        html_pdf = f"""
        <html><body style='font-family:Arial;'>
        <h1>Firme acquisite</h1>
        <h2>Firma Generale</h2>{firma1}<br><br>
        <h2>Firma Scattolini</h2>{firma2}<br><br>
        <p>Data: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
        </body></html>
        """

        pdfkit.from_string(html_pdf, filename, configuration=pdfkit_config)

        return f"<h1>PDF salvato come {filename}</h1><p><a href='/'>Torna indietro</a></p>"

    return render_template_string(html_template)

if __name__ == "__main__":
    app.run(debug=True)
