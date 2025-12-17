import cv2
import mediapipe as mp
import math
import socketio
import base64
import pyautogui
from io import BytesIO
import time
import numpy as np

# --- CONFIGURATION ---
SERVER_URL = 'http://localhost:5000'
GRAB_THRESHOLD = 40   # Pinch distance
DROP_THRESHOLD = 120  # Open hand distance
WINDOW_NAME = "Magic Hand - Huawei Clone"

# --- SETUP ---
sio = socketio.Client()
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
camera = cv2.VideoCapture(0)

# State Machine
state = "IDLE" 
last_action_time = 0
cooldown = 2.0 
is_connected = False
flash_counter = 0 # For visual effect

# --- WEBSOCKETS ---
@sio.event
def connect():
    global is_connected
    is_connected = True
    print("[Connected] Linked to Server!")

@sio.event
def disconnect():
    global is_connected
    is_connected = False
    print("[Disconnected] Lost connection.")

# NEW: Listen for the server telling us the transfer is done
@sio.event
def transfer_completed(data):
    global state
    print(f"\n[SUCCESS] File transferred to {data.get('to_device', 'mobile')}!")
    print("[RESET] Resetting state to IDLE.")
    state = "IDLE"

def connect_to_server():
    try:
        sio.connect(SERVER_URL)
    except:
        print("!! Server not found. Run server.py first! !!")

connect_to_server()

# --- HELPER FUNCTIONS ---
def calculate_distance(p1, p2):
    return math.hypot(p2.x - p1.x, p2.y - p1.y)

def take_screenshot_as_base64():
    # Capture the entire primary screen
    screenshot = pyautogui.screenshot()
    
    # Debug info
    print(f"Captured Screenshot Size: {screenshot.size}")
    
    # --- FIX FOR DISCONNECTS: OPTIMIZE IMAGE ---
    # 1. Convert to RGB (JPEG needs this)
    screenshot = screenshot.convert("RGB")
    
    # 2. Resize if huge (max width 1280) to keep transfer fast
    # This prevents the socket from crashing due to large payloads
    screenshot.thumbnail((1280, 720)) 
    
    buffered = BytesIO()
    # 3. Save as JPEG (Quality 70) instead of PNG
    # This reduces size from ~3MB to ~200KB (15x faster)
    screenshot.save(buffered, format="JPEG", quality=70)
    
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    print(f"Encoded Image Size: {len(img_str)/1024:.2f} KB") # Print size to check
    return img_str

# --- MAIN LOOP ---
print("Camera Active. Press 'q' to quit.")

while True:
    ret, frame = camera.read()
    if not ret: break
    
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process Hands
    result = hands.process(rgb_frame)
    
    status_text = f"Status: {state}"
    color = (0, 255, 0)
    
    if result.multi_hand_landmarks:
        for hand_lms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            p4 = hand_lms.landmark[4]  # Thumb Tip
            p8 = hand_lms.landmark[8]  # Index Tip
            
            x4, y4 = int(p4.x * w), int(p4.y * h)
            x8, y8 = int(p8.x * w), int(p8.y * h)
            
            # Draw Fingers
            cv2.circle(frame, (x4, y4), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (x8, y8), 10, (255, 0, 255), cv2.FILLED)
            
            distance = calculate_distance(p4, p8) * w
            current_time = time.time()
            
            # --- LOGIC ---
            # 1. GRAB (Pinch)
            if distance < GRAB_THRESHOLD and state == "IDLE":
                if current_time - last_action_time > cooldown:
                    state = "HOLDING"
                    last_action_time = current_time
                    flash_counter = 10 # Trigger flash effect
                    print("[ACTION] GRAB! Capturing Screen...")
                    
                    if is_connected:
                        b64_image = take_screenshot_as_base64()
                        sio.emit('grab_data', {'image_data': b64_image})
                    else:
                        print("Server not connected.")

            # 2. DROP (Open Hand) - Just resets state here
            elif distance > DROP_THRESHOLD and state == "HOLDING":
                if current_time - last_action_time > cooldown:
                    state = "IDLE"
                    last_action_time = current_time
                    print("[ACTION] RELEASED")

    # --- UI & EFFECTS ---
    if state == "HOLDING":
        status_text = "HOLDING FILE"
        color = (0, 165, 255)
        cv2.putText(frame, "FILE IN HAND", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Flash effect when screenshot is taken
    if flash_counter > 0:
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (255, 255, 255), -1)
        alpha = flash_counter / 20.0
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        flash_counter -= 1

    # Connection Dot
    conn_color = (0, 255, 0) if is_connected else (0, 0, 255)
    cv2.circle(frame, (w - 30, 30), 10, conn_color, -1)
    
    cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    cv2.imshow(WINDOW_NAME, frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
sio.disconnect()