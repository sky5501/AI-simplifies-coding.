"""
File: ai_engine.py
Description: API key parser, multi-provider caller, and automated failover engine.
"""

import os
import json
import urllib.request
import urllib.error

def detect_and_parse_apis(api_keys_str):
    keys = [k.strip() for k in api_keys_str.split(",") if k.strip()]
    connected_apis = []
    
    for i, key in enumerate(keys):
        provider = "Unknown"
        if key.startswith("sk-proj-") or (key.startswith("sk-") and len(key) > 30):
            provider = "OpenAI"
        elif key.startswith("sk-ant-"):
            provider = "Anthropic"
        elif key.startswith("AIza"):
            provider = "Gemini"
        elif key.startswith("gsk_"):
            provider = "Groq"
        elif key.startswith("sk-"):
            provider = "DeepSeek/Custom"
        else:
            provider = "Generic-API"
        
        print(f"\n--- CONFIGURING TOKEN #{i+1} ({provider}) ---")
        custom_name = input(f"Enter custom alias (press Enter for default): ").strip()
        if not custom_name:
            custom_name = f"{provider}-AI-{i+1}"
            
        power_level = input(f"Select power tier ([tb] Standard / [manh] Power) [default: tb]: ").strip().lower()
        if power_level not in ["tb", "manh"]:
            power_level = "tb"
            
        default_config = {
            "safety_level": "low",
            "temperature": 0.7 if power_level == "manh" else 0.5,
            "max_tokens": 2048 if power_level == "manh" else 1024,
            "top_p": 1.0
        }
        
        connected_apis.append({
            "key": key,
            "provider": provider,
            "name": custom_name,
            "power": power_level,
            "config": default_config
        })
        print(f"[+] Added successfully: [{custom_name}] | Provider: {provider} | Tier: {power_level.upper()}")
        
    return connected_apis

def call_ai_on_demand(ai_obj, prompt):
    provider = ai_obj["provider"]
    key = ai_obj["key"]
    name = ai_obj["name"]
    config = ai_obj["config"]
    
    print(f"\n[CALLING] AI [{name}] (Provider: {provider} | Tier: {ai_obj['power'].upper()}) is processing...")
    
    try:
        if provider == "Gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
            block_threshold = "BLOCK_NONE" if config['safety_level'].lower() == "low" else "BLOCK_MEDIUM_AND_ABOVE"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": float(config['temperature']),
                    "maxOutputTokens": int(config['max_tokens']),
                    "topP": float(config['top_p'])
                },
                "safetySettings": [
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": block_threshold},
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": block_threshold},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": block_threshold},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": block_threshold}
                ]
            }
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['candidates'][0]['content']['parts'][0]['text']
                
        elif provider in ["OpenAI", "Groq", "DeepSeek/Custom"]:
            url = "https://api.openai.com/v1/chat/completions"
            model_name = "gpt-4o-mini"
            if provider == "Groq":
                url = "https://api.groq.com/openai/v1/chat/completions"
                model_name = "llama3-70b-8192" if ai_obj['power'] == "manh" else "llama3-8b-8192"
            elif provider == "DeepSeek/Custom":
                url = "https://api.deepseek.com/chat/completions"
                model_name = "deepseek-chat"
                
            payload = {
                "model": model_name,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": float(config['temperature']),
                "max_tokens": int(config['max_tokens']),
                "top_p": float(config['top_p'])
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {key}'
                }
            )
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode('utf-8'))
                return res_data['choices'][0]['message']['content']
        else:
            return f"[Simulated Response] AI {name} responded successfully."
            
    except Exception as e:
        print(f"[-] Error calling [{name}]: {e}")
        return None

def execute_with_failover(apis, current_idx, prompt):
    attempts = 0
    total_apis = len(apis)
    
    while attempts < total_apis:
        active_ai = apis[current_idx]
        print(f"[*] Attempting AI [{active_ai['name']}] ({current_idx + 1}/{total_apis})...")
        
        res = call_ai_on_demand(active_ai, prompt)
        
        if res and res.strip():
            print(f"[OK] Success with AI [{active_ai['name']}]!")
            return res, current_idx
        else:
            print(f"[!] AI [{active_ai['name']}] failed/unresponsive. Switching to next...")
            current_idx = (current_idx + 1) % total_apis
            attempts += 1
            
    print("[-] All AI models in pool failed to respond.")
    return None, current_idx
      
