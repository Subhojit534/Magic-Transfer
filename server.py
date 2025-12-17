import socketio
import eventlet
from flask import Flask, render_template
import socket

# Initialize Flask and SocketIO
sio = socketio.Server(cors_allowed_origins='*')
flask_app = Flask(__name__)
app = socketio.WSGIApp(sio, flask_app)

# The "Cloud Clipboard"
cloud_clipboard = {
    "data": None,
    "type": None,
    "sender_id": None
}

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# Serve the HTML App
@flask_app.route('/')
def index():
    return render_template('index.html')

# --- EVENTS ---

@sio.event
def connect(sid, environ):
    print(f"[+] Connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"[-] Disconnected: {sid}")

# Handle PC Grab
@sio.event
def grab_data(sid, data):
    print(f"\n[GRAB] Data stored from {sid}")
    cloud_clipboard["data"] = data["image_data"]
    cloud_clipboard["type"] = "image"
    cloud_clipboard["sender_id"] = sid
    sio.emit('server_response', {'message': 'Copied! Ready to Drop.'}, to=sid)

# Handle Browser Drop Request
@sio.event
def request_drop(sid):
    print(f"\n[DROP] Request from {sid}")
    
    if cloud_clipboard["data"]:
        print(" -> Transferring file...")
        sio.emit('receive_drop', {
            'image_data': cloud_clipboard["data"]
        }, to=sid)
        
        # --- FIX: CLEAR THE CLIPBOARD ---
        print(" -> File released! Clearing memory.")
        cloud_clipboard["data"] = None
        cloud_clipboard["type"] = None
        cloud_clipboard["sender_id"] = None
        
    else:
        sio.emit('server_response', {'message': 'Clipboard is empty!'}, to=sid)

if __name__ == '__main__':
    ip = get_local_ip()
    port = 5000
    print("\n=======================================")
    print(f"   MOBILE URL: http://{ip}:{port}")
    print("=======================================\n")
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', port)), app)