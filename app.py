from flask import Flask, render_template
from flask_socketio import SocketIO
import psutil
import time
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get the number of logical CPU cores
num_cores = psutil.cpu_count()

def fetch_process_data():
    while True:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                # Normalize CPU usage by number of cores
                proc.info['cpu_percent'] = proc.info['cpu_percent'] / num_cores
                processes.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Emit the process data to connected clients
        socketio.emit('update', processes)
        time.sleep(1)  # Update every 1 second

# Start the background thread to fetch data
threading.Thread(target=fetch_process_data, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
