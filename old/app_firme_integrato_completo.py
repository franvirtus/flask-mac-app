
from flask import Flask, render_template_string, request

app = Flask(__name__)

form_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Firma per Specialisti</title>
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
    <form method="post" action="/submit">
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

@app.route('/')
def home():
    return render_template_string(form_template)

@app.route('/submit', methods=['POST'])
def submit():
    firma_generale = request.form.get('signature_data_generale', '')
    firma_scattolini = request.form.get('signature_data_scattolini', '')

    result_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Risultato</title></head>
    <body>
        <h2>Firma Generale:</h2>
        {'<img src="' + firma_generale + '" width="300"/>' if firma_generale else '<p>Nessuna firma</p>'}
        <h2>Firma Scattolini:</h2>
        {'<img src="' + firma_scattolini + '" width="300"/>' if firma_scattolini else '<p>Nessuna firma</p>'}
        <br><br><a href="/">Torna indietro</a>
    </body>
    </html>
    """
    return result_html

if __name__ == '__main__':
    app.run(debug=True)
