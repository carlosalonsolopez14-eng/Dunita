#!/usr/bin/env python3.11
"""Download building sprites from GitHub"""
import requests
import os

API_URL = "https://api.github.com/repos/carlosalonsolopez14-eng/Dunita/contents/Documentacion/imagenes_edificios"
OUT_DIR = "/home/ubuntu/dunita_game/assets/sprites/buildings"

os.makedirs(OUT_DIR, exist_ok=True)

resp = requests.get(API_URL)
files = resp.json()

for f in files:
    name = f['name']
    url = f['download_url']
    out_path = os.path.join(OUT_DIR, name)
    print(f"Downloading {name}...")
    r = requests.get(url)
    with open(out_path, 'wb') as fp:
        fp.write(r.content)
    print(f"  Saved: {out_path} ({len(r.content)} bytes)")

print(f"\nTotal: {len(files)} files downloaded")
