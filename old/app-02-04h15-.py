import datetime
import base64
import os

from flask import Flask, render_template_string, request
import pdfkit
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# ==========================
# 1) Parametri interni (senza config.json)
# ==========================
EMAIL_USERNAME = "privacyvirtusgroup@gmail.com"
EMAIL_PASSWORD = "smem zaak ubkm yvlc"
SHARED_FOLDER = r"C:\Salvataggio privacy"
HOST = "0.0.0.0"
PORT = 5000

# ==========================
# 2) Dizionari
# ==========================
specialist_names = {
    "1": "Dott. Messineo",
    "2": "Dott.ssa Lorenzini",
    "3": "Dott_Verdi",
    "4": "Dott_Neri"
}

privacy_texts = {
    "1": """1.	I dati sensibili da Lei forniti verranno trattati secondo i principi di liceità, correttezza, adeguatezza ed in generale nei limiti di quanto previsto dal Regolamento per le finalità di consulenza, anamnesi e redazione di una corretta alimentazione connesse all’assolvimento dell’incarico professionale da Lei conferito;<br>
2. Il trattamento sarà effettuato sia manualmente che avvalendosi di strumenti elettronici;<br>
3. Il conferimento dei dati è obbligatorio per potere assolvere all’incarico conferito per le finalità di cui al punto 1 e l'eventuale rifiuto a fornire tali dati comporta l’impossibilità di dare esecuzione al contratto e quindi l’impossibilità di fornirLe la prestazione sanitaria richiesta e la relativa assistenza.<br>
4. I dati in nessun caso saranno oggetto di diffusione e saranno comunicati esclusivamente a soggetti autorizzati ed al professionista esterno che, in qualità di responsabile del trattamento, cura la contabilità dello Studio. In quest’ultimo caso i dati comunicati saranno quelli strettamente necessari per assolvere agli obblighi contabili e fiscali;<br>
5. Le fatture relative alle prestazioni sanitarie rese, verranno inviate al Sistema Tessera Sanitaria per la predisposizione del Suo Modello 730 precompilato. Qualora volesse opporsi a tale invio, potrà comunicarlo oralmente al Titolare stesso, il quale provvederà ad annotare l’opposizione sulla Sua fattura.<br>
6. Il titolare del trattamento è il Dott. Gaetano Messineo con sede legale in Via Montello, 79 Brescia BS e studio in Via Corfù, 71 -25124 Brescia<br>
7. In ogni momento potrà esercitare i Suoi diritti nei confronti del titolare del trattamento, quali il diritto di accesso ai dati personali e la rettifica o la cancellazione degli stessi o la limitazione del trattamento che La riguardano o il diritto di opporsi al loro trattamento, oltre al diritto alla portabilità dei dati; ed in generale tutti i diritti previsti dal Regolamento.<br>
8. Al fine di tutelare i diritti di cui al punto precedente, potrà proporre reclamo all’Autorità Garante per la Protezione dei dati personali;<br>
9. Il Suoi dati verranno conservati per il tempo necessario per il raggiungimento delle finalità di cui al punto 1 ed in ogni caso, per assolvere agli obblighi imposti dalle normative sanitarie;<br>
10.Il consenso prestato con la sottoscrizione del presente modulo è in ogni momento revocabile. L’esercizio del diritto di revoca non pregiudica le prestazioni già rese;""",
    "2": """INFORMATIVA AI SENSI DELL'ART. 13 DEL REG. UE 2016/679 <br>
Ai sensi dell.art 13 del Regolamento Europeo 2016/679 (di seguito GDPR) della normativa nazionale e dei Provvedimenti del Garante Privacy ed in relazione ai dati personali di cui la sottoscritta Veronica Lorenzini entrerà in possesso, 
La informo di quanto segue:<br>
1.	FINALITA DEL TRATTAMENTO E NATURA OBBLIGATORIA O FACOLTATIVA DEL CONTENUTO<br>
I Suoi dati personali, anche sensibili ai sensi dell'art. 9 GDPR saranno trattati dal Titolare, tramite l'utilizzo di strumenti informatici e/o cartacei, per una o più delle finalità seguenti:<br>

A)	Finalità connesse e strumentali alla corretta e completa esecuzione del mio incarico professionale commesso a tutte le attività di valutazione e trattamento manipolativo osteopatico svolte a tutela della Sua salute. Il conferimento dei Suoi dati per queste finalità è facoltativo. Tuttavia, il mancato conferimento del consenso comporterà l'impossibilità per il Titolare di erogare la prestazione richiesta. Potrà esprimere il proprio consenso, ai sensi dell'art. 6.1 e dell'art. 9.2 lett. a) GDPR sottoscrivendo l'apposito modulo rilasciato dal Titolare<br>

B)	Finalità connesse all'espletamento di obblighi normativi e fiscali, quali a titolo esemplificativo il rispetto degli obblighi di legge regolamento imposti dalla normativa comunitaria e/o nazionale, nonché di tutti gli adempimenti di carattere amministrativo e contabile collegati al pagamento delle prestazioni professionali erogate e/o alla gestione degli obblighi contrattuali con compagnie assicuratrici. Il conferimento dei dati per queste finalità non è soggetto al consenso conformemente a quanto previsto dall'art. 6.1 lett. b) e c) GDPR <br>

C)	Finalità connesse ad analisi statistiche. Rientra in questa tipologia l'impiego dei Suoi dati, anche sensibili, previa loro anonimizzazione, per ricerche e studi condotti dal Titolare.<br>
Per queste finalità il conferimento dei Suoi dati è facoltativo ed è subordinato alla prestazione del Suo consenso tramite la sottoscrizione dell'apposito modulo rilasciato dal Titolare.<br>

D)	Finalità connesse all'invio di materiale informativo. Rientrano in questa tipologia l'invio di newsletter e/o di comunicazione periodiche via e-mail su attività e servizi del Titolare.<br>
Per queste finalità il conferimento dei Sooi dati è facoltativo ed è subordinato alla prestazione del Suo consenso tramite la sottoscrizione dell'apposito modulo rilasciato dal Titolare.<br>

2.	MODALITÀ DEL TRATTAMENTO DEI DATI <br>
Il trattamento dei dati è realizzato per mezzo delle operazioni o complesso di operazioni indicato all'art. 2 del Reg. UE e attraverso l'utilizzo di strumenti informatici o cartacei.<br>
Il trattamento dei dati è svolto dal Titolare e/o dagli incaricati del trattamento.<br>
3.	COMUNICAZIONE DEI DATI<br>
Previo Suo consenso, per il perseguimento delle finalità di cui al punto 1 A), il Titolare potrà comunicare i Suoi dati personali e sensibili a familiari e/o a personale medico e, più in generale, sanitario da Lei indicato.<br>
Inoltre, i Suoi dati potranno essere comunicati senza il suo consenso a soggetti eventualmente deputati alla gestione di pratiche di rimborso e/o di verifica delle prestazioni erogate; enti previdenziali ed assistenziali, compagnie assicurative che, in qualità di titolari autonomi del trattamento offrono servizi di assistenza integrativa, forze di Polizia, autorità giudiziaria ed altri organismi di pubblica sicurezza. <br>
4.	DIFFUSIONE DEI DATI E TRASFERIMENTO DEI DATI ALL'ESTERO<br>
I Suoi dati personali:<br>
•	non sono soggetti a diffusione; non sono traferiti all'estero.<br>
5.	PERIODO DI CONSERVAZIONE DEI DATI<br>
I Suoi dati di natura sensibile verranno conservati, per il periodo di tempo previsto dalla normativa comunitaria, da leggi, o da regolamenti e comunque, per un periodo non superiore a quello strettamente necessario per adempiere agli incarichi conferiti.<br>
I dati personali non sensibili e funzionali all'assolvimento di obblighi di legge saranno conservati anche successivamente al termine della prestazione professionale erogata in ottemperanza a detti obblighi, nel più rigoroso rispetto delle tempistiche di conservazione di cui alle norme di volta in volta applicabili, e comunque per un periodo non superiore a 10 аnni.<br>
6.	DIRITTI DELL'INTERESSATO<br>
In qualità di interessato al trattamento, Lei potrà far valere i propri diritti, come espressi dagli artt. 15, 16, 17, 18, 19, 20, 21, 22 del Regolamento UE 2016/679, rivolgendosi al Titolare, oppure al Responsabile del trattamento, se indicato. Lei ha il diritto, in qualunque momento, di chiedere al Titolare del trattamento l'accesso ai Suoi dati personali, la rettifica, la cancellazione degli stessi, la limitazione del trattamento. Inoltre, ha il diritto di opporsi, in qualsiasi momento, al trattamento dei suoi dati (compresi i trattamenti automatizzati, es. la profilazione), nonché alla portabilità dei suoi dati. Fatto salvo ogni altro ricorso amministrativo e giurisdizionale, se ritiene che il trattamento dei dati che la riguardano violi quanto previsto dal Regolamento Europeo UR 2016/679, ai sensi dell'art. 15 lettera 1) del succitato Regolamento Europeo UE 2016/679, Lei ha il diritto di proporre reclamo al Garante per la protezione dei dati personali e, con riferimento all'art. 6 paragrafo 1, lettera a) e art. 9, paragrafo 2, lettera a) del medesimo Regolamento, ha il diritto di revocate in qualsiasi momento il consenso prestato. Nel caso di richiesta di portabilità del dato, il Titolare del trattamento Le fornirà in un formato strutturato, di uso comune e leggibile da dispositivo automatico, i dati personali che la riguardano, fatti salvi i commi 3 e 4 dell'art. 20 del Reg. UE 2016/679.<br>
7.	MODALITA' DI ESERCIZIO DEI DIRITTI<br>
Potrà in qualsiasi momento esercitare i diritti di cui sopra tramite:<br>
•	e-mail all'indirizzo lorenziniveronica77@gmail.com<br>
8.	TITOLARE, RESPONSABILI E INCARICATI<br>
La Titolare del trattamento è Veronica Lorenzini presso Virtus Group.<br>
Responsabile del trattamento à Veronica Lorenzini. L'elenco aggiornato dei responsabili e degli incaricati al trattamento è custodito presso la sede del Titolare del trattamento.<br>

""",
    "3": "[Informativa Dott. Verdi da inserire qui terza informativa]",
    "4": "[Informativa Dott. Neri da inserire qui quarta informativa]"
}

# ==========================
# 3) Inizializza Flask e pdfkit
# ==========================
app = Flask(__name__)
pdfkit_config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

# Definisci l'anno corrente per i menu a tendina
current_year = datetime.datetime.now().year

# ==========================
# 4) Template Homepage ("/") con logo
# ==========================
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
  <!-- Logo visibile solo in homepage -->
  <img src="/static/logo.png" alt="Logo">
  <div class="contact-info">
  <p>
  <strong>
    Nutrizione e terapia dello sport<br>
    Via Montello 79 – 25128 Brescia<br>
    Tel. 3518899843<br>
    Email: info@virtusbrixia.com
  </div>
  <h1>Seleziona lo Specialista</h1>
  <button onclick="window.location.href='/privacy/1'">Dott. Messineo</button>
  <button onclick="window.location.href='/privacy/2'">Dott. Lorenzini</button>
  <button onclick="window.location.href='/privacy/3'">Dott. Verdi</button>
  <button onclick="window.location.href='/privacy/4'">Dott. Neri</button>
  <button onclick="window.location.href='/privacy/4'">Dott. Gialli</button>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(home_template)

# ==========================
# 5) Template Privacy ("/privacy/<specialist>")
# ==========================
privacy_template = '''
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Modulo Informativa - {{ specialist_name }}</title>
  <style>
    body { font-family: Arial, sans-serif; padding: 20px; }
    h1 { margin-bottom: 20px; text-align: center; }
    .content { max-width: 800px; margin: 0 auto; line-height: 1.6; }
    button {
      display: block;
      margin: 30px auto;
      padding: 10px 20px;
      font-size: 1.2em;
      cursor: pointer;
    }
  </style>
</head>
<body>
  <h1>Modulo Informativa - {{ specialist_name }}</h1>
  <div class="content">
    <p>{{ privacy_text | safe}}</p>
{% if specialist == '2' %}
<form method="get" action="/form">
    <label><input type="radio" name="consenso1" value="acconsento" required> Acconsento al trattamento (punto A)</label><br>
    <label><input type="radio" name="consenso2" value="acconsento" required> Acconsento alle finalità statistiche (punto C)</label><br>
    <label><input type="radio" name="consenso3" value="acconsento" required> Acconsento comunicazione dati a familiari / sanitari</label><br>
    <input type="hidden" name="specialist" value="2">
   
</form>
{% else %}

{% endif %}
    
     <button onclick="window.location.href='/form?specialist={{ specialist }}'">Accetto</button>
  </div>
</body>
</html>
'''

@app.route('/privacy/<specialist>')
def privacy_view(specialist):
    spec_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    text = privacy_texts.get(specialist, "[Informativa da inserire qui]")
    return render_template_string(
        privacy_template,
        specialist_name=spec_name,
        privacy_text=text,
        specialist=specialist
    )

# ==========================
# 6) Template Form ("/form")
# ==========================
form_template = r'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Inserisci i tuoi dati</title>
    <style>
      body {
        font-family: Arial, sans-serif;
        padding: 20px;
        text-align: center;
      }
      h1 { margin-bottom: 20px; }
      form {
        display: inline-block;
        text-align: left;
        padding: 10px;
        border: 1px solid #ccc;
        border-radius: 8px;
      }
      label {
        display: block;
        margin-top: 10px;
        font-weight: bold;
      }
      input, select {
        font-size: 1em;
        padding: 5px;
        width: 300px;
        max-width: 100%%;
        margin-bottom: 10px;
        display: block;
      }
      input[type="submit"] {
        margin-top: 20px;
        font-size: 1.2em;
        padding: 10px 20px;
        display: block;
        margin: 20px auto 0 auto;
      }
      /* Canvas firma */
      #signature-pad {
        border: 1px solid #000;
        width: 300px;
        height: 100px;
      }
      .canvas-container {
        position: relative;
        display: inline-block;
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
      /* Stile date menù a tendina */
      .date-select.day { width: 50px; display: inline-block; }
      .date-select.month { width: 60px; display: inline-block; }
      .date-select.year { width: 80px; display: inline-block; }
      .date-sep { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Inserisci i tuoi dati</h1>
    <form action="/submit" method="post">
        <label for="nome">Nome:</label>
        <input type="text" id="nome" name="nome" required>
        
        <label for="cognome">Cognome:</label>
        <input type="text" id="cognome" name="cognome" required>

        <label for="indirizzo">Indirizzo:</label>
        <input type="text" id="indirizzo" name="indirizzo" required>

        <label for="luogo_nascita">Luogo di nascita:</label>
        <input type="text" id="luogo_nascita" name="luogo_nascita" required>
        
        <label for="codice_fiscale">Codice Fiscale (16 caratteri):</label>
        <input type="text" id="codice_fiscale" name="codice_fiscale" required pattern="^[A-Za-z0-9]{16}$" title="Inserisci 16 caratteri alfanumerici">
        
        <label>Data di nascita:</label>
        <div style="display: inline-block;">
          <!-- Giorno -->
          <select name="birth_day" class="date-select day" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>gg</option>
            {% for d in range(1, 32) %}
              <option value="{{ d }}">{{ '%02d'|format(d) }}</option>
            {% endfor %}
          </select>
          <span class="date-sep">/</span>
          <!-- Mese -->
          <select name="birth_month" class="date-select month" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>mm</option>
            {% for m in range(1, 13) %}
              <option value="{{ m }}">{{ '%02d'|format(m) }}</option>
            {% endfor %}
          </select>
          <span class="date-sep">/</span>
          <!-- Anno decrescente -->
          <select name="birth_year" class="date-select year" required onfocus="this.options[0].style.display='none';" onblur="if(this.selectedIndex===-1) this.options[0].style.display='block';">
            <option value="" disabled selected hidden>aaaa</option>
            {% for y in range(current_year, 1899, -1) %}
              <option value="{{ y }}">{{ y }}</option>
            {% endfor %}
          </select>
        </div>
        
        <!-- Sezione firma -->
        <label>Firma (usa la tavoletta o il dito):</label>
        <div class="canvas-container">
          <canvas id="signature-pad"></canvas>
          <button type="button" class="clear-btn" onclick="clearSignature()" title="Cancella firma">X</button>
        </div>
        <input type="hidden" id="signature_data" name="signature_data">
        
        <!-- Campo nascosto per passare lo specialista -->
        <input type="hidden" name="specialist" value="{{ specialist }}">
        {% if specialist == '2' %}
        <input type="hidden" name="consenso1" value="{{ consenso1 }}">
        <input type="hidden" name="consenso2" value="{{ consenso2 }}">
        <input type="hidden" name="consenso3" value="{{ consenso3 }}">
        {% endif %}
        
        <input type="submit" value="Invia">
    </form>
    
    <!-- Libreria Signature Pad -->
    <script src="https://cdn.jsdelivr.net/npm/signature_pad@4.0.0/dist/signature_pad.umd.min.js"></script>
    <script>
      var canvas = document.getElementById('signature-pad');
      var signaturePad = new SignaturePad(canvas);
      
      function clearSignature() {
        signaturePad.clear();
      }
      
      document.querySelector('form').addEventListener('submit', function(e) {
        if (!signaturePad.isEmpty()) {
          var dataURL = signaturePad.toDataURL();
          document.getElementById('signature_data').value = dataURL;
        } else {
          document.getElementById('signature_data').value = "";
        }
      });
    </script>
</body>
</html>
'''

@app.route('/form')
def show_form():
    specialist = request.args.get('specialist', '1')
    consenso1 = request.args.get('consenso1', '')
    consenso2 = request.args.get('consenso2', '')
    consenso3 = request.args.get('consenso3', '')
    
    return render_template_string(
        form_template,
        specialist=specialist,
        current_year=current_year,
        consenso1=consenso1,
        consenso2=consenso2,
        consenso3=consenso3
    )
# ==========================
# 7) Template Conferma ("/confirm")
# ==========================
confirm_template = r'''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Documento generato</title>
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      label { display: block; margin-top: 10px; }
      input { font-size: 1em; padding: 5px; width: 100%%; max-width: 300px; }
      input[type="submit"] { margin-top: 20px; font-size: 1.2em; padding: 10px 20px; }
      a { display: inline-block; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>Grazie, {{ nome }} {{ cognome }}!</h1>
    <p>Il tuo PDF è stato generato con successo: <strong>{{ pdf_file }}</strong>.</p>
    <hr>
    <h2>Invia il PDF via Email</h2>
    <form action="/send_email" method="post">
        <label for="destinatario">Inserisci l'indirizzo email a cui inviare il PDF:</label>
        <input type="email" id="destinatario" name="destinatario" required>
        <input type="hidden" name="pdf_file" value="{{ pdf_file }}">
        <input type="hidden" name="specialist" value="{{ specialist }}">
        <input type="hidden" name="nome" value="{{ nome }}">
        <input type="hidden" name="cognome" value="{{ cognome }}">
        <input type="submit" value="Invia Email">
    </form>
    <a href="/">Chiudi e torna all'inizio</a>
</body>
</html>
'''

@app.route('/submit', methods=['POST'])
def submit():
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    indirizzo = request.form.get('indirizzo', '').strip()
    codice_fiscale = request.form.get('codice_fiscale', '').strip()
    luogo_nascita = request.form.get('luogo_nascita', '').strip()
    birth_day = request.form.get('birth_day', '').strip()
    birth_month = request.form.get('birth_month', '').strip()
    birth_year = request.form.get('birth_year', '').strip()
    data_nascita = f"{birth_day}/{birth_month}/{birth_year}"
    specialist = request.form.get('specialist', '1').strip()
    firma_data = request.form.get('signature_data', '')

    consenso1 = request.form.get("consenso1", "Non indicato")
    consenso2 = request.form.get("consenso2", "Non indicato")
    consenso3 = request.form.get("consenso3", "Non indicato")

    if len(codice_fiscale) != 16:
        return f'''<h1>Errore</h1><p>Il codice fiscale deve contenere esattamente 16 caratteri.</p><p><a href="/form?specialist={specialist}">Torna al form</a></p>'''

    timestamp_str = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    folder_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    specialist_folder = os.path.join(SHARED_FOLDER, folder_name)
    os.makedirs(specialist_folder, exist_ok=True)

    filename_pdf = f"{nome}_{cognome}_{timestamp_str}.pdf"
    pdf_path = os.path.join(specialist_folder, filename_pdf)

    firma_img_tag = f'<img src="{firma_data}" alt="Firma" style="width:200px;"/>' if firma_data.startswith("data:image/png;base64,") else "<p><em>Nessuna firma</em></p>"

    informativa = privacy_texts.get(specialist, "[Informativa da inserire qui]")

    consensi_extra = ""
    if specialist == "2":
        consensi_extra = f"""
        <h3>Consensi specifici:</h3>
        <ul>
            <li>Consenso al trattamento (punto A): <strong>{consenso1}</strong></li>
            <li>Consenso alle finalità statistiche (punto C): <strong>{consenso2}</strong></li>
            <li>Consenso comunicazione a familiari/sanitari: <strong>{consenso3}</strong></li>
        </ul>
        """

    if specialist == "2":
        frase_iniziale = f"""
        Io sottoscritto/a <strong>{nome} {cognome}</strong>, nato/a a <strong>{luogo_nascita}</strong> il <strong>{data_nascita}</strong>,
        e residente in <strong>{indirizzo}</strong>, acquisite le summenzionate informazioni fornite
        dal Titolare del trattamento ai sensi dell’art. 13 del Reg. UE, e consapevole, in particolare,
        che il trattamento potrà riguardare dati relativi alla salute, presto il mio consenso per il trattamento dei suddetti dati
        per le finalità di cui al punto 1, lett. A) dell’informativa.
        """
    else:
        frase_iniziale = f"""
        Il/la sottoscritto/a {nome} {cognome}, residente in {indirizzo}, Codice Fiscale: {codice_fiscale}, nato/a il {data_nascita}<br>
        <strong>dopo avere letto la superiore informativa, dà il consenso al trattamento dei dati che lo riguardano per le finalità ivi indicate.</strong>
        """

    # HTML completo con la frase dinamica
    pdf_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>Documento - {nome} {cognome}</title>
    </head>
    <body>
      <div style="text-align: justify; line-height:1.6; font-family: Arial; font-size: 14px;">
        <h1 style="text-align:center;">Informativa {specialist_names.get(specialist, '')}</h1>
        <p>{informativa}</p>
        <hr>
        <p>{frase_iniziale}</p>
        {consensi_extra}
        <hr>
        <h2>Firma</h2>
        <p>{firma_img_tag}</p>
        <p>Data compilazione: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}</p>
      </div>
    </body>
    </html>
    """

    pdfkit.from_string(pdf_html, pdf_path, configuration=pdfkit_config)
    
    return render_template_string(
        confirm_template,
        nome=nome,
        cognome=cognome,
        pdf_file=filename_pdf,
        specialist=specialist
    )

# ==========================
# 9) Rotta /send_email: invia PDF via email
# ==========================
@app.route('/send_email', methods=['POST'])
def send_email():
    destinatario = request.form.get('destinatario', '').strip()
    pdf_file = request.form.get('pdf_file', '').strip()
    specialist = request.form.get('specialist', '1').strip()
    nome = request.form.get('nome', '').strip()
    cognome = request.form.get('cognome', '').strip()
    indirizzo = request.form.get('indirizzo', '').strip()

    folder_name = specialist_names.get(specialist, f"Specialista_{specialist}")
    pdf_full_path = os.path.join(SHARED_FOLDER, folder_name, pdf_file)

    if not os.path.exists(pdf_full_path):
        return f"<h1>Errore: il file {pdf_full_path} non esiste sul server</h1>"

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    USERNAME = EMAIL_USERNAME
    PASSWORD = EMAIL_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = USERNAME
    msg['To'] = destinatario
    msg['Subject'] = f"Documento firmato: {nome} {cognome}"

    corpo = f"Ciao,\nin allegato il PDF firmato da {nome} {cognome}.\n\nSaluti."
    msg.attach(MIMEMultipart('alternative'))
    msg.get_payload()[0].set_payload(corpo)

    with open(pdf_full_path, 'rb') as f:
        parte = MIMEBase('application', 'octet-stream')
        parte.set_payload(f.read())
    encoders.encode_base64(parte)
    parte.add_header('Content-Disposition', f'attachment; filename=\"{pdf_file}\"')
    msg.attach(parte)

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
        server.quit()
        return f"""
        <h1>Email inviata con successo a {destinatario}!</h1>
        <p><a href="/">Torna all'inizio</a></p>
        """
    except Exception as e:
        return f"<h1>Errore durante l'invio email:</h1><p>{str(e)}</p>"

# ==========================
# 10) Avvio dell'app
# ==========================
if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=8080)
