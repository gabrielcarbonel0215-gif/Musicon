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

        for tc in test_cases:
            test_song_download(tc)

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
