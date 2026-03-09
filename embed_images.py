#!/usr/bin/env python3
"""
embed_images.py — A2.2 Edition
================================
Lädt alle Pexels-Bilder aus den A2.2-HTML-Dateien herunter und:

  1. Speichert jedes Bild als .jpg im Cache-Ordner:
       A2.2/img/pexels-XXXXXXX.jpg      (permanenter Bild-Cache)

  2. Bettet die Bilder als Base64-Data-URLs direkt in die HTML-Dateien ein
       → vollständig offline-fähige HTML-Dateien

Verwendung:
  python3 embed_images.py                  # alle HTML-Dateien im Ordner
  python3 embed_images.py DE_A2_2011V*.html  # nur bestimmte Dateien

Benötigt: pip install requests
Der Bild-Cache wird nie zweimal heruntergeladen (Neustart sicher).
"""

import sys, re, os, base64, time, json
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR    = os.path.join(SCRIPT_DIR, 'img')   # Bild-Cache: echte .jpg Dateien
os.makedirs(IMG_DIR, exist_ok=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer':    'https://www.pexels.com/'
}

# ─── Bild herunterladen (zuerst aus Cache, dann von Pexels) ───────────────────

def get_image_b64(url: str) -> str:
    """Gibt Base64-Data-URL zurück. Nutzt img/-Cache wenn möglich."""
    # Cache-Dateiname: pexels-ID aus URL ableiten
    m = re.search(r'/photos/(\d+)/', url)
    cache_id = m.group(1) if m else re.sub(r'[^\w]', '_', url)[-40:]
    cache_path = os.path.join(IMG_DIR, f'pexels-{cache_id}.jpg')

    if os.path.exists(cache_path):
        with open(cache_path, 'rb') as f:
            data = f.read()
        print(f"    📦 Cache: pexels-{cache_id}.jpg ({len(data)//1024} KB)")
    else:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
        # Bild als .jpg im Cache speichern
        with open(cache_path, 'wb') as f:
            f.write(data)
        print(f"    ⬇️  Geladen: pexels-{cache_id}.jpg ({len(data)//1024} KB)")
        time.sleep(0.15)   # kleine Pause zwischen Downloads

    b64 = base64.b64encode(data).decode('ascii')
    return f"data:image/jpeg;base64,{b64}"


# ─── Haupt-Logik ─────────────────────────────────────────────────────────────

def process_file(filepath: str):
    print(f"\n{'='*60}")
    print(f"Verarbeite: {os.path.basename(filepath)}")
    print('='*60)

    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Alle eindeutigen Pexels-URLs finden
    pattern = r'(https://images\.pexels\.com/photos/[^\s"\'<>]+)'
    urls = list(dict.fromkeys(re.findall(pattern, html)))
    if not urls:
        print("  Keine Pexels-URLs gefunden — übersprungen.")
        return

    print(f"  {len(urls)} Bild-URL(s) gefunden.")

    # Backup
    backup = filepath.replace('.html', '.backup.html')
    if not os.path.exists(backup):
        with open(backup, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  💾 Backup: {os.path.basename(backup)}")

    # Bilder ersetzen
    changed = 0
    for url in urls:
        print(f"  → {url[-70:]}")
        try:
            data_url = get_image_b64(url)
            html = html.replace(url, data_url)
            changed += 1
        except Exception as e:
            print(f"    ✗ Fehler: {e}")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    size_kb = os.path.getsize(filepath) // 1024
    print(f"\n  ✅ {changed}/{len(urls)} Bilder eingebettet — {os.path.basename(filepath)} ({size_kb} KB)")


def main():
    if len(sys.argv) >= 2:
        files = sys.argv[1:]
    else:
        files = sorted([
            os.path.join(SCRIPT_DIR, f)
            for f in os.listdir(SCRIPT_DIR)
            if f.endswith('.html') and not f.endswith('.backup.html')
            and f.startswith('DE_A2_2')
        ])

    if not files:
        print("Keine HTML-Dateien gefunden.")
        sys.exit(1)

    print(f"A2.2 embed_images.py — {len(files)} Datei(en)")
    print(f"Bild-Cache: {IMG_DIR}")
    print(f"Bereits im Cache: {len([f for f in os.listdir(IMG_DIR) if f.endswith('.jpg')])} Bilder\n")

    for fp in files:
        process_file(fp)

    cache_count = len([f for f in os.listdir(IMG_DIR) if f.endswith('.jpg')])
    print(f"\n{'='*60}")
    print(f"FERTIG! Bild-Cache enthält jetzt {cache_count} Bilder in: img/")
    print(f"Die .jpg-Dateien können auch direkt als src=\"img/pexels-ID.jpg\" genutzt werden.")
    print(f"\nNächster Schritt:")
    print(f"  cd htmlS/A2.2 && git add *.html && git commit -m 'Bilder als Base64 eingebettet'")


if __name__ == '__main__':
    main()
