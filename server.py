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

        if path.startswith('/api/debug_dl'):
            parsed_qs = urllib.parse.parse_qs(parsed.query)
            q = parsed_qs.get('q', ['Coldplay Yellow'])[0]
            out_test = os.path.join(SONGS_DIR, "test_diag.%(ext)s")
            
            p_ff = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, errors='ignore')
            
            cmd_yt = [
                "yt-dlp",
                "--verbose",
                "--extractor-args", "youtube:player_client=android,tv_embedded",
                f"ytsearch1:{q} audio",
                "-x",
                "--audio-format", "m4a",
                "-o", out_test
            ]
            p_yt = subprocess.run(cmd_yt, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            cmd_sc = [
                "yt-dlp",
                "--verbose",
                f"scsearch1:{q}",
                "-x",
                "--audio-format", "m4a",
                "-o", out_test
            ]
            p_sc = subprocess.run(cmd_sc, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            self.send_json({
                "ffmpeg_ok": p_ff.returncode == 0,
                "ffmpeg_err": p_ff.stderr[:100] if p_ff.stderr else "",
                "yt_code": p_yt.returncode,
                "yt_err": p_yt.stderr[-400:],
                "yt_out": p_yt.stdout[-400:],
                "sc_code": p_sc.returncode,
                "sc_err": p_sc.stderr[-400:],
                "sc_out": p_sc.stdout[-400:]
            })
            return

        if path == '/api/downloads':
            items = []
            if os.path.exists(SONGS_DIR):
                for f in sorted(os.listdir(SONGS_DIR)):
                    if f.endswith('.m4a') or f.endswith('.mp3'):
                        fp = os.path.join(SONGS_DIR, f)
                        size_mb = round(os.path.getsize(fp) / (1024 * 1024), 2)
                        raw_name = f[:-4]
                        clean_name = raw_name
                        if len(clean_name) > 3 and clean_name[:2].isdigit() and clean_name[2] == '_':
                            clean_name = clean_name[3:]
                        parts = clean_name.split('_')
                        if len(parts) >= 2:
                            artist = parts[-1].replace('-', ' ')
                            title = ' '.join(parts[:-1]).replace('-', ' ')
                        else:
                            title = clean_name.replace('_', ' ')
                            artist = 'Cinnamoroll Music'
                        
                        meta = {}
                        meta_path = os.path.join(BASE_DIR, 'songs_metadata.json')
                        if os.path.exists(meta_path):
                            try:
                                with open(meta_path, 'r', encoding='utf-8') as mf:
                                    meta = json.load(mf).get(f, {})
                            except Exception:
                                pass

                        cover_filename = f"{raw_name}.jpg"
                        has_local_cover = os.path.exists(os.path.join(COVERS_DIR, cover_filename))
                        cover_url = f"logos/{cover_filename}" if has_local_cover else meta.get('cover_url', 'logos/Fix_You.jpg')
                        fallback_url = meta.get('fallback_url', cover_url)

                        items.append({
                            "id": raw_name,
                            "file": f,
                            "title": meta.get('title', title),
                            "artist": meta.get('artist', artist),
                            "size": f"{size_mb} MB",
                            "cover": cover_url,
                            "fallback": fallback_url,
                            "download_url": f"/api/audio/{urllib.parse.quote(f)}",
                            "format": "m4a"
                        })
            self.send_json({"status": "success", "count": len(items), "songs": items})
            return


        if path.startswith('/api/audio/'):
            filename = urllib.parse.unquote(path[len('/api/audio/'):])
            filepath = os.path.join(SONGS_DIR, filename)
            if not os.path.exists(filepath):
                # Search case-insensitive or partial
                clean_target = filename.lower().replace('.m4a', '').replace('.mp3', '')
                for f in os.listdir(SONGS_DIR):
                    if f.lower() == filename.lower() or clean_target in f.lower() or f.lower().replace('.m4a', '') in clean_target:
                        filepath = os.path.join(SONGS_DIR, f)
                        filename = f
                        break

            if os.path.exists(filepath):
                filesize = os.path.getsize(filepath)
                range_header = self.headers.get('Range')
                if range_header:
                    m = re.match(r'bytes=(\d+)-(\d*)', range_header)
                    if m:
                        start = int(m.group(1))
                        end = int(m.group(2)) if m.group(2) else filesize - 1
                        length = end - start + 1
                        self.send_response(206)
                        self.send_header('Content-Type', 'audio/mp4')
                        self.send_header('Content-Range', f'bytes {start}-{end}/{filesize}')
                        self.send_header('Content-Length', str(length))
                        self.send_header('Accept-Ranges', 'bytes')
                        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        with open(filepath, 'rb') as f:
                            f.seek(start)
                            self.wfile.write(f.read(length))
                        return

                self.send_response(200)
                self.send_header('Content-Type', 'audio/mp4')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.send_header('Content-Length', str(filesize))
                self.send_header('Accept-Ranges', 'bytes')
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
                preview_url = params.get('preview_url', '')

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
                        if f.endswith('.m4a') and (safe_title.lower() in f.lower() or f.lower().find(safe_title.lower()[:8]) != -1):
                            found_existing = os.path.join(SONGS_DIR, f)
                            base_name = f[:-4]
                            break

                if not found_existing:
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

                    # Tier 1: YouTube Android/TV embedded clients (bypasses YouTube datacenter web bot challenge)
                    print(f"--> [Tier 1] Intentando descarga con YouTube Android/TV para '{query}'...")
                    out_template = os.path.join(SONGS_DIR, f"{base_name}.%(ext)s")
                    cmd1 = [
                        "yt-dlp",
                        "--no-warnings",
                        "--extractor-args", "youtube:player_client=android,tv_embedded",
                        f"ytsearch1:{query} audio",
                        "-x",
                        "--audio-format", "m4a",
                        "--audio-quality", "0",
                        "-o", out_template
                    ]
                    proc1 = subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='ignore')

                    if proc1.returncode == 0 and os.path.exists(target_m4a) and os.path.getsize(target_m4a) > 200000:
                        found_existing = target_m4a
                        print(f"--> [Tier 1] Éxito YouTube Android/TV: {target_m4a}")
                    else:
                        # Tier 2: SoundCloud search (unblocked on all cloud datacenters / Render)
                        print(f"--> [Tier 2] Probando SoundCloud para '{query}'...")
                        cmd2 = [
                            "yt-dlp",
                            "--no-warnings",
                            f"scsearch1:{query}",
                            "-x",
                            "--audio-format", "m4a",
                            "--audio-quality", "0",
                            "-o", out_template
                        ]
                        proc2 = subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='ignore')
                        if proc2.returncode == 0 and os.path.exists(target_m4a) and os.path.getsize(target_m4a) > 200000:
                            found_existing = target_m4a
                            print(f"--> [Tier 2] Éxito SoundCloud: {target_m4a}")
                        else:
                            # Tier 3: preview_url from request
                            if preview_url and preview_url.startswith('http'):
                                try:
                                    print(f"--> [Tier 3] Descargando desde stream provisto: {preview_url[:60]}")
                                    req = urllib.request.Request(preview_url, headers={'User-Agent': 'Mozilla/5.0'})
                                    with urllib.request.urlopen(req, timeout=15) as r, open(target_m4a, 'wb') as out_f:
                                        out_f.write(r.read())
                                    if os.path.exists(target_m4a) and os.path.getsize(target_m4a) > 0:
                                        found_existing = target_m4a
                                except Exception as e:
                                    print(f"--> Error stream provisto: {e}")

                            # Tier 4: search iTunes catalog for audio stream
                            if not found_existing:
                                try:
                                    print(f"--> [Tier 4] Buscando en catálogo iTunes para '{query}'...")
                                    itunes_url = f"https://itunes.apple.com/search?term={urllib.parse.quote(query)}&entity=song&limit=1"
                                    req = urllib.request.Request(itunes_url, headers={'User-Agent': 'Mozilla/5.0'})
                                    with urllib.request.urlopen(req, timeout=10) as r:
                                        it_data = json.loads(r.read().decode())
                                        if it_data.get('results') and it_data['results'][0].get('previewUrl'):
                                            stream_url = it_data['results'][0]['previewUrl']
                                            req_stream = urllib.request.Request(stream_url, headers={'User-Agent': 'Mozilla/5.0'})
                                            with urllib.request.urlopen(req_stream, timeout=15) as sr, open(target_m4a, 'wb') as out_f:
                                                out_f.write(sr.read())
                                            if os.path.exists(target_m4a) and os.path.getsize(target_m4a) > 0:
                                                found_existing = target_m4a
                                except Exception as e:
                                    print(f"--> Error fallback iTunes: {e}")

                if found_existing:
                    size_mb = round(os.path.getsize(found_existing) / (1024*1024), 2)
                    print(f"--> Archivo listo: {found_existing} ({size_mb} MB)")
                    
                    # Persist metadata for new downloads so they show up in /api/downloads
                    meta_path = os.path.join(BASE_DIR, 'songs_metadata.json')
                    try:
                        m_data = {}
                        if os.path.exists(meta_path):
                            with open(meta_path, 'r', encoding='utf-8') as mf:
                                m_data = json.load(mf)
                        m_data[os.path.basename(found_existing)] = {
                            "title": title,
                            "artist": artist,
                            "album": "Descargado",
                            "cover_url": f"logos/{base_name}_portada.jpg" if cover_url else "logos/Fix_You.jpg",
                            "fallback_url": cover_url or "logos/Fix_You.jpg"
                        }
                        with open(meta_path, 'w', encoding='utf-8') as mf:
                            json.dump(m_data, mf, ensure_ascii=False, indent=2)
                    except Exception:
                        pass

                    self.send_json({
                        "status": "success",
                        "file": os.path.basename(found_existing),
                        "download_url": f"/api/audio/{urllib.parse.quote(os.path.basename(found_existing))}",
                        "size_mb": size_mb
                    })
                    return
                else:
                    self.send_json({"status": "error", "message": "No se pudo obtener el archivo de audio"}, status=404)
                    return

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
