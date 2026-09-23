from flask import Flask, render_template_string, jsonify
import threading
import time
import serial
import random

app = Flask(__name__)

# Inizializziamo a 0 come intero
ultimo_dato = 0 
PORTA_SERIALE = 'COM3'

def leggi_dati():
    global ultimo_dato
    try:
        # errors='ignore' evita crash se arrivano byte sporchi via radio
        ser = serial.Serial(PORTA_SERIALE, 115200, timeout=1)
        while True:
            if ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8', errors='ignore').strip()
                if linea:
                    # STAMPA DI DEBUG: Vediamo cosa arriva davvero!
                    print(f"Ricevuto dal sensore: '{linea}'") 
                    
                    try:
                        # Se il sensore manda la virgola (es. 25,4), la cambiamo in punto
                        linea_pulita = linea.replace(',', '.')
                        
                        # Convertiamo in float e poi tronchiamo a int
                        ultimo_dato = int(float(linea_pulita))
                    except ValueError:
                        print(f"ATTENZIONE: Impossibile convertire '{linea}' in numero.")
                        # Non mettiamo più pass, almeno vediamo l'errore a schermo
    except Exception as e:
        print(f"Errore connessione seriale: {e}")
        ultimo_dato = "Errore"

#def simula_dati():
#    global ultimo_dato
#    while True:
#        ultimo_dato = random.randint(10, 90)
#        time.sleep(5)

threading.Thread(target=leggi_dati, daemon=True).start()

PAGINA_HTML = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>Sensore di temperatura</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { margin: 0; font-family: Arial, sans-serif; display: flex; height: 100vh; background-color: #f4f6f9; }

        #pannello {
            width: 250px;
            background-color: #2c3e50;
            color: white;
            padding: 20px;
            box-shadow: 2px 0 5px rgba(0,0,0,0.1);
        }
        #pannello h1 { margin-top: 0; font-size: 24px; border-bottom: 2px solid #34495e; padding-bottom: 10px; }
        .valore-box { margin-top: 30px; padding: 15px; background: #34495e; border-radius: 8px; text-align: center; }
        .valore-box span { display: block; font-size: 40px; font-weight: bold; color: #e74c3c; margin-top: 10px;}

        #main { flex-grow: 1; padding: 30px; display: flex; flex-direction: column; }
        .grafico-container { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); flex-grow: 1; }
    </style>
</head>
<body>

    <div id="pannello">
        <h1>Dashboard</h1>
        <p>Ricevitore Radio</p>

        <div class="valore-box">
            Dato Attuale:
            <span id="testo-dato">--</span>
        </div>
    </div>

    <div id="main">
        <h2 style="color: #333; margin-top: 0;">Grafico</h2>
        <div class="grafico-container">
            <canvas id="mioGrafico"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('mioGrafico').getContext('2d');
        const grafico = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Temperatura',
                    data: [],
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        setInterval(async () => {
            const risposta = await fetch('/api/dati');
            const json = await risposta.json();
            
            // Forziamo il dato a intero anche in JavaScript per sicurezza
            const nuovoDato = parseInt(json.valore, 10);

            if (!isNaN(nuovoDato)) {
                // Niente più .toFixed(2) dato che ora è un numero intero
                document.getElementById('testo-dato').innerText = nuovoDato;

                const oraAttuale = new Date().toLocaleTimeString();
                grafico.data.labels.push(oraAttuale);
                grafico.data.datasets[0].data.push(nuovoDato);

                if (grafico.data.labels.length > 15) {
                    grafico.data.labels.shift();
                    grafico.data.datasets[0].data.shift();
                }

                grafico.update();
            } else {
                document.getElementById('testo-dato').innerText = "Errore/Attesa";
            }
        }, 10000); // Aggiorna ogni 10 secondi
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(PAGINA_HTML)

@app.route('/api/dati')
def api_dati():
    return jsonify({"valore": ultimo_dato})

if __name__ == '__main__':
    app.run(port=5000, use_reloader=False)
    
