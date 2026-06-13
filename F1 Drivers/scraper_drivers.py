import os
import json
import requests

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
BASE_DIR = "F1 Drivers"
DRIVERS_FOLDER = os.path.join(BASE_DIR, "drivers")
DRIVERS_JSON_PATH = os.path.join(BASE_DIR, "drivers.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Izvorne sirove slike koje si poslao
RAW_DRIVER_LINKS = {
    "george_russell": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/mercedes/georus01/2026mercedesgeorus01right.webp",
    "kimi_antonelli": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/mercedes/andant01/2026mercedesandant01right.webp",
    "charles_leclerc": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/ferrari/chalec01/2026ferrarichalec01right.webp",
    "lewis_hamilton": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/ferrari/lewham01/2026ferrarilewham01right.webp",
    "lando_norris": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/mclaren/lannor01/2026mclarenlannor01right.webp",
    "oscar_piastri": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/mclaren/oscpia01/2026mclarenoscpia01right.webp",
    "max_verstappen": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/redbullracing/maxver01/2026redbullracingmaxver01right.webp",
    "isack_hadjar": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/redbullracing/isahad01/2026redbullracingisahad01right.webp",
    "pierre_gasly": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/alpine/piegas01/2026alpinepiegas01right.webp",
    "franco_colapinto": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/alpine/fracol01/2026alpinefracol01right.webp",
    "liam_lawson": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/racingbulls/lialaw01/2026racingbullslialaw01right.webp",
    "arvid_lindblad": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/racingbulls/arvlin01/2026racingbullsarvlin01right.webp",
    "esteban_ocon": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/haas/estoco01/2026haasestoco01right.webp",
    "oliver_bearman": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/haas/olibea01/2026haasolibea01right.webp",
    "carlos_sainz": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/williams/carsai01/2026williamscarsai01right.webp",
    "alexander_albon": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/williams/alealb01/2026williamsalealb01right.webp",
    "nico_hulkenberg": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/audi/nichul01/2026audinichul01right.webp",
    "gabriel_bortoleto": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/audi/gabbor01/2026audigabbor01right.webp",
    "fernando_alonso": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/astonmartin/feralo01/2026astonmartinferalo01right.webp",
    "lance_stroll": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/astonmartin/lanstr01/2026astonmartinlanstr01right.webp",
    "sergio_perez": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/cadillac/serper01/2026cadillacserper01right.webp",
    "valtteri_bottas": "https://media.formula1.com/image/upload/c_fill,w_720/q_auto/v1740000001/common/f1/2026/cadillac/valbot01/2026cadillacvalbot01right.webp"
}

# ==========================================
# FILE UTILITIES
# ==========================================
def initialize_environment():
    """Initializes required folders for drivers."""
    os.makedirs(DRIVERS_FOLDER, exist_ok=True)
    print(f"[INFO] Created drivers directory at: {DRIVERS_FOLDER}")

def download_binary_file(url, destination_path):
    """Downloads a driver image and stores it locally."""
    try:
        response = requests.get(url, headers=HEADERS, stream=True, timeout=15)
        if response.status_code == 200:
            with open(destination_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"[SUCCESS] Downloaded headshot to: {destination_path}")
            return True
        print(f"[ERROR] Failed to download from {url} (Status: {response.status_code})")
    except Exception as e:
        print(f"[EXCEPTION] Error during download: {e}")
    return False

# ==========================================
# PIPELINE EXECUTION
# ==========================================
def run_driver_pipeline():
    """Main execution orchestrator for the driver headshot cropper & downloader."""
    initialize_environment()
    
    drivers_json_output = {"driver_headshots": {}}
    
    print(f"\n[CROP & DOWNLOAD] Processing {len(RAW_DRIVER_LINKS)} driver profiles...")
    for driver_name, raw_url in RAW_DRIVER_LINKS.items():
        # Modifikacija URL-a u letu: mijenjamo c_fill,w_720 u pametni face-crop omjer 400x400
        cropped_url = raw_url.replace("c_fill,w_720", "c_fill,g_face,w_400,h_400")
        
        filename = f"{driver_name}.webp"
        full_dest_path = os.path.join(DRIVERS_FOLDER, filename)
        
        print(f"[PROCESSING] Downloading cropped headshot for: {driver_name}")
        success = download_binary_file(cropped_url, full_dest_path)
        
        if success:
            # Zapisujemo modificirani krojeni link u lokalni JSON
            drivers_json_output["driver_headshots"][driver_name] = cropped_url

    # Spremanje konačnog drivers.json datoteke u /F1 Drivers/
    try:
        with open(DRIVERS_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(drivers_json_output, f, indent=4, ensure_ascii=False)
        print(f"\n[FINISHED] Config successfully written to: {DRIVERS_JSON_PATH}")
    except Exception as e:
        print(f"[ERROR] Failed to write JSON output: {e}")

if __name__ == "__main__":
    print("==========================================")
    print("F1 DRIVER HEADSHOT PIPELINE v1.0")
    print("==========================================")
    run_driver_pipeline()
    print("==========================================")
