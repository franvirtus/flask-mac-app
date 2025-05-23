
from flask import Flask, render_template_string, request
import datetime

app = Flask(__name__)

# Dati specialisti e informative
specialist_names = {
    "1": "Dott. Messineo",
    "2": "Dott.ssa Lorenzini",
    "3": "Dott.ssa Scattolini",
    "4": "Dott. Neri"
}

privacy_texts = {
    "1": "Informativa per Dott. Messineo...",
    "2": "Informativa per Dott.ssa Lorenzini...",
    "3": "Informativa per Dott.ssa Scattolini...",
    "4": "Informativa per Dott. Neri..."
}

form_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Firme e Informative</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 20px; }
        h1 { text-align: center; }

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
</html>"""


@app.route('/form', methods=['GET', 'POST'])
def mostra_form():
    specialist = request.args.get("specialist", "1")
    specialist_name = specialist_names.get(specialist, "Specialista Sconosciuto")
    privacy_text = privacy_texts.get(specialist, "[Informativa mancante]")

    if request.method == "POST":
        consenso = request.form.get("consenso", "Non indicato")
        firma_gen = request.form.get("signature_data_generale", "")
        firma_sca = request.form.get("signature_data_scattolini", "")
        return f"<h1>Grazie!</h1><p>Consenso: {consenso}</p><p>Firma Generale ricevuta: {bool(firma_gen)}</p><p>Firma Scattolini ricevuta: {bool(firma_sca)}</p>"

    return render_template_string(
        form_template,
        specialist_name=specialist_name,
        privacy_text=privacy_text
    )

if __name__ == '__main__':
    app.run(debug=True)
