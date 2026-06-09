import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Circuits"
CIRCUITS_FOLDER = os.path.join(BASE_DIR, "circuits")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "circuits_link.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# JSON & FILE UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders."""
    if not os.path.exists(CIRCUITS_FOLDER):
        os.makedirs(CIRCUITS_FOLDER)
        print(f"[INFO] Created circuits directory at: {CIRCUITS_FOLDER}")

def load_json_config():
    """Loads the entire configuration from the JSON file."""
    if not os.path.exists(LINKS_JSON_PATH):
        # Ako file ne postoji, kreira se prazna šablona u koju dodaješ linkove
        default_data = {
            "direct_circuit_maps": {}
        }
        os.makedirs(BASE_DIR, exist_ok=True)
        with open(LINKS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=4, ensure_ascii=False)
        return default_data
    
    try:
        with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON configuration: {e}")
        return {"direct_circuit_maps": {}}

# ==========================================
# NETWORK & DOWNLOAD CORE
# ==========================================
def download_binary_file(url, destination_path):
    """Downloads an asset (image/track map) and stores it locally."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[SUCCESS] Downloaded asset to: {destination_path}")
            return True
        print(f"[ERROR] Failed to download asset from {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error during asset download: {e}")
    return False

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_circuit_scraper_pipeline():
    """Main execution orchestrator for the circuit scraper."""
    initialize_environment()
    config = load_json_config()
    
    direct_maps = config.get("direct_circuit_maps", {})
    
    if not direct_maps:
        print(f"[FINISHED] No direct maps configured in {LINKS_JSON_PATH}. Add links there first!")
        return

    print(f"\n[DOWNLOAD] Starting download of {len(direct_maps)} layouts from JSON...")
    for circuit_name, image_url in direct_maps.items():
        # Automatsko prepoznavanje ekstenzije iz samog linka (.webp, .png, .jpg)
        ext = "png"
        if "webp" in image_url.lower():
            ext = "webp"
        elif "jpg" in image_url.lower() or "jpeg" in image_url.lower():
            ext = "jpg"
            
        filename = f"{circuit_name}.{ext}"
        full_dest_path = os.path.join(CIRCUITS_FOLDER, filename)
        
        print(f"[PROCESSING] Downloading: {circuit_name} -> {filename}")
        download_binary_file(image_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 CIRCUIT ASSET MANAGEMENT PIPELINE v3")
    print("==========================================")
    run_circuit_scraper_pipeline()
    print("==========================================")
