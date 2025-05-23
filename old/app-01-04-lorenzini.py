from flask import Flask, render_template_string, request, redirect, url_for
import pdfkit
import datetime
import os
import base64

app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe")

@app.route("/privacy_lorenzini")
def privacy_lorenzini():
    privacy_text = """INFORMATIVA AI SENSI DELL'ART. 13 DEL REG. UE 2016/679 <br>
    ... (testo completo dell'informativa) ...<br><br>
    <form action='/form_lorenzini' method='get'>
    <fieldset style='border:none;'>
        <legend><strong>Consensi Finali</strong></legend>
        <label><input type="radio" name="consenso_a" value="Acconsento" required> 1. Acconsento al trattamento dei dati per finalità A)</label><br>
        <label><input type="radio" name="consenso_c" value="Acconsento" required> 2. Acconsento per finalità C)</label><br>
        <label><input type="radio" name="consenso_sanitari" value="Acconsento" required> 3. Acconsento alla comunicazione a familiari/sanitari</label><br>
    </fieldset>
    <button type='submit'>Accetto</button>
    </form>
    """
    return render_template_string(f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset='utf-8'><title>Informativa Lorenzini</title></head>
    <body>
    <h1>Informativa Dott.ssa Lorenzini</h1>
    <div style='line-height:1.6;'>{privacy_text}</div>
    </body>
    </html>
    """)

@app.route("/form_lorenzini")
def form_lorenzini():
    current_year = datetime.datetime.now().year
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Modulo Lorenzini</title>
    <style>
        body { font-family: Arial; padding: 20px; }
        label { display: block; margin-top: 10px; }
        input, select { width: 300px; padding: 5px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>Modulo Lorenzini</h1>
    <form action="/submit_lorenzini" method="post">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>

        <label for="cognome">Cognome:</label>
        <input type="text" id="cognome" name="cognome" required>

        <label for="nato_a">Nato/a a:</label>
        <input type="text" id="nato_a" name="nato_a" required>

        <label for="residente">Residente a:</label>
        <input type="text" id="residente" name="residente" required>

        <label for="via">Via:</label>
        <input type="text" id="via" name="via" required>

        <label for="luogo">Luogo:</label>
        <input type="text" id="luogo" name="luogo" required>

        <input type="submit" value="Genera PDF">
    </form>
</body>
</html>
''')

@app.route("/submit_lorenzini", methods=["POST"])
def submit_lorenzini():
    nome = request.form.get("nome")
    cognome = request.form.get("cognome")
    nato_a = request.form.get("nato_a")
    residente = request.form.get("residente")
    via = request.form.get("via")
    luogo = request.form.get("luogo")

    consenso_a = request.args.get("consenso_a", "Acconsento")
    consenso_c = request.args.get("consenso_c", "Acconsento")
    consenso_sanitari = request.args.get("consenso_sanitari", "Acconsento")

    oggi = datetime.datetime.now().strftime("%d/%m/%Y")
    pdf_html = f'''
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body>
        <h2>Modulo Privacy - Dott.ssa Lorenzini</h2>
        <p>Io sottoscritto/a {nome} {cognome}, nato/a a {nato_a}, residente a {residente}, in via {via},</p>
        <p>{consenso_a} al trattamento dei dati per le finalità di cui al punto 1, lett. A).</p>
        <p>Dichiaro inoltre:</p>
        <ul>
            <li>{consenso_c} per le finalità di cui al punto 2, lett. C)</li>
            <li>{consenso_sanitari} alla comunicazione dei miei dati a familiari e/o sanitari</li>
        </ul>
        <p><strong>Firma</strong></p>
        <p>{luogo}, il {oggi}</p>
    </body>
    </html>
    '''

    filename = f"Modulo_Lorenzini_{nome}_{cognome}.pdf"
    pdf_path = os.path.join("C:/Salvataggio privacy/Dott_Lorenzini", filename)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    pdfkit.from_string(pdf_html, pdf_path, configuration=pdfkit_config)

    return f"<h1>PDF generato con successo!</h1><p>File: {filename}</p><a href='/'>Torna alla Home</a>"

if __name__ == "__main__":
    app.run(debug=True, port=8080)
