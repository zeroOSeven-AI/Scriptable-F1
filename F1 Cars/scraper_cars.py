import os
import json
import requests

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Cars"
CARS_FOLDER = os.path.join(BASE_DIR, "cars")
LINKS_JSON_PATH = os.path.join(BASE_DIR, "cars_link.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ==========================================
# ENVIRONMENT & UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders."""
    os.makedirs(CARS_FOLDER, exist_ok=True)
    print(f"[INFO] Storage directory checked/created at: {CARS_FOLDER}")

def load_car_links():
    """Loads raw car links from JSON config."""
    if not os.path.exists(LINKS_JSON_PATH):
        print(f"[ERROR] Source file missing: {LINKS_JSON_PATH}")
        return {}
    
    try:
        with open(LINKS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("team_cars", data)
    except Exception as e:
        print(f"[ERROR] Failed to read JSON configuration: {e}")
        return {}

def scale_url_to_widget_size(url):
    """Optimizes the massive 3392px layout down to a crisp 1200px width for mobile screens."""
    if "c_lfill,w_3392" in url:
        return url.replace("c_lfill,w_3392", "c_lfill,w_1200")
    return url

def download_binary_file(url, destination_path):
    """Downloads the car image asset."""
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
def run_car_pipeline():
    """Main execution orchestrator for the car image pipeline."""
    initialize_environment()
    raw_links = load_car_links()
    
    if not raw_links:
        print(f"[FINISHED] No car links found to process.")
        return

    print(f"\n[PIPELINE] Processing {len(raw_links)} team cars (2026 Season Layout)...")
    for team_key, car_url in raw_links.items():
        # Optimiziraj širinu na 1200px
        optimized_url = scale_url_to_widget_size(car_url)
        
        filename = f"{team_key}.webp"
        full_dest_path = os.path.join(CARS_FOLDER, filename)
        
        print(f"[PROCESSING] Fetching 2026 Car: {team_key} -> {filename}")
        download_binary_file(optimized_url, full_dest_path)

if __name__ == "__main__":
    print("==========================================")
    print("F1 TEAM CAR 2026 PIPELINE v2")
    print("==========================================")
    run_car_pipeline()
    print("==========================================")
