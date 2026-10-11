import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import os
import sys
import subprocess
import traceback
import re

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, "canciones")
COVERS_DIR = os.path.join(BASE_DIR, "logos")

os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

def sanitize_filename(name):
    clean = re.sub(r'[^\w\s\-áéíóúÁÉÍÓÚñÑ]', '', name).strip()
    return re.sub(r'\s+', '_', clean)

class MusicHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/status':
            self.send_json({"status": "running", "songs_dir": SONGS_DIR, "covers_dir": COVERS_DIR})
            return

        if path.startswith('/api/audio/'):
            filename = urllib.parse.unquote(path[len('/api/audio/'):])
            filepath = os.path.join(SONGS_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-Type', 'audio/mp4')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(os.path.getsize(filepath)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.copyfile(f, self.wfile)
                return
            else:
                self.send_error(404, "File not found")
                return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/download_song':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length).decode('utf-8', errors='ignore')
            print(f"--> Solicitud de descarga recibida: {raw_body[:100]}")
            try:
                params = json.loads(raw_body)
                title = params.get('title', 'cancion').strip()
                artist = params.get('artist', 'artista').strip()
                query = params.get('query', '').strip() or f"{title} {artist}"
                cover_url = params.get('cover_url', '')

                safe_title = sanitize_filename(title)
                safe_artist = sanitize_filename(artist)
                base_name = f"{safe_title}_{safe_artist}"
                target_m4a = os.path.join(SONGS_DIR, f"{base_name}.m4a")

                # Check if exact file or existing numbered file exists
                found_existing = None
                if os.path.exists(target_m4a):
                    found_existing = target_m4a
                else:
                    # check if a file with similar title exists in canciones/
                    for f in os.listdir(SONGS_DIR):
                        if f.endswith('.m4a') and safe_title.lower() in f.lower():
                            found_existing = os.path.join(SONGS_DIR, f)
                            base_name = f[:-4]
                            break

                if found_existing:
                    size_mb = round(os.path.getsize(found_existing) / (1024*1024), 2)
                    print(f"--> Canción ya existe: {found_existing} ({size_mb} MB)")
                    self.send_json({
                        "status": "success",
                        "already_exists": True,
                        "file": os.path.basename(found_existing),
                        "download_url": f"/api/audio/{urllib.parse.quote(os.path.basename(found_existing))}",
                        "size_mb": size_mb
                    })
                    return

                # Save cover
                if cover_url:
                    cover_target = os.path.join(COVERS_DIR, f"{base_name}_portada.jpg")
                    if not os.path.exists(cover_target):
                        try:
                            req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
                            with urllib.request.urlopen(req, timeout=10) as r, open(cover_target, 'wb') as cf:
                                cf.write(r.read())
                        except Exception:
                            pass

                # Download using yt-dlp
                print(f"--> Ejecutando yt-dlp para '{query}'...")
                out_template = os.path.join(SONGS_DIR, f"{base_name}.%(ext)s")
                cmd = [
                    "yt-dlp",
                    "--no-warnings",
                    f"ytsearch1:{query} audio",
                    "-x",
                    "--audio-format", "m4a",
                    "--audio-quality", "0",
                    "-o", out_template
                ]

                proc = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')

                if proc.returncode == 0 and os.path.exists(target_m4a):
                    size_mb = round(os.path.getsize(target_m4a) / (1024*1024), 2)
                    print(f"--> Descarga exitosa: {target_m4a} ({size_mb} MB)")
                    self.send_json({
                        "status": "success",
                        "file": f"{base_name}.m4a",
                        "download_url": f"/api/audio/{urllib.parse.quote(base_name)}.m4a",
                        "size_mb": size_mb
                    })
                else:
                    cmd2 = [
                        "yt-dlp",
                        "--no-warnings",
                        f"ytsearch1:{query}",
                        "-x",
                        "--audio-format", "m4a",
                        "-o", out_template
                    ]
                    proc2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                    if proc2.returncode == 0 and os.path.exists(target_m4a):
                        size_mb = round(os.path.getsize(target_m4a) / (1024*1024), 2)
                        print(f"--> Descarga exitosa (intento 2): {target_m4a} ({size_mb} MB)")
                        self.send_json({
                            "status": "success",
                            "file": f"{base_name}.m4a",
                            "download_url": f"/api/audio/{urllib.parse.quote(base_name)}.m4a",
                            "size_mb": size_mb
                        })
                    else:
                        err_msg = proc.stderr or proc2.stderr or "Error en descarga"
                        print(f"--> Error yt-dlp: {err_msg[:200]}")
                        self.send_json({"status": "error", "message": err_msg[:200]}, status=500)

            except Exception as e:
                traceback.print_exc()
                self.send_json({"status": "error", "message": str(e)}, status=500)
            return

        self.send_error(404, "Endpoint not found")

def run_server():
    server_address = ('', PORT)
    with socketserver.TCPServer(server_address, MusicHandler) as httpd:
        print(f"Servidor iniciado en http://localhost:{PORT}")
        sys.stdout.flush()
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
