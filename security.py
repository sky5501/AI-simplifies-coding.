"""
File: security.py
Description: Termux/GitHub operation permission handler.
"""

import config

def check_permission_or_request():
    if not config.PERMISSION_GRANTED:
        print("\n[!] SECURITY WARNING: Access permission not granted!")
        ans = input("[?] Do you grant permission for Termux/AI to interact with GitHub? (y/n): ").strip().lower()
        if ans == 'y':
            config.PERMISSION_GRANTED = True
            print("[+] Permission granted successfully.")
            return True
        else:
            print("[-] Access denied. Operation aborted.")
            return False
    return True
  
