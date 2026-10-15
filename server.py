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
import base64
import warnings
import threading
import time
import unicodedata

warnings.filterwarnings("ignore", message=".*TripleDES.*")

PORT = int(os.environ.get("PORT", 8000))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SONGS_DIR = os.path.join(BASE_DIR, "canciones")
COVERS_DIR = os.path.join(BASE_DIR, "logos")
CATALOG_FILE = os.path.join(BASE_DIR, "user_playlist_catalog.json")
WISHLIST_FILE = os.path.join(BASE_DIR, "wishlist.json")
METADATA_FILE = os.path.join(BASE_DIR, "songs_metadata.json")

FILE_LOCK = threading.Lock()
WISHLIST_WORKER_LOCK = threading.Lock()
WORKER_EVENT = threading.Event()
HEALER_STATUS = {
    "state": "idle",
    "checked": 0,
    "valid": 0,
    "healed": 0,
    "last_run": None
}

os.makedirs(SONGS_DIR, exist_ok=True)
os.makedirs(COVERS_DIR, exist_ok=True)

def strip_accents(text):
    if not text:
        return ""
    return "".join(c for c in unicodedata.normalize("NFD", str(text)) if unicodedata.category(c) != "Mn")

def clean_track_title(title):
    if not title:
        return ""
    return re.sub(r'\s*\((?:feat\.?|ft\.?|with)\s+[^)]+\)', '', title, flags=re.IGNORECASE).strip()

def sanitize_filename(name):
    clean = re.sub(r'[^\w\s\-áéíóúÁÉÍÓÚñÑ]', '', name).strip()
    return re.sub(r'\s+', '_', clean)

def get_audio_duration(file_path):
    """Retrieve audio duration in seconds using ffprobe or ffmpeg fallback."""
    if not file_path or not os.path.exists(file_path):
        return 0.0
    try:
        cmd = [
            'ffprobe', '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            file_path
        ]
        out = subprocess.check_output(cmd, text=True, errors='ignore').strip()
        dur = float(out)
        if dur > 0:
            return dur
    except Exception:
        pass

    try:
        cmd = ['ffmpeg', '-i', file_path]
        res = subprocess.run(cmd, capture_output=True, text=True, errors='ignore')
        m = re.search(r'Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)', res.stderr)
        if m:
            h, mins, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
            return h * 3600 + mins * 60 + s
    except Exception:
        pass

    return 0.0

def is_valid_full_song(file_path):
    """Strict verification gate: size > 1.5 MB and duration > 120 seconds."""
    if not file_path or not os.path.exists(file_path):
        return False
    try:
        sz = os.path.getsize(file_path)
        if sz <= 1500000:
            return False
    except OSError:
        return False
    dur = get_audio_duration(file_path)
    if dur <= 120.0:
        return False
    return True

def decrypt_saavn_url(enc_b64):
    """Decrypt JioSaavn TripleDES-ECB media URLs and strip PKCS padding."""
    try:
        from cryptography.hazmat.primitives.ciphers import Cipher, modes
        try:
            from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES
        except ImportError:
            from cryptography.hazmat.primitives.ciphers.algorithms import TripleDES
        from cryptography.hazmat.backends import default_backend

        key = b'38346591'
        enc = base64.b64decode(enc_b64)
        cipher = Cipher(TripleDES(key * 3), modes.ECB(), backend=default_backend())
        dec = cipher.decryptor().update(enc)
        pad_len = dec[-1]
        if 1 <= pad_len <= 8:
            dec = dec[:-pad_len]
        url_str = dec.decode('utf-8', errors='ignore').strip()
        cleaned_url = re.sub(r'[\x00-\x1f]', '', url_str)
        if cleaned_url.startswith('http'):
            return cleaned_url
        return None
    except Exception as e:
        print(f"Error descifrando Saavn URL: {e}")
        return None

def resolve_via_cloud_cdn(query, title, artist, target_m4a):
    """
    Autonomous cloud-resilient resolver using direct CDN media streams.
    Bypasses YouTube datacenter bot detection on Render.
    """
    candidates = []
    raw_candidates = []
    c_title = clean_track_title(title)
    if title and artist and title != 'cancion' and artist != 'artista':
        raw_candidates.extend([f"{title} {artist}", f"{c_title} {artist}", f"{artist} {c_title}", c_title, title])
    if query:
        raw_candidates.append(query)
    if not raw_candidates:
        raw_candidates = [query or f"{title} {artist}"]

    for rc in raw_candidates:
        rc = rc.strip()
        if rc and rc not in candidates:
            candidates.append(rc)
        unacc = strip_accents(rc)
        if unacc and unacc not in candidates:
            candidates.append(unacc)

    print(f"--> [Tier 1: Cloud CDN Resolver] Buscando pistas para: {candidates[:6]}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'X-Forwarded-For': '49.36.128.1',
        'CF-IPCountry': 'IN'
    }

    for term in candidates:
        api_url = f"https://www.jiosaavn.com/api.php?__call=search.getResults&q={urllib.parse.quote(term)}&_format=json&_marker=0&api_version=4&ctx=web6dot0&p=1&n=10"
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode('utf-8', errors='ignore'))
                results = data.get('results', [])
                if not results:
                    continue

                def score_item(item):
                    item_title = strip_accents((item.get('title') or '').lower())
                    subtitle = strip_accents((item.get('subtitle') or '').lower())
                    more_info = item.get('more_info') or {}
                    album = strip_accents((more_info.get('album') or '').lower())
                    pts = 0
                    for bad_word in ['karaoke', 'instrumental', 'originally', 'tribute', '8-bit', 'lullaby', 'ringtone', 'nightcore']:
                        if bad_word in item_title or bad_word in subtitle or bad_word in album:
                            pts -= 25
                    if 'live' in item_title or 'live' in subtitle or 'live' in album:
                        pts -= 6
                    if title and title.lower() != 'cancion':
                        t_low = strip_accents(c_title.lower())
                        if item_title == t_low:
                            pts += 25
                        elif t_low and t_low in item_title:
                            pts += 12
                    if artist and artist.lower() != 'artista':
                        a_low = strip_accents(artist.lower().split('&')[0].split(',')[0].strip())
                        singers = strip_accents((more_info.get('singers') or '').lower())
                        music = strip_accents((more_info.get('music') or '').lower())
                        artist_map = more_info.get('artistMap') or {}
                        prim_names = strip_accents(" ".join((a.get('name') or '').lower() for a in artist_map.get('primary_artists', [])))
                        if a_low and (a_low in subtitle or a_low in prim_names):
                            pts += 30
                        elif a_low and (a_low in singers or a_low in music):
                            pts += 15
                    return pts

                results = sorted(results, key=score_item, reverse=True)

                for item in results:
                    if score_item(item) < 0:
                        continue
                    enc = item.get('more_info', {}).get('encrypted_media_url')
                    if not enc:
                        continue
                    dec = decrypt_saavn_url(enc)
                    if not dec:
                        continue

                    bitrate_variants = [
                        dec.replace('_96.mp4', '_320.mp4').replace('_160.mp4', '_320.mp4'),
                        dec.replace('_96.mp4', '_160.mp4'),
                        dec
                    ]

                    for stream_url in bitrate_variants:
                        temp_file = target_m4a + ".tmp"
                        try:
                            dl_req = urllib.request.Request(stream_url, headers=headers)
                            with urllib.request.urlopen(dl_req, timeout=20) as s_resp, open(temp_file, 'wb') as tf:
                                while True:
                                    chunk = s_resp.read(65536)
                                    if not chunk:
                                        break
                                    tf.write(chunk)

                            if is_valid_full_song(temp_file):
                                if os.path.exists(target_m4a):
                                    try: os.remove(target_m4a)
                                    except: pass
                                os.rename(temp_file, target_m4a)
                                art_url = item.get('image', '')
                                if art_url:
                                    art_url = art_url.replace('150x150', '500x500')
                                return target_m4a, art_url
                            else:
                                if os.path.exists(temp_file):
                                    try: os.remove(temp_file)
                                    except: pass
                        except Exception:
                            if os.path.exists(temp_file):
                                try: os.remove(temp_file)
                                except: pass
        except Exception as e:
            print(f"--> [Tier 1] Error en búsqueda '{term}': {e}")
            continue

    return None, None


def download_or_resolve_song(title="", artist="", query="", cover_url="", preview_url="", target_filename=None):
    """
    Core autonomous resolution engine: resolves a full-length (>1.5 MB, >120s) .m4a track,
    downloads official cover artwork, and persists metadata in songs_metadata.json.
    """
    title = (title or "").strip()
    artist = (artist or "").strip()
    query = (query or "").strip()
    cover_url = (cover_url or "").strip()

    if not query and title:
        query = f"{title} {artist}".strip()
    elif query and (not title or title == 'cancion'):
        if ' - ' in query:
            parts = query.split(' - ', 1)
            artist = parts[0].strip()
            title = parts[1].strip()
        else:
            words = query.split()
            if len(words) >= 2:
                title = " ".join(words[:-1])
                artist = words[-1]
            else:
                title = query
                artist = "Cinnamoroll Music"

    if not title:
        title = "cancion"
    if not artist:
        artist = "artista"

    safe_title = sanitize_filename(title)
    safe_artist = sanitize_filename(artist)
    if target_filename:
        base_name = target_filename.rsplit('.', 1)[0]
        target_m4a = os.path.join(SONGS_DIR, target_filename)
    else:
        base_name = f"{safe_title}_{safe_artist}"
        target_m4a = os.path.join(SONGS_DIR, f"{base_name}.m4a")

    # Step 1: Check existing valid files (must be > 1.5MB and > 120s)
    found_existing = None
    if os.path.exists(target_m4a):
        if is_valid_full_song(target_m4a):
            found_existing = target_m4a
        else:
            try: os.remove(target_m4a)
            except Exception: pass

    if not found_existing and not target_filename:
        first_artist_token = strip_accents(safe_artist.lower().split('_')[0])
        for f in os.listdir(SONGS_DIR):
            if f.endswith('.m4a') or f.endswith('.mp3'):
                cand = os.path.join(SONGS_DIR, f)
                f_low = strip_accents(f.lower())
                t_low = strip_accents(safe_title.lower())
                if t_low and t_low in f_low and (not first_artist_token or first_artist_token in f_low):
                    if is_valid_full_song(cand):
                        found_existing = cand
                        base_name = f.rsplit('.', 1)[0]
                        break
                    else:
                        try: os.remove(cand)
                        except Exception: pass

    resolved_art = None

    # Step 2: Multi-tier external resolution
    if not found_existing:
        print(f"--> [Tier 1: Cloud CDN] Resolviendo pista para '{query}' ({title} - {artist})...")
        try:
            cdn_file, art_from_cdn = resolve_via_cloud_cdn(query, title, artist, target_m4a)
            if cdn_file and is_valid_full_song(cdn_file):
                found_existing = cdn_file
                resolved_art = art_from_cdn
                print(f"--> [Tier 1: Cloud CDN] ¡Éxito! Canción descargada y verificada: {found_existing}")
        except Exception as e:
            print(f"--> [Tier 1: Cloud CDN] Error: {e}")

    def find_valid_downloaded_file(base):
        for ext in ['.m4a', '.mp3', '.opus', '.webm', '.ogg']:
            cand = os.path.join(SONGS_DIR, f"{base}{ext}")
            if is_valid_full_song(cand):
                return cand
            elif os.path.exists(cand):
                try: os.remove(cand)
                except: pass
        for f in os.listdir(SONGS_DIR):
            if f.startswith(base):
                cand = os.path.join(SONGS_DIR, f)
                if is_valid_full_song(cand):
                    return cand
                elif os.path.exists(cand):
                    try: os.remove(cand)
                    except: pass
        return None

    out_template = os.path.join(SONGS_DIR, f"{base_name}.%(ext)s")
    cookies_path = os.path.join(BASE_DIR, "cookies.txt")

    # --- TIER 2: YouTube with JS runtime (Node.js / Deno) ---
    if not found_existing:
        print(f"--> [Tier 2] Intentando YouTube con JS runtime para '{query}'...")
        cmd1 = [
            "yt-dlp", "--no-warnings", "--js-runtimes", "node,deno",
            "--match-filter", "duration > 120"
        ]
        if os.path.exists(cookies_path):
            cmd1 += ["--cookies", cookies_path]
        cmd1 += [
            f"ytsearch1:{query} audio",
            "-x",
            "--audio-format", "m4a",
            "--audio-quality", "0",
            "-o", out_template
        ]
        subprocess.run(cmd1, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        found_existing = find_valid_downloaded_file(base_name)
        if found_existing:
            print(f"--> [Tier 2] Éxito YouTube con JS runtime: {found_existing}")

    # --- TIER 3: YouTube visionos/android client ---
    if not found_existing:
        print(f"--> [Tier 3] Probando YouTube visionos/android para '{query}'...")
        cmd2 = [
            "yt-dlp",
            "--no-warnings",
            "--js-runtimes", "node,deno",
            "--extractor-args", "youtube:player_client=visionos,android,tv_embedded",
            "--match-filter", "duration > 120"
        ]
        if os.path.exists(cookies_path):
            cmd2 += ["--cookies", cookies_path]
        cmd2 += [
            f"ytsearch1:{query}",
            "-x",
            "--audio-format", "m4a",
            "--audio-quality", "0",
            "-o", out_template
        ]
        subprocess.run(cmd2, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        found_existing = find_valid_downloaded_file(base_name)
        if found_existing:
            print(f"--> [Tier 3] Éxito YouTube visionos/android: {found_existing}")

    # --- TIER 4: SoundCloud fallback (strictly filtered > 120s) ---
    if not found_existing:
        print(f"--> [Tier 4] Probando SoundCloud fallback para '{query}'...")
        cmd3 = [
            "yt-dlp",
            "--no-warnings",
            "--match-filter", "duration > 120",
            "--max-downloads", "1",
            f"scsearch5:{query}",
            "-x",
            "--audio-format", "m4a",
            "--audio-quality", "0",
            "-o", out_template
        ]
        subprocess.run(cmd3, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        found_existing = find_valid_downloaded_file(base_name)
        if found_existing:
            print(f"--> [Tier 4] Éxito SoundCloud: {found_existing}")

    # Step 3: Strict Full-Length Verification Gate & Library Persistence
    if found_existing and is_valid_full_song(found_existing):
        size_mb = round(os.path.getsize(found_existing) / (1024 * 1024), 2)
        duration_s = round(get_audio_duration(found_existing), 1)
        print(f"--> Archivo verificado y listo: {found_existing} ({size_mb} MB, {duration_s}s)")

        existing_meta = {}
        with FILE_LOCK:
            if os.path.exists(METADATA_FILE):
                try:
                    with open(METADATA_FILE, 'r', encoding='utf-8') as mf:
                        existing_meta = json.load(mf).get(os.path.basename(found_existing), {})
                except Exception:
                    existing_meta = {}

        local_cover_filename = None
        for cand_name in [f"{base_name}_portada.jpg", f"{base_name}.jpg", existing_meta.get("cover_file")]:
            if cand_name and cand_name != "Fix_You.jpg":
                cand_path = os.path.join(COVERS_DIR, cand_name)
                if os.path.exists(cand_path) and os.path.getsize(cand_path) > 100:
                    local_cover_filename = cand_name
                    break

        if not local_cover_filename and existing_meta.get("cover_url", "").startswith("logos/"):
            rel_name = existing_meta["cover_url"][len("logos/"):]
            if rel_name != "Fix_You.jpg" and os.path.exists(os.path.join(COVERS_DIR, rel_name)):
                local_cover_filename = rel_name

        artwork_to_fetch = None
        if not local_cover_filename:
            target_cover_filename = f"{base_name}_portada.jpg"
            local_cover_path = os.path.join(COVERS_DIR, target_cover_filename)
            for art_cand in [cover_url, resolved_art, existing_meta.get("fallback_url")]:
                if not art_cand or not art_cand.startswith('http'):
                    continue
                try:
                    req = urllib.request.Request(art_cand, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as r, open(local_cover_path, 'wb') as cf:
                        cf.write(r.read())
                    if os.path.exists(local_cover_path) and os.path.getsize(local_cover_path) > 100:
                        local_cover_filename = target_cover_filename
                        artwork_to_fetch = art_cand
                        break
                except Exception:
                    if os.path.exists(local_cover_path):
                        try: os.remove(local_cover_path)
                        except: pass
        else:
            artwork_to_fetch = cover_url if (cover_url and cover_url.startswith('http')) else (resolved_art or existing_meta.get("fallback_url"))

        if local_cover_filename:
            cover_rel_url = f"logos/{local_cover_filename}"
        elif cover_url and cover_url.startswith('logos/'):
            cover_rel_url = cover_url
        else:
            cover_rel_url = artwork_to_fetch or "logos/Fix_You.jpg"

        with FILE_LOCK:
            try:
                m_data = {}
                if os.path.exists(METADATA_FILE):
                    with open(METADATA_FILE, 'r', encoding='utf-8') as mf:
                        m_data = json.load(mf)
                existing_meta = m_data.get(os.path.basename(found_existing), {})
                m_data[os.path.basename(found_existing)] = {
                    "title": title,
                    "artist": artist,
                    "album": existing_meta.get("album", "Descargado"),
                    "duration": f"{int(duration_s // 60)}:{int(duration_s % 60):02d}",
                    "cover_file": local_cover_filename if local_cover_filename else existing_meta.get("cover_file", "Fix_You.jpg"),
                    "cover_url": cover_rel_url,
                    "fallback_url": artwork_to_fetch or existing_meta.get("fallback_url") or cover_rel_url
                }
                with open(METADATA_FILE, 'w', encoding='utf-8') as mf:
                    json.dump(m_data, mf, ensure_ascii=False, indent=2)
            except Exception as meta_e:
                print(f"Error persistiendo metadata: {meta_e}")

        return {
            "status": "success",
            "file": os.path.basename(found_existing),
            "download_url": f"/api/audio/{urllib.parse.quote(os.path.basename(found_existing))}",
            "size_mb": size_mb,
            "duration_s": duration_s,
            "title": title,
            "artist": artist,
            "cover": cover_rel_url
        }
    else:
        if found_existing and os.path.exists(found_existing):
            try: os.remove(found_existing)
            except Exception: pass
        return {
            "status": "error",
            "message": "No se pudo obtener el archivo de audio completo (> 1.5 MB, > 120s)"
        }


def load_wishlist():
    with FILE_LOCK:
        if not os.path.exists(WISHLIST_FILE):
            return []
        try:
            with open(WISHLIST_FILE, 'r', encoding='utf-8') as wf:
                data = json.load(wf)
                return data if isinstance(data, list) else []
        except Exception:
            return []


def save_wishlist(items):
    with FILE_LOCK:
        try:
            with open(WISHLIST_FILE, 'w', encoding='utf-8') as wf:
                json.dump(items, wf, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando wishlist: {e}")


def enqueue_wishlist_songs(raw_items, trigger_worker=True):
    """Normalize and atomically enqueue a list of song items into wishlist.json."""
    added = []
    with FILE_LOCK:
        items = []
        if os.path.exists(WISHLIST_FILE):
            try:
                with open(WISHLIST_FILE, 'r', encoding='utf-8') as wf:
                    data = json.load(wf)
                    if isinstance(data, list):
                        items = data
            except Exception:
                items = []

        for entry in raw_items:
            if isinstance(entry, str):
                q = entry.strip()
                if ' - ' in q:
                    artist, title = [p.strip() for p in q.split(' - ', 1)]
                else:
                    title, artist = q, "Artista"
                cover_url = ""
            elif isinstance(entry, dict):
                title = (entry.get('title') or '').strip()
                artist = (entry.get('artist') or '').strip()
                q = (entry.get('query') or f"{title} {artist}").strip()
                cover_url = (entry.get('cover_url') or entry.get('cover') or '').strip()
                if not title and q:
                    if ' - ' in q:
                        artist, title = [p.strip() for p in q.split(' - ', 1)]
                    else:
                        title = q
                        artist = artist or "Artista"
            else:
                continue

            if not title:
                continue

            item_id = sanitize_filename(f"{title}_{artist}").lower()
            existing = next((x for x in items if x.get("id") == item_id), None)
            if existing:
                existing_file = existing.get("file")
                existing_valid = bool(
                    existing.get("status") == "completed"
                    and existing_file
                    and is_valid_full_song(os.path.join(SONGS_DIR, existing_file))
                )
                if existing.get("status") == "error" or (existing.get("status") == "completed" and not existing_valid):
                    existing["status"] = "pending"
                added.append(existing)
                continue

            new_item = {
                "id": item_id,
                "title": title,
                "artist": artist,
                "query": q,
                "cover_url": cover_url,
                "status": "pending",
                "added_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            items.append(new_item)
            added.append(new_item)

        try:
            with open(WISHLIST_FILE, 'w', encoding='utf-8') as wf:
                json.dump(items, wf, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando wishlist: {e}")

    if trigger_worker:
        WORKER_EVENT.set()
    return added


def heal_catalog_once():
    """
    Autonomous startup catalog healer:
    Verifies every track in user_playlist_catalog.json has a dedicated, non-duplicate
    full-length (> 1.5 MB, > 120s) .m4a file in canciones/. Repairs any invalid or
    borrowed files automatically in the background.
    """
    HEALER_STATUS["state"] = "scanning"
    HEALER_STATUS["last_run"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if not os.path.exists(CATALOG_FILE):
        HEALER_STATUS["state"] = "completed"
        return

    try:
        with FILE_LOCK:
            with open(CATALOG_FILE, 'r', encoding='utf-8') as cf:
                catalog = json.load(cf)
    except Exception as e:
        print(f"--> [Auto-Healer] Error leyendo catálogo: {e}")
        HEALER_STATUS["state"] = "error"
        return

    seen_files = set()
    checked = 0
    valid = 0
    healed = 0
    catalog_modified = False

    for entry in catalog:
        checked += 1
        title = entry.get("title", "")
        artist = entry.get("artist", "")
        fname = entry.get("file", "")
        fpath = os.path.join(SONGS_DIR, fname) if fname else ""
        is_dup = bool(fname and fname in seen_files)

        if fname and not is_dup and is_valid_full_song(fpath):
            seen_files.add(fname)
            valid += 1
            continue

        # Track needs auto-healing
        print(f"--> [Auto-Healer] Reparando pista del catálogo: '{title}' - '{artist}' (file={fname}, dup={is_dup})")
        target_fname = fname if (fname and not is_dup) else f"{sanitize_filename(title)}_{sanitize_filename(artist)}.m4a"
        res = download_or_resolve_song(
            title=title,
            artist=artist,
            query=f"{title} {artist}",
            cover_url=entry.get("fallback") or entry.get("cover", ""),
            target_filename=target_fname
        )
        if res.get("status") == "success":
            new_file = res["file"]
            seen_files.add(new_file)
            entry["file"] = new_file
            entry["audioUrl"] = f"/api/audio/{new_file}"
            entry["size"] = f"{res['size_mb']} MB"
            catalog_modified = True
            healed += 1
            valid += 1
            print(f"--> [Auto-Healer] Pista reparada con éxito: {new_file} ({res['size_mb']} MB, {res['duration_s']}s)")

    if catalog_modified:
        with FILE_LOCK:
            try:
                with open(CATALOG_FILE, 'w', encoding='utf-8') as cf:
                    json.dump(catalog, cf, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"--> [Auto-Healer] Error guardando catálogo actualizado: {e}")

    HEALER_STATUS["checked"] = checked
    HEALER_STATUS["valid"] = valid
    HEALER_STATUS["healed"] = healed
    HEALER_STATUS["state"] = "completed"
    print(f"--> [Auto-Healer] Escaneo completado: {valid}/{checked} pistas válidas ({healed} reparadas).")


def process_pending_wishlist():
    """Process any pending items in wishlist.json and download full-length 320kbps .m4a files."""
    with WISHLIST_WORKER_LOCK:
        while True:
            items = load_wishlist()
            next_item = next((x for x in items if x.get("status") == "pending"), None)
            if not next_item:
                break

            item_id = next_item.get("id")
            for x in items:
                if x.get("id") == item_id:
                    x["status"] = "downloading"
            save_wishlist(items)

            res = download_or_resolve_song(
                title=next_item.get("title", ""),
                artist=next_item.get("artist", ""),
                query=next_item.get("query", ""),
                cover_url=next_item.get("cover_url", "")
            )

            items = load_wishlist()
            for x in items:
                if x.get("id") == item_id:
                    if res.get("status") == "success":
                        x["status"] = "completed"
                        x["file"] = res["file"]
                        x["download_url"] = res["download_url"]
                        x["size_mb"] = res["size_mb"]
                        x["duration_s"] = res["duration_s"]
                        x["cover"] = res.get("cover", "")
                        x["completed_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    else:
                        x["status"] = "error"
                        x["error"] = res.get("message", "No se pudo resolver audio completo")
            save_wishlist(items)


def background_worker_loop():
    """Daemon thread for autonomous catalog self-healing and wishlist pre-downloading."""
    try:
        heal_catalog_once()
    except Exception as e:
        print(f"--> [Background Worker] Error en auto-healer: {e}")

    while True:
        try:
            process_pending_wishlist()
        except Exception as e:
            print(f"--> [Background Worker] Error procesando wishlist: {e}")
        WORKER_EVENT.wait(timeout=15)
        WORKER_EVENT.clear()


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
        if path in ('/', '/index.html'):
            idx_path = os.path.join(BASE_DIR, 'index.html')
            if os.path.exists(idx_path):
                with open(idx_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        if path == '/manifest.json':
            manifest_path = os.path.join(BASE_DIR, 'manifest.json')
            if os.path.exists(manifest_path):
                with open(manifest_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/manifest+json; charset=utf-8')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        if path == '/sw.js':
            sw_path = os.path.join(BASE_DIR, 'sw.js')
            if os.path.exists(sw_path):
                with open(sw_path, 'rb') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                self.send_header('Service-Worker-Allowed', '/')
                self.send_header('Cache-Control', 'no-cache')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        if path == '/api/status':
            self.send_json({
                "status": "running",
                "songs_dir": SONGS_DIR,
                "covers_dir": COVERS_DIR,
                "healer": HEALER_STATUS,
                "wishlist_count": len(load_wishlist())
            })
            return

        if path == '/api/wishlist':
            items = load_wishlist()
            self.send_json({
                "status": "success",
                "count": len(items),
                "healer": HEALER_STATUS,
                "items": items
            })
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
                meta_dict = {}
                if os.path.exists(METADATA_FILE):
                    try:
                        with open(METADATA_FILE, 'r', encoding='utf-8') as mf:
                            meta_dict = json.load(mf)
                    except Exception:
                        pass

                for f in sorted(os.listdir(SONGS_DIR)):
                    if f.endswith('.m4a') or f.endswith('.mp3'):
                        fp = os.path.join(SONGS_DIR, f)
                        if os.path.getsize(fp) <= 1500000:
                            continue
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
                        
                        meta = meta_dict.get(f, {})
                        cover_url = 'logos/Fix_You.jpg'
                        for c_cand in [f"{raw_name}.jpg", f"{raw_name}_portada.jpg", meta.get('cover_file')]:
                            if c_cand and os.path.exists(os.path.join(COVERS_DIR, c_cand)):
                                cover_url = f"logos/{c_cand}"
                                break
                        if cover_url == 'logos/Fix_You.jpg' and meta.get('cover_url'):
                            cu = meta['cover_url']
                            if not cu.startswith('logos/') or os.path.exists(os.path.join(BASE_DIR, cu)):
                                cover_url = cu
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
                        self.send_header('Content-Disposition', f'inline; filename="{filename}"')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        try:
                            with open(filepath, 'rb') as f:
                                f.seek(start)
                                self.wfile.write(f.read(length))
                        except (ConnectionResetError, BrokenPipeError):
                            pass
                        return

                self.send_response(200)
                self.send_header('Content-Type', 'audio/mp4')
                self.send_header('Content-Disposition', f'inline; filename="{filename}"')
                self.send_header('Content-Length', str(filesize))
                self.send_header('Accept-Ranges', 'bytes')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                try:
                    with open(filepath, 'rb') as f:
                        self.copyfile(f, self.wfile)
                except (ConnectionResetError, BrokenPipeError):
                    pass
                return
            else:
                self.send_error(404, "File not found")
                return

        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == '/api/wishlist':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length).decode('utf-8', errors='ignore')
            try:
                payload = json.loads(raw_body) if raw_body.strip() else {}
                wait_sync = False
                if isinstance(payload, list):
                    raw_items = payload
                elif isinstance(payload, dict):
                    wait_sync = bool(payload.get('wait') or payload.get('sync'))
                    if 'songs' in payload and isinstance(payload['songs'], list):
                        raw_items = payload['songs']
                    elif 'items' in payload and isinstance(payload['items'], list):
                        raw_items = payload['items']
                    else:
                        raw_items = [payload]
                else:
                    raw_items = []

                added = enqueue_wishlist_songs(raw_items, trigger_worker=not wait_sync)
                if wait_sync:
                    process_pending_wishlist()
                    all_items = load_wishlist()
                    added_ids = {a.get("id") for a in added}
                    added = [x for x in all_items if x.get("id") in added_ids]

                self.send_json({
                    "status": "success",
                    "queued": len(added),
                    "items": added
                })
            except Exception as e:
                traceback.print_exc()
                self.send_json({"status": "error", "message": str(e)}, status=400)
            return

        if path == '/api/download_song':
            length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(length).decode('utf-8', errors='ignore')
            print(f"--> Solicitud de descarga recibida: {raw_body[:100]}")
            try:
                params = json.loads(raw_body)
                res = download_or_resolve_song(
                    title=params.get('title', ''),
                    artist=params.get('artist', ''),
                    query=params.get('query', ''),
                    cover_url=params.get('cover_url', ''),
                    preview_url=params.get('preview_url', '')
                )
                if res.get("status") == "success":
                    self.send_json(res)
                else:
                    self.send_json(res, status=404)
            except Exception as e:
                traceback.print_exc()
                self.send_json({"status": "error", "message": str(e)}, status=500)
            return

        self.send_error(404, "Endpoint not found")


class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True


def run_server():
    worker_thread = threading.Thread(target=background_worker_loop, daemon=True)
    worker_thread.start()
    server_address = ('', PORT)
    with ThreadedHTTPServer(server_address, MusicHandler) as httpd:
        print(f"Servidor iniciado en http://localhost:{PORT}")
        sys.stdout.flush()
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()

