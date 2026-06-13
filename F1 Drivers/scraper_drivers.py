import os
import json
import requests

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Drivers"
DRIVERS_FOLDER = os.path.join(BASE_DIR, "drivers")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "drivers_link.json")
OUTPUT_JSON_PATH = os.path.join(BASE_DIR, "drivers.json")

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
    """Modifies the F1 CDN URL to auto-crop the face into a 400x400 square."""
    if "c_fill" in url:
        # Zamjenjuje standardni c_fill,w_720 s face-detection cropom
        return url.replace("c_fill,w_720", "c_fill,g_face,w_400,h_400")
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

    processed_drivers_json = {}

    print(f"\n[PIPELINE] Processing {len(raw_links)} driver portraits...")
    for driver_key, original_url in raw_links.items():
        # 1. Kroji URL na razini servera pomoću g_face parametra
        cropped_url = crop_url_for_icon(original_url)
        
        filename = f"{driver_key}.webp"
        full_dest_path = os.path.join(DRIVERS_FOLDER, filename)
        
        print(f"[PROCESSING] Cropping & Downloading: {driver_key} -> {filename}")
        
        # 2. Skini skrojenu sliku lokalno na laptop
        success = download_binary_file(cropped_url, full_dest_path)
        
        if success:
            # 3. Dodaj u mapu za novi drivers.json
            processed_drivers_json[driver_key] = cropped_url

    # Spremi novi json s uređenim linkovima u /F1 Drivers/drivers.json
    try:
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump({"driver_headshots": processed_drivers_json}, f, indent=4, ensure_ascii=False)
        print(f"\n[SUCCESS] Generated local index at: {OUTPUT_JSON_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to save output JSON: {e}")

if __name__ == "__main__":
    print("==========================================")
    print("F1 DRIVER ICON FACE-CROP PIPELINE v1")
    print("==========================================")
    run_driver_pipeline()
    print("==========================================")
