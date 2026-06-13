import os
import json
import requests

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Drivers"
DRIVERS_FOLDER = os.path.join(BASE_DIR, "drivers")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "drivers_link.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# ENVIRONMENT & UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders."""
    os.makedirs(DRIVERS_FOLDER, exist_ok=True)
    print(f"[INFO] Storage directory checked/created at: {DRIVERS_FOLDER}")

def load_driver_links():
    """Loads raw driver links from JSON config."""
    if not os.path.exists(LINKS_JSON_PATH):
        print(f"[ERROR] Source file missing: {LINKS_JSON_PATH}")
        return {}
    
    try:
        with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Podržava ako je omotano u objekt ili ako je čisti rječnik
            return data.get("driver_headshots", data)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON configuration: {e}")
        return {}

def crop_url_for_icon(url):
    """Modifies the F1 CDN URL to auto-crop the face into a 600x600 square."""
    if "c_fill" in url:
        # Zamjenjuje standardni c_fill,w_720 s face-detection cropom u 600x600
        return url.replace("c_fill,w_720", "c_fill,g_face,w_600,h_600")
    return url

def download_binary_file(url, destination_path):
    """Downloads the cropped image asset."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return True
        print(f"[ERROR] Failed to download: {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error during download: {e}")
    return False

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_driver_pipeline():
    """Main execution orchestrator for the driver icon pipeline."""
    initialize_environment()
    raw_links = load_driver_links()
    
    if not raw_links:
        print(f"[FINISHED] No driver links found to process.")
        return

    print(f"\n[PIPELINE] Processing {len(raw_links)} driver portraits...")
    for driver_key, original_url in raw_links.items():
        # 1. Kroji URL na razini servera pomoću g_face parametra (600x600)
        cropped_url = crop_url_for_icon(original_url)
        
        filename = f"{driver_key}.webp"
        full_dest_path = os.path.join(DRIVERS_FOLDER, filename)
        
        print(f"[PROCESSING] Cropping & Downloading: {driver_key} -> {filename}")
        
        # 2. Skini skrojenu sliku lokalno na laptop
        download_binary_file(cropped_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 DRIVER ICON FACE-CROP PIPELINE v3")
    print("==========================================")
    run_driver_pipeline()
    print("==========================================")
