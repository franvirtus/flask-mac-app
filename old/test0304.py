from flask import Flask, render_template_string, request

app = Flask(__name__)

form_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Firma per Specialisti</title>
</head>
<body>
    <h1>Modulo di Firma</h1>
    <form method="post" action="/submit">
        <label>Nome:</label>
        <input type="text" name="nome"><br><br>
        <label>Firma:</label>
        <input type="text" name="firma"><br><br>
        <input type="submit" value="Invia">
    </form>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(form_template)

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome')
    firma = request.form.get('firma')
    return f"<h1>Grazie {nome}, firma ricevuta: {firma}</h1>"

if __name__ == '__main__':
    app.run(debug=True)
