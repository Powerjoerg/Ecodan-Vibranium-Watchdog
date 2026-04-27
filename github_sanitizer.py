import os
import shutil
import stat

ROOT_DIR = r"c:\Users\joerg\Desktop\REPRO  ECODAN BOOST\ecodan-pv-boost-v2-fixed\ecodan-pv-boost"
PACKAGES_DIR = os.path.join(ROOT_DIR, "packages")

# Das Ziel
TARGET_DIR = os.path.join(ROOT_DIR, "github_export")
TARGET_PACKAGES_DIR = os.path.join(TARGET_DIR, "packages")
TARGET_IMAGES_DIR = os.path.join(TARGET_DIR, "images")

# Die Ersetzungen
REPLACEMENTS = {
    "st1820_80b54e38809c": "thermostat_1",
    "st1820_b08184f2dbc8": "thermostat_2",
    "st1820_b08184f48e64": "thermostat_3",
    "st1820_b08184f67248": "thermostat_4",
    "st1820_b08184f4860c": "thermostat_5",
    "st1820_b08184f5c164": "thermostat_6",
    "myenergi_zappi_15553841": "zappi",
    "shellypro3em_e08cfe95cbe0": "shelly_wp"
}

def sanitize_file(source_path, target_path):
    with open(source_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    for old_val, new_val in REPLACEMENTS.items():
        content = content.replace(old_val, new_val)

    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(content)

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def main():
    print("\n🧹 1. Loesche alten Muell (behalte Git-Verbindung)...")
    if os.path.exists(TARGET_DIR):
        for item in os.listdir(TARGET_DIR):
            if item == ".git": 
                continue # Finger weg von Git!
            item_path = os.path.join(TARGET_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path, onerror=remove_readonly)
            else:
                os.remove(item_path)

    print("🏗️ 2. Baue korrekte GitHub Ordner-Struktur auf...")
    if not os.path.exists(TARGET_DIR):
        os.makedirs(TARGET_DIR)
    if not os.path.exists(TARGET_PACKAGES_DIR):
        os.makedirs(TARGET_PACKAGES_DIR)

    # --- ROOT DATEIEN ---
    print("📄 3. Kopiere & Bereinige Hauptdokumente (README etc.)...")
    md_files = ["README.md", "SYSTEM_DOKUMENTATION_PUBLIC.md", "NOTFALL_HANDBUCH.md", "LICENSE"]
    for md in md_files:
        src = os.path.join(ROOT_DIR, md)
        if os.path.exists(src):
            if md == "LICENSE":
                shutil.copy2(src, os.path.join(TARGET_DIR, md))
            else:
                sanitize_file(src, os.path.join(TARGET_DIR, md))

    # --- BILDER ---
    print("📸 4. Kopiere Bilder-Ordner...")
    src_images = os.path.join(ROOT_DIR, "images")
    if os.path.exists(src_images):
        shutil.copytree(src_images, TARGET_IMAGES_DIR)

    # --- PACKAGES (YAML) ---
    print("⚙️ 5. Bereinige YAML Code und lege ihn in den 'packages' Ordner...")
    for filename in os.listdir(PACKAGES_DIR):
        if filename.endswith(".yaml") or filename.endswith(".txt"):
            source_path = os.path.join(PACKAGES_DIR, filename)
            target_path = os.path.join(TARGET_PACKAGES_DIR, filename)
            sanitize_file(source_path, target_path)

    print("\n✅ FERTIG! Dein perfektes, strukturiertes Repo liegt jetzt in 'github_export'.")

if __name__ == "__main__":
    main()
