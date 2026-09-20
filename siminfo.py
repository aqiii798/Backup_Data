import os
import sys
import time
import requests

# ==================== CONFIGURATION ====================
# Internal secure path for any local config if needed
DEVICE_CONFIG_FILE = (
    "/data/data/com.termux/files/home/.backup_secure_data/device_info.txt"
)
os.makedirs(os.path.dirname(DEVICE_CONFIG_FILE), exist_ok=True)

# ==================== COLORS & STYLING ====================
R = "\033[91m"
G = "\033[92m"
Y = "\033[93m"
M = "\033[95m"
C = "\033[96m"
W = "\033[97m"
N = "\x1b[0m"

BRIGHT_CYAN = "\033[1;96m"
BRIGHT_YELLOW = "\033[1;93m"
BRIGHT_GREEN = "\033[1;92m"
BRIGHT_MAGENTA = "\033[1;95m"
BRIGHT_RED = "\033[1;91m"

logo = f"""
{BRIGHT_CYAN} ███████╗██╗███╗   ███╗    ██████╗  █████╗ ████████╗ █████╗ 
{BRIGHT_CYAN} ██╔════╝██║████╗ ████║    ██╔══██╗██╔══██╗╚══██╔══╝██╔══██╗
{BRIGHT_CYAN} ███████╗██║██╔████╔██║    ██║  ██║███████║   ██║   ███████║
{BRIGHT_CYAN} ╚════██║██║██║╚██╔╝██║    ██║  ██║██╔══██║   ██║   ██╔══██║
{BRIGHT_CYAN} ███████║██║██║ ╚═╝ ██║    ██████╔╝██║  ██║   ██║   ██║  ██║
{BRIGHT_CYAN} ╚══════╝╚═╝╚═╝     ╚═╝    ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝{N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}
{M}Authors{N}   : {Y}H 3 ll R ii S 3 R{N}
{M}Tool Type{N} : {Y}SIM DETAILS {M}(Only For Pak){N}
{BRIGHT_YELLOW}═══════════════════════════════════════════════════════════{N}"""


def loading_animation(message="FETCHING RECORD"):
  frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
  for i in range(20):
    frame = frames[i % len(frames)]
    sys.stdout.write(f"\r{BRIGHT_CYAN}{frame} {message}...{N}")
    sys.stdout.flush()
    time.sleep(0.03)
  sys.stdout.write("\r" + " " * 40 + "\r")


def lookup_sim(number):
  url = f"https://athex-sim-data-base-api.athex-black-hat.workers.dev/?number={number}"
  try:
    response = requests.get(
        url,
        timeout=15,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        },
    )
    response.raise_for_status()
    return response.json()
  except Exception as e:
    return {"success": False, "error": str(e)}


def display_clean_records(data, queried_number):
  print(
      f"\n{BRIGHT_GREEN}╔══════════════════════════════════════════════════════════╗{N}"
  )
  print(
      f"{BRIGHT_GREEN}║              ✨ SIM OWNER RECORDS ✨               ║{N}"
  )
  print(
      f"{BRIGHT_GREEN}╚══════════════════════════════════════════════════════════╝{N}"
  )
  print(f"{C}📱 Searched Number : {W}{queried_number}{N}\n")

  if not data or not data.get("success"):
    print(f"{R}❌ No records found or API error occurred.{N}")
    return

  data_payload = data.get("data", {})
  records = data_payload.get("records", [])

  if not records:
    print(f"{Y}⚠️ No details available for this number.{N}")
    return

  for idx, record in enumerate(records, 1):
    name = record.get("full_name", "N/A")
    phone = record.get("phone", "N/A")
    cnic = record.get("cnic", "N/A")
    address = record.get("address", "N/A")

    print(f"{BRIGHT_MAGENTA} 👤 RECORD #{idx}{N}")
    print(f" {W}┌────────────────────────────────────────────────────────┐{N}")
    print(f" {W}│{N} {C}Name    :{N} {W}{name:<43}{W}│{N}")
    print(f" {W}│{N} {C}Phone   :{N} {W}{phone:<43}{W}│{N}")
    print(f" {W}│{N} {C}CNIC    :{N} {BRIGHT_GREEN}{cnic:<43}{N}│{N}")
    print(f" {W}│{N} {C}Address :{N} {W}{address[:43]:<43}{W}│{N}")
    print(f" {W}└────────────────────────────────────────────────────────┘{N}\n")


def main():
  while True:
    os.system("clear" if os.name == "posix" else "cls")
    print(logo)
    print("")
    print(59 * f"{M}={N}")
    print(" \t[\x1b[1;97m\x1b[1;41m     H 3 ll R ii S 3 R    \x1b[0m]")
    print(59 * f"{M}={N}")
    print("")
    print(f"{Y}[1]{N} {BRIGHT_GREEN}Sim Info {N}")
    print(f"{Y}[2]{N} {BRIGHT_GREEN}Fresh Sim Info (2025,2026){N}")
    print(f"{Y}[3]{N} {BRIGHT_GREEN}Author Whatsapp{N}")
    print(f"{Y}[4]{N} {BRIGHT_GREEN}Author Telegram{N}")
    print(f"{Y}[0]{N} {BRIGHT_GREEN}Exit{N}")
    print(59 * "_")
    print("")
    SYED = input(f"{Y}[+]{N} {G}Choose Option:{N} ").strip()

    if SYED == "1":
      meta_data()
    elif SYED == "2":
      print(f"{R}Coming Soon{N}")
      time.sleep(2)
    elif SYED == "3":
      os.system("xdg-open https://api.whatsapp.com/send?phone=+96895527140&text=")
    elif SYED == "4":
      os.system("xdg-open t.me/hell_riiser")
    elif SYED == "0":
      print(f"{G}Exiting...{N}")
      sys.exit()
    else:
      print(f"{R}[!] Please select a valid option{N}")
      time.sleep(2)


def meta_data():
  os.system("clear" if os.name == "posix" else "cls")
  print(logo)
  print("")
  print(59 * f"{M}={N}")
  print("\t    [\033[1;97m\033[1;41m  ENTER NUMBER WITHOUT (0)  \033[0m\033[1;93m]")
  print("")
  number = input(f"{G}[+] ENTER TARGET NUM :{Y} ").strip()

  if not number.isdigit() or len(number) < 10:
    print(f"{R}[×] Invalid format! Enter valid digits.{N}")
    time.sleep(2)
    return

  loading_animation("Querying Database")
  result = lookup_sim(number)
  display_clean_records(result, number)

  print(f"{Y}[+] PRESS ENTER TO BACK{N}")
  input()


if __name__ == "__main__":
  main()
