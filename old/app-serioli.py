from flask import Flask, request, render_template_string
import pdfkit
import os
import datetime

app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
SHARED_FOLDER = r"C:\Salvataggio privacy"

@app.route('/privacy/4')
def serioli_form():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    return render_template_string(template_serioli, today=today)

@app.route('/submit_serioli', methods=['POST'])
def submit_serioli():
    nome = request.form.get("nome", "").strip()
    cognome = request.form.get("cognome", "").strip()
    consenso1 = request.form.get("consenso1", "")
    consenso2 = request.form.get("consenso2", "")
    consenso3 = request.form.get("consenso3", "")
    data = request.form.get("data", "")
    firma_data = request.form.get("signature_data", "")

    if not firma_data.startswith("data:image"):
        return "<h1>Errore: Firma mancante o non valida</h1>"

    firma_html = f'<img src="{firma_data}" alt="Firma" style="width:200px;" />'

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"serioli_{nome}_{cognome}_{timestamp}.pdf"
    folder_path = os.path.join(SHARED_FOLDER, "Dott.ssa Serioli")
    os.makedirs(folder_path, exist_ok=True)
    pdf_path = os.path.join(folder_path, filename)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"><title>Consenso</title></head>
    <body style="font-family:Arial; font-size:14px;">
    <h2>Consensi</h2>
    <p>Io sottoscritto/a <strong>{nome} {cognome}</strong>, vista l’informativa sul trattamento dei dati personali, sopra riportata:</p>
    
    <ul>
      <li><strong>Consenso 1:</strong> {consenso1}</li>
      <li><strong>Consenso 2:</strong> {consenso2}</li>
      <li><strong>Consenso 3:</strong> {consenso3}</li>
    </ul>

    <p><strong>Data:</strong> {data}</p>
    <p><strong>Firma:</strong><br>{firma_html}</p>
    </body>
    </html>
    """

    pdfkit.from_string(html, pdf_path, configuration=pdfkit_config)

    return f"<h1>PDF generato con successo!</h1><p>File: {filename}</p><p><a href='/'>Torna alla Home</a></p>"

template_serioli = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Consenso Dott.ssa Serioli</title>
  <style>
    body { font-family: Georgia, serif; padding: 30px; line-height: 1.6; }
    label { display: block; margin: 10px 0; }
    input[type=text], input[type=date] {
        width: 300px;
        padding: 5px;
        font-size: 1em;
    }
    .canvas-container {
        border: 1px solid #000; width: 500px; height: 150px; position: relative;
    }
    canvas { width: 100%; height: 100%; }
    .clear-btn {
        position: absolute; top: 5px; right: 10px;
        color: red; font-weight: bold; background: none; border: none; font-size: 18px; cursor: pointer;
    }
  </style>
</head>
<body>
  <h2>Consensi</h2>
  <form method="post" action="/submit_serioli">
    <label>Nome:<br><input type="text" name="nome" required></label>
    <label>Cognome:<br><input type="text" name="cognome" required></label>

    <label>Data:<br><input type="date" name="data" value="{{ today }}"></label>

    <label><input type="radio" name="consenso1" value="Acconsento" required> Acconsento</label>
    <label><input type="radio" name="consenso1" value="Non acconsento" required> Non acconsento</label>

    <label><input type="radio" name="consenso2" value="Acconsento" required> Acconsento</label>
    <label><input type="radio" name="consenso2" value="Non acconsento" required> Non acconsento</label>

    <label><input type="radio" name="consenso3" value="Autorizzo" required> Autorizzo</label>
    <label><input type="radio" name="consenso3" value="Non autorizzo" required> Non autorizzo</label>

    <h3>Firma (usa il dito o il mouse)</h3>
    <div class="canvas-container">
      <canvas id="signature-pad"></canvas>
      <button type="button" class="clear-btn" onclick="clearSignature()">X</button>
    </div>
    <input type="hidden" name="signature_data" id="signature_data">

    <br><input type="submit" value="Genera PDF">
  </form>

  <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
  <script>
    const canvas = document.getElementById('signature-pad');
    const pad = new SignaturePad(canvas);

    function clearSignature() {
      pad.clear();
    }

    document.querySelector('form').addEventListener('submit', function(e) {
      if (!pad.isEmpty()) {
        document.getElementById('signature_data').value = pad.toDataURL();
      } else {
        alert("Per favore, firma prima di inviare.");
        e.preventDefault();
      }
    });
  </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5005)
