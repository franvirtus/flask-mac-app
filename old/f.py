import pdfkit
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    # 1. Recupera i dati dal form (inclusa la firma in Base64)
    nome = request.form.get('name')
    firma_data = request.form.get('signature_data')  # stringa data:image/png;base64,...
    # 2. Prepara un HTML che includa la firma
    html_content = f"""
    <html>
      <head><meta charset="UTF-8"></head>
      <body>
        <p><strong>Nome:</strong> {nome}</p>
        <p><strong>Firma:</strong></p>
        <img src="{firma_data}" alt="Firma" style="width:200px; height:auto;">
      </body>
    </html>"""
    # 3. Configura pdfkit (specifica il percorso di wkhtmltopdf su Windows, se necessario)
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    # 4. Genera il PDF dal contenuto HTML
    pdfkit.from_string(html_content, "modulo_firmato.pdf", configuration=config)
    # 5. Restituisce il PDF generato (come file da scaricare, in questo esempio)
    return send_file("modulo_firmato.pdf", as_attachment=True)
