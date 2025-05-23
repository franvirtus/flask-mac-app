
from flask import Flask, render_template_string, request
app = Flask(__name__)

@app.route("/")
def index():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Firma Test</title>
        <style>
            .canvas-container {
                position: relative;
                display: inline-block;
                border: 1px solid #000;
                width: 300px;
                height: 100px;
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
        </style>
    </head>
    <body>
        <h1>Firma per Specialisti</h1>

        <form method="POST" action="/submit">
            <label>Firma Generale:</label>
            <div class="canvas-container">
                <canvas id="signature-pad-generale" width="300" height="100"></canvas>
                <button type="button" class="clear-btn" onclick="clearSignature('generale')">X</button>
            </div>
            <input type="hidden" name="signature_data_generale" id="signature_data_generale">

            <label>Firma Scattolini:</label>
            <div class="canvas-container">
                <canvas id="signature-pad-scattolini" width="300" height="100"></canvas>
                <button type="button" class="clear-btn" onclick="clearSignature('scattolini')">X</button>
            </div>
            <input type="hidden" name="signature_data_scattolini" id="signature_data_scattolini">

            <input type="submit" value="Invia">
        </form>

        <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
        <script>
            const padGenerale = new SignaturePad(document.getElementById("signature-pad-generale"));
            const padScattolini = new SignaturePad(document.getElementById("signature-pad-scattolini"));

            function clearSignature(tipo) {
                if (tipo === "generale") {
                    padGenerale.clear();
                } else if (tipo === "scattolini") {
                    padScattolini.clear();
                }
            }

            document.querySelector("form").addEventListener("submit", function(e) {
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
    """)

@app.route("/submit", methods=["POST"])
def submit():
    data1 = request.form.get("signature_data_generale", "")
    data2 = request.form.get("signature_data_scattolini", "")
    return f"<h1>Ricevuto!</h1><p>Generale: {bool(data1)}</p><p>Scattolini: {bool(data2)}</p>"

if __name__ == "__main__":
    app.run(debug=True)
