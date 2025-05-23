from flask import Flask, render_template_string

app = Flask(__name__)

home_template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Seleziona lo Specialista</title>
  <style>
    body {
      text-align: center;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 20px;
    }
    h1 {
      margin-bottom: 20px;
    }
    button {
      margin: 10px;
      padding: 10px 20px;
      font-size: 1.2em;
      cursor: pointer;
    }
    img {
      display: block;
      margin: 0 auto 20px auto;
      width: 150px;
    }
  </style>
</head>
<body>
  <img src="/static/logo.png" alt="Logo">
  <div class="contact-info">
    <p><strong>Nutrizione e terapia dello sport<br>
    Via Montello 79 – 25128 Brescia<br>
    Tel. 3518899843<br>
    Email: info@virtusbrixia.com</strong></p>
  </div>
  <h1>Seleziona lo Specialista</h1>
  <button onclick="window.location.href='/privacy_messineo'">Dott. Messineo</button>
  <button onclick="window.location.href='/privacy_lorenzini'">Dott.ssa Lorenzini</button>
  <button onclick="window.location.href='/privacy_scattolini'">Dott.ssa Scattolini</button>
  <button onclick="window.location.href='/privacy_serioli'">Dott.ssa Serioli</button>
</body>
</html>
'''

@app.route('/')
def homepage():
    return render_template_string(home_template)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
