import urllib.request
import urllib.parse
import json
import os
import sys
import subprocess
import time

TEST_PORT = 8009
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(PROJECT_ROOT, "canciones")
COVERS_DIR = os.path.join(PROJECT_ROOT, "logos")
METADATA_FILE = os.path.join(PROJECT_ROOT, "songs_metadata.json")

def wait_for_server(max_wait=10):
    start = time.time()
    while time.time() - start < max_wait:
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/status", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False

def check_audio_duration_ffprobe(filepath):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filepath
    ]
    out = subprocess.check_output(cmd, text=True, errors="ignore").strip()
    return float(out)

def test_song_download(test_payload):
    print(f"\n=======================================================")
    print(f"[TEST] Probando descarga para: {test_payload['query']}")
    print(f"=======================================================")

    data = json.dumps(test_payload).encode('utf-8')
    req = urllib.request.Request(
        f"{BASE_URL}/api/download_song",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    with urllib.request.urlopen(req, timeout=40) as resp:
        assert resp.status == 200, f"Status code no es 200: {resp.status}"
        resp_data = json.loads(resp.read().decode('utf-8'))
        print(f"[TEST] Respuesta recibida: {resp_data}")

        # AC1: status is success
        assert resp_data.get("status") == "success", "status no es 'success'"
        filename = resp_data.get("file")
        assert filename, "No se retornó el nombre del archivo"
        dl_url = resp_data.get("download_url")
        assert dl_url, "No se retornó download_url"

        # AC2: File on disk >= 1.5 MB
        local_path = os.path.join(SONGS_DIR, filename)
        assert os.path.exists(local_path), f"El archivo no existe en el disco: {local_path}"
        file_size = os.path.getsize(local_path)
        size_mb = file_size / (1024 * 1024)
        print(f"[TEST] Archivo en disco: {filename}, tamaño: {size_mb:.2f} MB ({file_size} bytes)")
        assert file_size >= 1500000, f"Tamaño del archivo menor a 1.5 MB: {size_mb:.2f} MB"

        # AC3: ffprobe duration >= 120 seconds
        duration = check_audio_duration_ffprobe(local_path)
        print(f"[TEST] Duración verificada con ffprobe: {duration:.2f} segundos")
        assert duration >= 120.0, f"Duración menor a 120 segundos: {duration:.2f}s"

        # AC4: Downloadable and streamable via /api/audio/<filename>
        audio_url = f"{BASE_URL}{dl_url}"
        print(f"[TEST] Verificando stream directo GET {audio_url}")
        with urllib.request.urlopen(audio_url, timeout=10) as stream_resp:
            assert stream_resp.status == 200, f"Stream falló con status {stream_resp.status}"
            stream_chunk = stream_resp.read(4096)
            assert len(stream_chunk) == 4096, "No se pudieron leer bytes del stream"

        range_req = urllib.request.Request(audio_url, headers={"Range": "bytes=0-1023"})
        with urllib.request.urlopen(range_req, timeout=10) as range_resp:
            assert range_resp.status == 206, f"Range request falló con status {range_resp.status}"
            range_chunk = range_resp.read()
            assert len(range_chunk) == 1024, f"Bytes incorrectos en Range: {len(range_chunk)}"
        print("[TEST] Streaming directo y Range requests verificados con éxito.")

        # AC R3: Registration in songs_metadata.json
        with open(METADATA_FILE, 'r', encoding='utf-8') as mf:
            metadata = json.load(mf)
        assert filename in metadata, f"{filename} no está registrado en songs_metadata.json"
        meta_entry = metadata[filename]
        print(f"[TEST] Entrada en metadata: {meta_entry}")
        assert meta_entry.get("title") == test_payload["title"]
        assert meta_entry.get("artist") == test_payload["artist"]
        assert meta_entry.get("cover_url"), "cover_url no está presente en metadata"

        cover_file = meta_entry.get("cover_file")
        if cover_file and cover_file != "Fix_You.jpg":
            cover_path = os.path.join(COVERS_DIR, cover_file)
            assert os.path.exists(cover_path), f"Carátula no guardada en: {cover_path}"
            print(f"[TEST] Carátula verificada en disco: {cover_path}")

        print(f"[TEST] Canción '{test_payload['title']}' validada al 100%.")


def test_catalog_integrity():
    print("\n=======================================================")
    print("[TEST] Verificando integridad del catálogo (46 pistas) y carpeta canciones/...")
    print("=======================================================")
    catalog_path = os.path.join(PROJECT_ROOT, "user_playlist_catalog.json")
    with open(catalog_path, "r", encoding="utf-8") as cf:
        catalog = json.load(cf)

    seen_files = set()
    for idx, entry in enumerate(catalog):
        fname = entry.get("file")
        assert fname, f"Entrada {idx} sin archivo: {entry}"
        assert fname not in seen_files, f"Archivo duplicado en catálogo: {fname}"
        seen_files.add(fname)

        fpath = os.path.join(SONGS_DIR, fname)
        assert os.path.exists(fpath), f"Archivo faltante en disco: {fpath}"
        sz = os.path.getsize(fpath)
        dur = check_audio_duration_ffprobe(fpath)
        assert sz > 1500000, f"Tamaño inválido ({sz} bytes) en {fname}"
        assert dur > 120.0, f"Duración inválida ({dur}s) en {fname}"

    all_audio_files = [f for f in sorted(os.listdir(SONGS_DIR)) if f.endswith(".m4a") or f.endswith(".mp3")]
    for fname in all_audio_files:
        fpath = os.path.join(SONGS_DIR, fname)
        sz = os.path.getsize(fpath)
        dur = check_audio_duration_ffprobe(fpath)
        assert sz > 1500000, f"Tamaño inválido en canciones/{fname}: {sz} bytes"
        assert dur > 120.0, f"Duración inválida en canciones/{fname}: {dur}s"

    print(f"[TEST] 100% de las {len(catalog)} pistas del catálogo y {len(all_audio_files)} archivos en canciones/ tienen tamaño > 1.5 MB y duración > 120s.")


def test_wishlist_automation():
    print("\n=======================================================")
    print("[TEST] Probando automatización de Wishlist (/api/wishlist sync + async)...")
    print("=======================================================")
    wishlist_path = os.path.join(PROJECT_ROOT, "wishlist.json")
    if os.path.exists(wishlist_path):
        try:
            os.remove(wishlist_path)
        except Exception:
            pass

    # 1. Synchronous wait=True test + cover verification
    payload = {
        "wait": True,
        "songs": [
            {"title": "Excusa Perfecta", "artist": "Santi Muk"},
            {"title": "I Think They Call This Love", "artist": "Elliot James Reay"}
        ]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/api/wishlist",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        assert resp.status == 200
        res_json = json.loads(resp.read().decode("utf-8"))
        assert res_json.get("status") == "success"
        assert res_json.get("queued") == 2
        for item in res_json.get("items", []):
            assert item.get("status") == "completed", f"Wishlist item no completado: {item}"
            assert item.get("size_mb", 0) > 1.5
            assert item.get("duration_s", 0) > 120.0
            assert item.get("cover") and item.get("cover") != "logos/Fix_You.jpg", f"Carátula incorrecta en wishlist: {item}"

    # 2. Asynchronous background worker test (without wait=True) on an uncached song
    uncached_file = os.path.join(SONGS_DIR, "Yellow_Coldplay.m4a")
    if os.path.exists(uncached_file):
        os.remove(uncached_file)

    async_payload = {
        "songs": [
            {"title": "Yellow", "artist": "Coldplay"}
        ]
    }
    async_req = urllib.request.Request(
        f"{BASE_URL}/api/wishlist",
        data=json.dumps(async_payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(async_req, timeout=10) as a_resp:
        assert a_resp.status == 200
        a_json = json.loads(a_resp.read().decode("utf-8"))
        assert a_json.get("status") == "success"
        assert a_json.get("queued") == 1
        initial_state = a_json["items"][0].get("status")
        print(f"[TEST] Estado inicial async en POST /api/wishlist: {initial_state}")
        assert initial_state in ("pending", "downloading", "completed")

    # Poll GET /api/wishlist until background worker finishes downloading Yellow - Coldplay
    observed_states = {initial_state}
    completed_item = None
    deadline = time.time() + 45
    while time.time() < deadline:
        with urllib.request.urlopen(f"{BASE_URL}/api/wishlist", timeout=10) as get_resp:
            assert get_resp.status == 200
            get_json = json.loads(get_resp.read().decode("utf-8"))
            yellow_item = next((x for x in get_json.get("items", []) if x.get("id") == "yellow_coldplay"), None)
            assert yellow_item is not None, "yellow_coldplay no encontrado en GET /api/wishlist"
            st = yellow_item.get("status")
            observed_states.add(st)
            if st == "completed":
                completed_item = yellow_item
                break
            elif st == "error":
                raise AssertionError(f"Background worker falló en yellow_coldplay: {yellow_item}")
        time.sleep(0.4)

    assert completed_item is not None, f"Timeout esperando a que yellow_coldplay complete. Estados: {observed_states}"
    assert completed_item.get("size_mb", 0) > 1.5
    assert completed_item.get("duration_s", 0) > 120.0
    print(f"[TEST] Transición de estados async observada: {observed_states} -> {completed_item['file']} ({completed_item['size_mb']} MB, {completed_item['duration_s']}s)")
    if os.path.exists(uncached_file):
        try:
            os.remove(uncached_file)
        except Exception:
            pass
    with open(METADATA_FILE, "r", encoding="utf-8") as mf:
        m_data = json.load(mf)
    if "Yellow_Coldplay.m4a" in m_data:
        del m_data["Yellow_Coldplay.m4a"]
        with open(METADATA_FILE, "w", encoding="utf-8") as mf:
            json.dump(m_data, mf, ensure_ascii=False, indent=2)
    yellow_cover = os.path.join(COVERS_DIR, "Yellow_Coldplay_portada.jpg")
    if os.path.exists(yellow_cover):
        try:
            os.remove(yellow_cover)
        except Exception:
            pass
    # Keep wishlist.json clean with the 2 verified catalog tracks
    with open(wishlist_path, "r", encoding="utf-8") as wf:
        w_items = [x for x in json.load(wf) if x.get("id") != "yellow_coldplay"]
    with open(wishlist_path, "w", encoding="utf-8") as wf:
        json.dump(w_items, wf, ensure_ascii=False, indent=2)


def test_pwa_installability():
    print("\n=======================================================")
    print("[TEST] Verificando instalabilidad PWA para Chrome en Android...")
    print("=======================================================")
    with urllib.request.urlopen(f"{BASE_URL}/manifest.json", timeout=10) as r:
        assert r.status == 200
        ct = r.headers.get("Content-Type", "")
        assert "manifest+json" in ct or "application/json" in ct, f"Content-Type inesperado: {ct}"
        manifest = json.loads(r.read().decode("utf-8"))
        assert manifest.get("name") == "Cinnamoroll Music"
        assert manifest.get("display") == "standalone"
        assert manifest.get("start_url") == "/"
        icons = manifest.get("icons", [])
        assert len(icons) >= 4, "Faltan íconos PWA (192, 512, maskable)"

    for ic in icons:
        with urllib.request.urlopen(f"{BASE_URL}{ic['src']}", timeout=10) as r:
            assert r.status == 200
            data = r.read()
            assert len(data) > 5000, f"Ícono demasiado pequeño: {ic['src']}"

    with urllib.request.urlopen(f"{BASE_URL}/sw.js", timeout=10) as r:
        assert r.status == 200
        sw_ct = r.headers.get("Content-Type", "")
        assert "javascript" in sw_ct, f"SW Content-Type inesperado: {sw_ct}"
        sw_code = r.read().decode("utf-8")
        assert "addEventListener('fetch'" in sw_code or 'addEventListener("fetch"' in sw_code

    with urllib.request.urlopen(f"{BASE_URL}/", timeout=10) as r:
        assert r.status == 200
        html = r.read().decode("utf-8")
        assert '<link rel="manifest" href="/manifest.json">' in html
        assert "navigator.serviceWorker.register('/sw.js')" in html
        assert 'id="btn-install-pwa"' in html

    print("[TEST] PWA Manifest, Service Worker, íconos 192/512 y botón de instalación verificados al 100%.")


def run_all_tests():
    env = os.environ.copy()
    env["PORT"] = str(TEST_PORT)
    proc = subprocess.Popen([sys.executable, "server.py"], cwd=PROJECT_ROOT, env=env)

    test_cases = [
        {
            "query": "Dua Lipa Levitating",
            "title": "Levitating",
            "artist": "Dua Lipa"
        },
        {
            "query": "Coldplay Viva La Vida",
            "title": "Viva La Vida",
            "artist": "Coldplay"
        },
        {
            "query": "The Weeknd Blinding Lights",
            "title": "Blinding Lights",
            "artist": "The Weeknd"
        }
    ]

    try:
        print("[TEST] Iniciando servidor de prueba en puerto", TEST_PORT)
        assert wait_for_server(), "El servidor no respondió a tiempo."
        print("[TEST] Servidor activo. Ejecutando batería de pruebas...")

        test_pwa_installability()
        test_catalog_integrity()

        for tc in test_cases:
            test_song_download(tc)

        test_wishlist_automation()

        print("\n=======================================================")
        print("  ¡TODAS LAS PRUEBAS E2E PASARON CON ÉXITO ROTUNDO!   ")
        print("=======================================================\n")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == '__main__':
    run_all_tests()

