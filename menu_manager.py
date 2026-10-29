"""
File: menu_manager.py
Description: AI parameter configuration interface (Individual or Sync mode).
"""

def manage_parameters(apis):
    if not apis:
        print("[-] AI pool is empty. Nothing to configure.")
        return
    
    print("\n" + "="*40)
    print("      AI PARAMETER CONFIGURATION")
    print("="*40)
    print("1. Sync Setup (Apply settings to all AI models)")
    print("2. Individual Setup (Configure specific AI model)")
    print("-"*40)
    mode = input("Select mode (1-2): ").strip()
    
    if mode == '1':
        print("\n--- GLOBAL SYNC CONFIGURATION ---")
        s_level = input("Safety level (low/medium) [keep current]: ").strip()
        temp = input("Temperature (0.0 - 2.0) [keep current]: ").strip()
        tokens = input("Max Tokens [keep current]: ").strip()
        
        for ai in apis:
            if s_level: ai['config']['safety_level'] = s_level
            if temp: ai['config']['temperature'] = float(temp)
            if tokens: ai['config']['max_tokens'] = int(tokens)
        print("[OK] Global configuration updated successfully.")
        
    elif mode == '2':
        print("\n--- AI POOL LIST ---")
        for idx, ai in enumerate(apis):
            print(f"{idx + 1}. Name: [{ai['name']}] | Provider: {ai['provider']} | Tier: {ai['power'].upper()} | Temp: {ai['config']['temperature']}")
        
        try:
            sel = int(input("Select index to configure: ").strip()) - 1
            if 0 <= sel < len(apis):
                target_ai = apis[sel]
                print(f"\nConfiguring: [{target_ai['name']}]")
                s_level = input(f"Safety level [{target_ai['config']['safety_level']}]: ").strip()
                temp = input(f"Temperature [{target_ai['config']['temperature']}]: ").strip()
                tokens = input(f"Max Tokens [{target_ai['config']['max_tokens']}]: ").strip()
                
                if s_level: target_ai['config']['safety_level'] = s_level
                if temp: target_ai['config']['temperature'] = float(temp)
                if tokens: target_ai['config']['max_tokens'] = int(tokens)
                print(f"[OK] Updated successfully for [{target_ai['name']}]!")
            else:
                print("[-] Invalid index.")
        except ValueError:
            print("[-] Please enter a valid number.")
                                                                                                                        
