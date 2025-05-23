import json
import os
from flask import Flask, render_template_string

# Carichiamo specialists.json
with open("specialists.json", "r", encoding="utf-8") as f:
    specialists_data = json.load(f)

app = Flask(__name__)

home_template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Specialisti</title>
</head>
<body>
  <h1>Specialisti</h1>
  {{ specialists_buttons }}
</body>
</html>
'''

@app.route('/')
def home():
    specialists_buttons = ""
    for key, info in specialists_data.items():
        # info dovrebbe essere { "nome": "Dott_Rossi", "modulo": "modulo_dottRossi.html" }
        # Quindi info["nome"] = "Dott_Rossi"
        name = info["nome"]
        specialists_buttons += f'<button>{name}</button><br>'
    final_html = home_template.replace("{{ specialists_buttons }}", specialists_buttons)
    return final_html

if __name__ == '__main__':
    app.run(debug=True)
