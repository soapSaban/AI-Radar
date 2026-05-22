import serial
import threading
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify
import logging

# Silence the Flask HTTP spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Load the Neural Network
print("[ LOADING RADAR BRAIN... ]")
model = tf.keras.models.load_model('radar_brain.keras')
print("[ AI ONLINE ]")

telemetry = {
    "distance": 0.0,
    "ldr_l": 0,
    "ldr_r": 0,
    "temp": 0.0,
    "state": "SCANNING...",
    "confidence": 0
}

def read_serial():
    try:
        ser = serial.Serial('COM5', 115200, timeout=1)
        print("\n[ ARDUINO LINK ESTABLISHED: LISTENING FOR DATA ]\n")
        
        while True:
            try:
                # The X-Ray
                raw_bytes = ser.readline()
                print(f"RAW: {raw_bytes}") 
                
                line = raw_bytes.decode('utf-8').strip()
                if line:
                    parts = line.split(',')
                    if len(parts) == 4:
                        dist = float(parts[0])
                        ldrl = int(parts[1])
                        ldrr = int(parts[2])
                        temp = float(parts[3])
                        
                        telemetry["distance"] = dist
                        telemetry["ldr_l"] = ldrl
                        telemetry["ldr_r"] = ldrr
                        telemetry["temp"] = temp

                        live_data = np.array([[dist, ldrl, ldrr, temp]])
                        prediction = model.predict(live_data, verbose=0)[0][0]
                        
                        if prediction >= 0.5:
                            telemetry["state"] = "GAMING"
                            telemetry["confidence"] = int(prediction * 100)
                        else:
                            telemetry["state"] = "CODING"
                            telemetry["confidence"] = int((1.0 - prediction) * 100)
                            
            except ValueError:
                pass # Ignore math errors from garbled lines
            except Exception as loop_err:
                pass
                
    except Exception as e:
        print(f"\n[ CRITICAL SERIAL ERROR ] {e}\n")

# Start the Arduino listener in the background BEFORE the web server starts
threading.Thread(target=read_serial, daemon=True).start()

# --- THE MOBILE UI DASHBOARD ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Radar Command</title>
    <style>
        body { background-color: #0d0d0d; color: #00FF00; font-family: 'Courier New', Courier, monospace; text-align: center; padding-top: 20vh; margin: 0;}
        .state { font-size: 3.5em; font-weight: bold; margin-bottom: 30px; transition: color 0.3s; }
        .data-box { background: #1a1a1a; border: 1px solid #333; border-radius: 10px; padding: 20px; width: 80%; max-width: 400px; margin: 0 auto; }
        .data { font-size: 1.2em; color: #aaaaaa; margin: 10px 0; }
        .val { color: #ffffff; font-weight: bold; }
        .gaming { color: #ff3333; text-shadow: 0 0 15px #ff3333; }
        .coding { color: #33ccff; text-shadow: 0 0 15px #33ccff; }
    </style>
</head>
<body>
    <div id="state" class="state coding">[ BOOTING ]</div>
    
    <div class="data-box">
        <div class="data">RADAR DIST: <span id="dist" class="val">0.0</span> cm</div>
        <div class="data">EXHAUST TEMP: <span id="temp" class="val">0.0</span> &deg;C</div>
        <hr style="border-color: #333;">
        <div class="data">OPTIC L: <span id="ldrl" class="val">0</span> | OPTIC R: <span id="ldrr" class="val">0</span></div>
    </div>

    <script>
        setInterval(() => {
            fetch('/data').then(r => r.json()).then(data => {
                let st = document.getElementById('state');
                st.innerText = "[ " + data.state + " ]";
                
                if(data.state === "GAMING") { st.className = "state gaming"; }
                else { st.className = "state coding"; }
                
                document.getElementById('dist').innerText = data.distance;
                document.getElementById('temp').innerText = data.temp;
                document.getElementById('ldrl').innerText = data.ldr_l;
                document.getElementById('ldrr').innerText = data.ldr_r;
            });
        }, 250); 
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return HTML_TEMPLATE

@app.route('/data')
def data():
    return jsonify(telemetry)

if __name__ == '__main__':
    print("\n[ WEB UI ONLINE ] Open this exact link on your phone:")
    print("http://192.168.29.120:5000n")
    app.run(host='0.0.0.0', port=5000)