<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <title>Modulo con Firma</title>
  <style>
    /* Stile per il canvas della firma */
    #signature-pad { border: 1px solid #000; width:300px; height:100px; }
  </style>
</head>
<body>
  <h2>Modulo da Firmare</h2>
  <form id="formFirma" action="/generate_pdf" method="POST">
    <label for="name">Nome:</label>
    <input type="text" name="name" id="name" required><br><br>
    <label>Firma:</label><br>
    <!-- Canvas per la firma -->
    <canvas id="signature-pad" width="300" height="100"></canvas><br>
    <button type="button" onclick="clearPad()">Cancella</button>
    <!-- Campo nascosto per la stringa Base64 della firma -->
    <input type="hidden" name="signature_data" id="signature_data">
    <br><button type="button" onclick="submitForm()">Invia</button>
  </form>

  <script>
    const canvas = document.getElementById('signature-pad');
    const ctx = canvas.getContext('2d');
    let drawing = false;

    // Eventi mouse per disegnare sul canvas
    canvas.addEventListener('mousedown', e => {
      drawing = true;
      ctx.beginPath();
      ctx.moveTo(e.offsetX, e.offsetY);
    });
    canvas.addEventListener('mousemove', e => {
      if (drawing) {
        ctx.lineTo(e.offsetX, e.offsetY);
        ctx.stroke();
      }
    });
    canvas.addEventListener('mouseup', e => { drawing = false; });
    canvas.addEventListener('mouseleave', e => { drawing = false; });

    // Cancella il canvas
    function clearPad() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // Converte la firma in immagine Base64 e invia il form
    function submitForm() {
      const dataURL = canvas.toDataURL('image/png');  // ottiene immagine in Base64
      document.getElementById('signature_data').value = dataURL;
      document.getElementById('formFirma').submit();
    }
  </script>
</body>
</html>
