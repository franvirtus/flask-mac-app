from flask import Flask, render_template_string, request
import datetime

app = Flask(__name__)

@app.route('/privacy_messineo', methods=['GET', 'POST'])
def privacy_messineo():
    if request.method == 'POST':
        nome = request.form.get("nome", "")
        cognome = request.form.get("cognome", "")
        consenso = request.form.get("consenso", "")
        data = request.form.get("data", datetime.datetime.now().strftime('%d/%m/%Y'))
        return f"<h1>Grazie {nome} {cognome}, consenso: {consenso}, data: {data}</h1>"

    today = datetime.datetime.now().strftime('%Y-%m-%d')
    template = '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Informativa - Dott. Messineo</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; line-height: 1.6; }
            label, input[type="text"], input[type="date"] {
                display: block;
                margin-bottom: 10px;
                width: 100%;
                max-width: 400px;
            }
        </style>
    </head>
    <body>
        <h1>Informativa - Dott. Messineo</h1>
        <p>[TESTO INFORMATIVA MESSINEO QUI]</p>

        <form method="post">
            <label>Nome:</label>
            <input type="text" name="nome" required>

            <label>Cognome:</label>
            <input type="text" name="cognome" required>

            <label>Consenso:</label>
            <label><input type="radio" name="consenso" value="Acconsento" required> Acconsento</label>
            <label><input type="radio" name="consenso" value="Non acconsento"> Non acconsento</label>

            <label>Data:</label>
            <input type="date" name="data" value="{{ today }}">

            <button type="submit">Invia</button>
        </form>
    </body>
    </html>
    '''
    return render_template_string(template, today=today)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
