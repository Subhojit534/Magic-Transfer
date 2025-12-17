# Magic-Transfer

**A Cross-Device "Air Gesture" Copy-Paste Tool powered by Computer Vision.**

> *Inspired by the Huawei "Air Gesture" feature.*

Magic Drop allows you to **"grab"** a screenshot from your PC screen using a pinch gesture and **"drop"** it onto your mobile device by simply opening your hand. It uses **MediaPipe** for hand tracking, **OpenCV** for image processing, and **WebSockets** for real-time data transfer.

![Project Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Features

* **Gesture Recognition:** Uses Google's MediaPipe to detect hand landmarks with high precision.
* **Smart State Machine:**
    * **Pinch (PC):** Triggers a screen capture.
    * **Open Hand (Mobile):** Triggers the file transfer.
* **Real-time Transfer:** Uses Socket.IO for low-latency communication between devices.
* **Automatic Optimization:** Compresses screenshots to JPEG to ensure instant transfer over Wi-Fi.
* **Cross-Platform:** The receiver runs in a web browser, making it compatible with iOS, Android, and Tablets.

---

## 🛠️ Tech Stack

* **Computer Vision:** OpenCV, MediaPipe
* **Backend:** Python (Flask, Socket.IO, Eventlet)
* **Frontend (Mobile):** HTML5, JavaScript (MediaPipe JS), Socket.IO Client
* **Utilities:** PyAutoGUI (Screenshot), PIL (Image Processing)

---

## 📂 Project Structure

**Important:** Flask requires HTML files to be inside a `templates` folder.

```text
├── magic_hand.py          # The PC Client (Camera + Gesture Detection + Screenshot)
├── server.py              # The Relay Server (Handles the "Cloud Clipboard")
├── templates/             # Folder for HTML files
│   └── index.html         # The Mobile Web App (Camera + Gesture Detection + Display)
└── requirements.txt       # Python Dependencies


⚙️ Installation & Setup
1. Prerequisites
Python 3.8 or higher installed.

A Webcam connected to your PC.

A Mobile device with a camera and a modern browser (Chrome/Safari).

Both devices must be on the same Wi-Fi network.

2. Organize Files
Ensure your folder looks like this so the server can find the website:

Create a folder named templates.

Move index.html inside that folder.

3. Install Dependencies
Open your terminal in the project directory and run:

Bash

pip install -r requirements.txt
(Note: If you encounter issues with eventlet, ensure you are not running another heavy async process).

🏃‍♂️ How to Run
Step 1: Start the Server
The server acts as the bridge between your PC and Mobile.

Bash

python server.py
Look at the output! The server will print a URL, for example:

MOBILE URL: http://192.168.1.5:5000

Step 2: Start the PC Client
Open a new terminal and run the gesture recognition script for your computer.

Bash

python magic_hand.py
A window will open showing your webcam feed.

Status should change to [Connected] Linked to Server!.

Step 3: Connect Mobile Device
Open the browser on your phone.

Type in the MOBILE URL generated in Step 1 (e.g., http://192.168.x.x:5000).

Allow camera permissions when prompted.

You should see your phone camera feed and the status: ✅ Watching Hand....

🎮 Usage Guide
1. The GRAB (On PC)
Look at your PC webcam.

Bring your hand up and make a Pinch Gesture (touch your thumb tip to your index finger tip).

Visual Cue: The screen will flash, and the text will change to "HOLDING FILE".

The screenshot is now stored in the server's memory.

2. The DROP (On Mobile)
Look at your phone screen.

Show an Open Palm to the camera (spread your fingers).

Visual Cue: The status will change to ⚡ Dropping....

Result: The screenshot taken on your PC will instantly appear on your phone screen!

🔧 Troubleshooting
"Server not found" / Connection Refused:

Ensure both devices are on the same Wi-Fi.

Your PC's firewall might be blocking port 5000. Try temporarily disabling the firewall or allowing the port.

Mobile Camera not working:

Ensure you are using http:// (not https) and that your browser allows camera access for insecure origins on local networks (common in Chrome flags).

TemplateNotFound Error:

Ensure index.html is exactly inside the templates folder, not in the main directory.
