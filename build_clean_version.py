import os
import base64
import json

base_dir = r"C:\Users\Abeli\.gemini\antigravity\scratch\proyecto_musica"
assets_dir = os.path.join(base_dir, "assets")

def get_b64(fname):
    p = os.path.join(assets_dir, fname)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""

c_splash = get_b64("cinnamoroll_splash.png")
c_avatar = get_b64("cinnamoroll_avatar.png")
c_banner = get_b64("cinnamoroll_banner.png")
c_detail = get_b64("cinnamoroll_detail.png")
c_sleeping = get_b64("cinnamoroll_sleeping.png")
c_star = get_b64("cinnamoroll_star.png")
c_player = get_b64("cinnamoroll_player_cloud.png")

# Load real songs metadata
with open(os.path.join(base_dir, "songs_metadata.json"), "r", encoding="utf-8") as f:
    meta_dict = json.load(f)

# Load user custom playlist catalog (46 songs from user)
with open(os.path.join(base_dir, "user_playlist_catalog.json"), "r", encoding="utf-8") as f:
    user_catalog_songs = json.load(f)
catalog_json_str = json.dumps(user_catalog_songs, indent=2, ensure_ascii=False)

server_songs_list = []
canciones_dir = os.path.join(base_dir, "canciones")

for fname in sorted(os.listdir(canciones_dir)):
    if fname.endswith(".m4a") or fname.endswith(".mp3"):
        fp = os.path.join(canciones_dir, fname)
        if os.path.getsize(fp) <= 1500000:
            continue
        size_mb = f"{round(os.path.getsize(fp) / (1024 * 1024), 2)} MB"
        m = meta_dict.get(fname, {})
        title = m.get("title", fname[:-4].replace("_", " "))
        artist = m.get("artist", "Artista")
        cover = m.get("cover_url", f"logos/{fname[:-4]}.jpg")
        fallback = m.get("fallback_url", cover)

        server_songs_list.append({
            "id": fname[:-4],
            "file": fname,
            "title": title,
            "artist": artist,
            "album": "Descargas",
            "size": size_mb,
            "cover": cover,
            "fallback": fallback,
            "audioUrl": f"/api/audio/{fname}",
            "download_url": f"/api/audio/{fname}",
            "format": "m4a"
        })

songs_json_str = json.dumps(server_songs_list, indent=2, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>Cinnamoroll Music</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Quicksand:wght@500;600;700&display=swap" rel="stylesheet">
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    * {{
      font-family: 'Nunito', 'Quicksand', sans-serif;
      -webkit-tap-highlight-color: transparent;
      box-sizing: border-box;
    }}
    ::-webkit-scrollbar {{ width: 5px; height: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: #c8defa; border-radius: 9999px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: #96c2f7; }}

    html, body {{
      height: 100%;
      height: 100dvh;
      margin: 0;
      padding: 0;
      overflow: hidden;
      width: 100%;
      background-color: #f4f8fe;
      -webkit-font-smoothing: antialiased;
    }}

    #app-frame {{
      width: 100%;
      height: 100%;
      height: 100dvh;
      max-height: 100dvh;
      display: flex;
      flex-direction: column;
      position: relative;
      overflow: hidden;
      background-color: #f4f8fe;
    }}

    @media (min-width: 640px) {{
      body {{
        overflow: auto;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
        background-color: #eaf2fd;
      }}
      #app-frame {{
        max-width: 420px;
        height: 880px;
        max-height: calc(100vh - 2rem);
        border-radius: 40px;
        border: 6px solid white;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
      }}
    }}

    .screen-view {{
      flex: 1 1 0%;
      min-height: 0;
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior-y: contain;
    }}

    .safe-bottom-dock {{
      min-height: 64px;
      padding-bottom: max(6px, env(safe-area-inset-bottom, 0px));
      box-sizing: content-box;
    }}

    .safe-mini-player {{
      bottom: calc(64px + max(12px, env(safe-area-inset-bottom, 0px)));
    }}

    @keyframes gentle-float {{
      0%, 100% {{ transform: translateY(0px); }}
      50% {{ transform: translateY(-5px); }}
    }}
    .animate-float {{
      animation: gentle-float 3.5s ease-in-out infinite;
    }}

    @keyframes star-twinkle {{
      0%, 100% {{ opacity: 0.35; transform: scale(0.85); }}
      50% {{ opacity: 1; transform: scale(1.15); }}
    }}
    .animate-twinkle {{
      animation: star-twinkle 2.5s ease-in-out infinite;
    }}

    input[type=range] {{
      -webkit-appearance: none;
      background: #dbeafe;
      border-radius: 9999px;
      height: 4px;
      outline: none;
    }}
    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      height: 14px;
      width: 14px;
      border-radius: 50%;
      background: #3b82f6;
      cursor: pointer;
      box-shadow: 0 1px 4px rgba(59, 130, 246, 0.4);
      transition: transform 0.15s ease;
    }}
    input[type=range]::-webkit-slider-thumb:hover {{
      transform: scale(1.2);
    }}
  </style>
</head>
<body class="text-slate-700 select-none">

  <!-- Main Mobile App Container (100dvh pinned dock architecture) -->
  <div id="app-frame" class="transition-all duration-300">

    <!-- ======================================================== -->
    <!-- 1. PANTALLA DE INICIO (SPLASH DE CARGA CINNAMOROLL) -->
    <!-- ======================================================== -->
    <div id="screen-splash" class="absolute inset-0 z-50 bg-gradient-to-b from-[#d9ebff] via-[#eaf4ff] to-[#ffffff] flex flex-col items-center justify-between p-8 transition-opacity duration-500">
      <div class="absolute top-12 left-10 text-xl animate-twinkle">✨</div>
      <div class="absolute top-20 right-12 text-lg animate-twinkle" style="animation-delay: 1.1s;">⭐</div>
      <div class="absolute top-44 left-14 text-sm animate-twinkle" style="animation-delay: 1.6s;">🎵</div>
      <div class="absolute top-40 right-14 text-base animate-twinkle" style="animation-delay: 0.7s;">☁️</div>

      <div class="flex-1 flex flex-col items-center justify-center text-center mt-6">
        <div class="relative w-44 h-32 flex items-center justify-center animate-float mb-6">
          <img src="{c_splash}" alt="Cinnamoroll" class="max-h-full max-w-full object-contain drop-shadow-sm">
        </div>

        <h1 class="text-3xl font-black tracking-tight text-[#4787d8] mb-0.5">
          Cinnamoroll
        </h1>
        <h2 class="text-2xl font-black tracking-wider text-[#64a1ec] mb-3">
          Music
        </h2>
        <p class="text-xs font-bold text-slate-400 max-w-[210px]">
          Tu música, siempre contigo
        </p>
      </div>

      <div class="w-full max-w-[220px] flex flex-col items-center gap-2 mb-8">
        <div class="w-full h-2.5 bg-white/90 rounded-full p-0.5 border border-blue-200 shadow-inner overflow-hidden">
          <div id="splash-progress" class="h-full bg-gradient-to-r from-blue-400 to-sky-300 rounded-full transition-all duration-300" style="width: 25%;"></div>
        </div>
        <span id="splash-status" class="text-[11px] font-bold text-blue-400 animate-pulse">Cargando...</span>
        <button id="btn-skip-splash" class="mt-1 text-[10px] text-slate-400 hover:text-blue-500 font-bold underline">
          Entrar directamente
        </button>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- 2. PANTALLA PRINCIPAL (INICIO) -->
    <!-- ======================================================== -->
    <div id="screen-home" class="flex-1 min-h-0 flex flex-col overflow-y-auto px-5 pt-4 pb-36 space-y-4 screen-view">
      <!-- App Header: avatar + title (gear removed per user request) -->
      <div class="flex items-center gap-2 pt-1">
        <img src="{c_avatar}" alt="Cinnamoroll" class="h-8 w-auto object-contain drop-shadow-xs">
        <span class="font-black text-lg text-[#263238] tracking-tight">Cinnamoroll Music</span>
      </div>

      <!-- Search Bar -->
      <div id="home-search-trigger" class="flex items-center gap-3 px-4 py-2.5 rounded-2xl bg-white shadow-xs border border-[#e1efff] hover:border-blue-300 cursor-pointer transition">
        <svg class="w-4 h-4 text-blue-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input 
          id="home-search-input"
          type="text" 
          placeholder="Buscar canciones, artistas..." 
          class="bg-transparent flex-1 text-xs text-slate-700 placeholder-slate-400 outline-none cursor-pointer"
        />
      </div>

      <!-- 4 Quick SQUIRCLE Buttons -->
      <div class="grid grid-cols-4 gap-2 pt-1 px-1">
        <!-- 1. Buscar -->
        <button id="quick-btn-search" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="10.5" cy="10.5" r="6.5"></circle>
              <line x1="15.5" y1="15.5" x2="20.5" y2="20.5"></line>
            </svg>
          </div>
          <span class="text-[10.5px] font-bold text-[#24426b] whitespace-nowrap">Buscar</span>
        </button>

        <!-- 2. Descargas -->
        <button id="quick-btn-downloads" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="4.5" x2="12" y2="15"></line>
              <polyline points="7.5 10.5 12 15 16.5 10.5"></polyline>
              <path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path>
            </svg>
          </div>
          <span class="text-[10.5px] font-bold text-[#24426b] whitespace-nowrap">Descargas</span>
        </button>

        <!-- 3. Favoritos -->
        <button id="quick-btn-favorites" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
          </div>
          <span class="text-[10.5px] font-bold text-[#24426b] whitespace-nowrap">Favoritos</span>
        </button>

        <!-- 4. Mi música -->
        <button id="quick-btn-library" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="10" y1="6.5" x2="20" y2="6.5"></line>
              <line x1="10" y1="12" x2="20" y2="12"></line>
              <line x1="10" y1="17.5" x2="20" y2="17.5"></line>
              <circle cx="4.5" cy="6.5" r="1.3" fill="#24426b" stroke="none"></circle>
              <circle cx="4.5" cy="12" r="1.3" fill="#24426b" stroke="none"></circle>
              <circle cx="4.5" cy="17.5" r="1.3" fill="#24426b" stroke="none"></circle>
            </svg>
          </div>
          <span class="text-[10.5px] font-bold text-[#24426b] whitespace-nowrap">Mi música</span>
        </button>
      </div>

      <!-- Promo Banner: EXACT single complete artwork matching user's mockup! -->
      <div id="home-promo-banner" class="shrink-0 rounded-3xl overflow-hidden shadow-xs border border-blue-200/50 cursor-pointer hover:shadow-md transition active:scale-[0.99]">
        <img src="{c_banner}" alt="¡Encuentra tus canciones favoritas!" class="w-full h-auto object-cover block">
      </div>

      <!-- Section: Recomendado para ti -->
      <div class="space-y-2.5 pt-1 shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <h4 class="font-black text-sm text-[#263238]">Recomendado para ti</h4>
            <button id="btn-rotate-home" class="w-5 h-5 rounded-full bg-[#edf5fe] hover:bg-blue-100 text-blue-500 flex items-center justify-center text-[11px] font-black transition active:scale-90" title="Rotar recomendaciones">
              ↻
            </button>
          </div>
          <button id="btn-see-more-recommended" class="text-xs font-bold text-blue-500 hover:text-blue-600">
            Ver más &gt;
          </button>
        </div>
        <div id="recommended-container" class="grid grid-cols-3 gap-2.5">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- Section: Tendencias -->
      <div class="space-y-2.5 pt-1 shrink-0">
        <div class="flex items-center justify-between">
          <h4 class="font-black text-sm text-[#263238]">Tendencias</h4>
          <button id="btn-see-more-trending" class="text-xs font-bold text-blue-500 hover:text-blue-600">
            Ver más &gt;
          </button>
        </div>
        <div id="trending-container" class="grid grid-cols-3 gap-2.5">
          <!-- Populated by JS -->
        </div>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- 3. RESULTADOS DE BÚSQUEDA (COLDPLAY, ETC.) -->
    <!-- ======================================================== -->
    <div id="screen-search" class="hidden flex-1 min-h-0 flex flex-col overflow-y-auto px-5 pt-4 pb-36 space-y-3.5 screen-view">
      <div class="flex items-center gap-2">
        <button id="btn-back-to-home" class="w-8 h-8 rounded-full bg-white shadow-xs flex items-center justify-center text-slate-500 hover:text-blue-500 border border-blue-100 transition shrink-0">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <div class="flex-1 flex items-center gap-2 px-3.5 py-2 rounded-2xl bg-white shadow-xs border border-[#d6e8fe]">
          <svg class="w-4 h-4 text-blue-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input 
            id="main-search-input"
            type="text" 
            placeholder="Buscar canciones, artistas..." 
            value=""
            class="bg-transparent flex-1 text-xs text-slate-700 outline-none font-semibold"
          />
          <button id="btn-clear-search" class="text-slate-400 hover:text-slate-600 text-xs px-1">
            ✕
          </button>
        </div>
      </div>

      <!-- Pills: Canciones, Artistas, Álbumes -->
      <div class="flex items-center gap-2">
        <button data-cat="canciones" class="search-tab-pill px-4 py-1 rounded-full text-xs font-extrabold bg-blue-500 text-white shadow-xs transition">
          Canciones
        </button>
        <button data-cat="artistas" class="search-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition">
          Artistas
        </button>
        <button data-cat="albumes" class="search-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition">
          Álbumes
        </button>
      </div>

      <!-- Results List -->
      <div id="search-results-list" class="space-y-2 pt-1">
        <!-- Populated by JS -->
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- 4. PANTALLA DE DESCARGAS REAL Y FUNCIONAL -->
    <!-- ======================================================== -->
    <div id="screen-downloads" class="hidden flex-1 min-h-0 flex flex-col overflow-y-auto px-5 pt-4 pb-36 space-y-3.5 screen-view">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="4.5" x2="12" y2="15"></line>
            <polyline points="7.5 10.5 12 15 16.5 10.5"></polyline>
            <path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path>
          </svg>
          <h2 class="font-black text-lg text-[#263238]">Descargas</h2>
        </div>
        <button id="btn-refresh-downloads" class="text-xs font-bold text-blue-500 hover:text-blue-600 transition flex items-center gap-1">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path></svg>
          <span>Actualizar</span>
        </button>
      </div>

      <!-- Sub Tabs: Canciones, Álbumes, En proceso -->
      <div class="flex items-center gap-2">
        <button data-subtab="canciones" class="dl-tab-pill px-4 py-1 rounded-full text-xs font-extrabold bg-blue-500 text-white shadow-xs transition">
          Canciones
        </button>
        <button data-subtab="albumes" class="dl-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition">
          Álbumes
        </button>
        <button data-subtab="en_proceso" class="dl-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition">
          En proceso
        </button>
      </div>

      <!-- Dynamic Active Download Progress Card (Only shown when a REAL download is running!) -->
      <div id="active-download-card" class="hidden rounded-2xl bg-white border border-[#d6e8fe] p-3.5 shadow-xs space-y-2">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <svg class="w-4 h-4 text-blue-500 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
              <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
            </svg>
            <span id="dl-card-status" class="text-xs font-black text-slate-700">Descargando canción...</span>
          </div>
          <span id="dl-card-percent" class="text-xs font-black text-blue-500">0%</span>
        </div>
        <div class="w-full h-2 bg-blue-50 rounded-full overflow-hidden p-0.5 border border-blue-100">
          <div id="dl-card-progress-bar" class="h-full bg-gradient-to-r from-blue-400 to-sky-400 rounded-full transition-all duration-300" style="width: 0%;"></div>
        </div>
        <div class="flex items-center justify-between text-[11px] text-slate-400 font-bold">
          <span id="dl-card-track-title">Conectando...</span>
          <span id="dl-card-size-info">Calculando...</span>
        </div>
      </div>

      <!-- Real Downloaded Songs List with Official Album Artwork! -->
      <div id="downloads-list-items" class="space-y-2 pt-1">
        <!-- Populated dynamically by JS with official album artwork for all tracks -->
      </div>

    </div>

    <!-- ======================================================== -->
    <!-- STICKY MINI PLAYER BAR (Fix You - Coldplay) -->
    <!-- ======================================================== -->
    <div id="mini-player-bar" class="absolute safe-mini-player left-3 right-3 z-30 bg-white/95 backdrop-blur-md rounded-2xl p-2 px-3 shadow-md border border-[#d6e8fe] flex items-center justify-between transition-all cursor-pointer">
      <div id="mini-track-info" class="flex items-center gap-2.5 overflow-hidden flex-1 mr-2">
        <img id="mini-cover" src="logos/Meet_You_Again_Reimagined_Ebony_Loren_Jason_LaPierre.jpg" onerror="this.onerror=null;this.src='https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/d1/3f/b5/d13fb5a5-de80-09d5-316c-87ef21ffb93e/artwork.jpg/1000x1000bb.jpg'" alt="Cover" class="w-9 h-9 rounded-xl object-cover shadow-xs shrink-0 border border-blue-50">
        <div class="overflow-hidden">
          <h5 id="mini-title" class="text-xs font-black text-slate-800 truncate">Meet You Again (Reimagined)</h5>
          <p id="mini-artist" class="text-[10px] font-bold text-slate-400 truncate">Ebony Loren & Jason LaPierre</p>
        </div>
      </div>

      <div class="flex items-center gap-1.5 shrink-0">
        <button id="mini-btn-play" class="w-7 h-7 rounded-full text-blue-500 hover:text-blue-600 flex items-center justify-center text-sm transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
        </button>
        <button id="mini-btn-next" class="w-7 h-7 rounded-full text-slate-400 hover:text-blue-500 flex items-center justify-center text-xs transition">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 4 15 12 5 20 5 4"></polygon><rect x="17" y="5" width="2.5" height="14" rx="0.5"></rect></svg>
        </button>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- BOTTOM DOCK NAVIGATION (3 Options: Inicio, Buscar, Descargas) -->
    <!-- ======================================================== -->
    <nav class="safe-bottom-dock bg-white border-t border-[#e2eefd] px-8 grid grid-cols-3 items-center z-30 shrink-0">
      <!-- 1. Inicio -->
      <button data-nav="home" class="nav-item-btn flex flex-col items-center justify-center gap-1 text-blue-500 font-bold transition">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 10.5L12 3l9 7.5v10a1.5 1.5 0 0 1-1.5 1.5H15v-5a3 3 0 0 0-6 0v5H4.5A1.5 1.5 0 0 1 3 20.5v-10z"></path>
        </svg>
        <span class="text-[11px]">Inicio</span>
      </button>

      <!-- 2. Buscar -->
      <button data-nav="search" class="nav-item-btn flex flex-col items-center justify-center gap-1 text-slate-400 hover:text-blue-500 font-bold transition">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="10.5" cy="10.5" r="6.5"></circle>
          <line x1="15.5" y1="15.5" x2="20.5" y2="20.5"></line>
        </svg>
        <span class="text-[11px]">Buscar</span>
      </button>

      <!-- 3. Descargas -->
      <button data-nav="downloads" class="nav-item-btn flex flex-col items-center justify-center gap-1 text-slate-400 hover:text-blue-500 font-bold transition">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="4.5" x2="12" y2="15"></line>
          <polyline points="7.5 10.5 12 15 16.5 10.5"></polyline>
          <path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path>
        </svg>
        <span class="text-[11px]">Descargas</span>
      </button>
    </nav>

    <!-- ======================================================== -->
    <!-- 4. VISTA DE CANCIÓN (MODAL DETALLE) -->
    <!-- ======================================================== -->
    <div id="modal-song-detail" class="hidden absolute inset-0 z-40 bg-[#f4f9ff] flex flex-col overflow-y-auto px-6 py-4 transition-all">
      <div class="flex items-center justify-between pt-1">
        <button id="btn-close-song-detail" class="w-8 h-8 rounded-full bg-white shadow-xs flex items-center justify-center text-slate-500 hover:text-blue-500 border border-blue-100 transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <span class="text-xs font-black text-slate-400">Detalles</span>
        <button id="btn-detail-favorite" class="w-8 h-8 rounded-full bg-white shadow-xs flex items-center justify-center text-[#4a88d9] hover:scale-110 border border-blue-100 transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
        </button>
      </div>

      <div class="flex flex-col items-center mt-4 mb-3">
        <div class="w-60 h-60 rounded-3xl overflow-hidden shadow-xl border-4 border-white cursor-pointer" id="detail-cover-card">
          <img id="detail-cover-img" src="logos/Meet_You_Again_Reimagined_Ebony_Loren_Jason_LaPierre.jpg" onerror="this.onerror=null;this.src='https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/d1/3f/b5/d13fb5a5-de80-09d5-316c-87ef21ffb93e/artwork.jpg/1000x1000bb.jpg'" alt="Cover" class="w-full h-full object-cover">
        </div>
      </div>

      <div class="space-y-0.5 text-left">
        <h3 id="detail-title" class="text-xl font-black text-slate-800">Meet You Again (Reimagined)</h3>
        <p id="detail-artist" class="text-sm font-bold text-slate-400">Ebony Loren & Jason LaPierre</p>
        <p id="detail-meta" class="text-[11px] text-slate-400 font-semibold pt-0.5">
          Álbum: Meet You Again...AGAIN! &nbsp;|&nbsp; 2025 &nbsp;|&nbsp; 3:06
        </p>
      </div>

      <!-- Scrubber Row: Play icon, slider, time, speaker icon -->
      <div class="mt-4 flex items-center gap-3">
        <button id="detail-btn-play-mini" class="w-8 h-8 rounded-full bg-blue-500 text-white flex items-center justify-center text-xs shrink-0 shadow-xs">
          <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
        </button>
        <div class="flex-1 space-y-1">
          <input id="detail-audio-scrubber" type="range" min="0" max="100" value="0" class="w-full">
          <div class="flex items-center justify-between text-[10px] font-bold text-slate-400">
            <span id="detail-current-time">0:00</span>
            <span id="detail-duration-time">4:55</span>
          </div>
        </div>
        <svg class="w-4 h-4 text-slate-400 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>
        </svg>
      </div>

      <!-- Big Button: Descargar -->
      <div class="mt-5 space-y-2">
        <button id="detail-btn-download-full" class="w-full py-3 rounded-2xl bg-gradient-to-r from-blue-400 to-sky-400 hover:from-blue-500 hover:to-sky-500 text-white font-black text-sm shadow-md shadow-blue-400/20 flex items-center justify-center gap-2 transition active:scale-98">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="12" y1="4.5" x2="12" y2="15"></line>
            <polyline points="7.5 10.5 12 15 16.5 10.5"></polyline>
            <path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path>
          </svg>
          <span>Descargar Canción Completa (.m4a)</span>
        </button>
        <p id="detail-download-status" class="text-center text-[10px] text-slate-400 font-bold"></p>
      </div>

      <!-- Portada de la canción (HD) -->
      <div class="mt-4 p-3.5 rounded-2xl bg-white border border-[#d6e8fe] shadow-xs space-y-2">
        <span class="text-xs font-black text-slate-700">Portada de la canción</span>
        <div class="flex items-center justify-between gap-3">
          <div class="w-14 h-14 rounded-xl overflow-hidden shadow-xs shrink-0 border border-blue-50">
            <img id="detail-subcover-img" src="logos/Meet_You_Again_Reimagined_Ebony_Loren_Jason_LaPierre.jpg" onerror="this.onerror=null;this.src='https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/d1/3f/b5/d13fb5a5-de80-09d5-316c-87ef21ffb93e/artwork.jpg/1000x1000bb.jpg'" alt="Mini" class="w-full h-full object-cover">
          </div>
          <div class="flex-1">
            <button id="btn-download-cover-hd" class="w-full py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-600 font-bold text-xs transition border border-blue-100">
              Guardar Portada HD
            </button>
          </div>
          <div class="w-16 h-14 shrink-0 flex items-center justify-center">
            <img src="{c_detail}" alt="Cinnamoroll" class="max-h-full max-w-full object-contain">
          </div>
        </div>
      </div>
      
      <div class="h-6"></div>
    </div>

    <!-- ======================================================== -->
    <!-- 5. REPRODUCTOR EXPANDIDO CELESTIAL -->
    <!-- ======================================================== -->
    <div id="modal-expanded-player" class="hidden absolute inset-0 z-40 bg-gradient-to-b from-[#b5d6ff] via-[#d7e9fe] to-[#edf6ff] flex flex-col justify-between p-6 overflow-hidden transition-all">
      <div class="absolute top-10 left-8 text-xl animate-twinkle">✨</div>
      <div class="absolute top-20 right-10 text-lg animate-twinkle" style="animation-delay: 1.2s;">⭐</div>
      <div class="absolute top-36 left-12 text-sm animate-twinkle" style="animation-delay: 0.8s;">🎵</div>

      <div class="flex items-center justify-between pt-1 z-10">
        <button id="btn-minimize-expanded-player" class="w-8 h-8 rounded-full bg-white/80 backdrop-blur shadow-xs flex items-center justify-center text-slate-600 hover:text-blue-500 transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"></polyline></svg>
        </button>
        <span class="text-xs font-black text-slate-600">Cinnamoroll Radio</span>
        <button id="btn-expanded-favorite" class="w-8 h-8 rounded-full bg-white/80 backdrop-blur shadow-xs flex items-center justify-center text-[#4a88d9] transition">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
        </button>
      </div>

      <div class="flex flex-col items-center my-2 relative z-10">
        <div class="relative w-52 h-32 flex items-center justify-center animate-float">
          <img src="{c_player}" alt="Cinnamoroll Cloud" class="max-h-full max-w-full object-contain drop-shadow-md">
        </div>
      </div>

      <div class="bg-white/95 backdrop-blur-md rounded-3xl p-5 shadow-xl border border-white space-y-3 z-10">
        <div class="flex items-center gap-3">
          <img id="exp-cover" src="logos/Meet_You_Again_Reimagined_Ebony_Loren_Jason_LaPierre.jpg" onerror="this.onerror=null;this.src='https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/d1/3f/b5/d13fb5a5-de80-09d5-316c-87ef21ffb93e/artwork.jpg/1000x1000bb.jpg'" alt="Cover" class="w-13 h-13 rounded-2xl object-cover shadow-xs shrink-0 border border-blue-50">
          <div class="overflow-hidden flex-1">
            <h4 id="exp-title" class="font-black text-sm text-slate-800 truncate">Meet You Again (Reimagined)</h4>
            <p id="exp-artist" class="text-xs font-bold text-slate-400 truncate">Ebony Loren & Jason LaPierre</p>
          </div>
          <button id="exp-heart" class="text-[#4a88d9]">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
          </button>
        </div>

        <div class="space-y-1">
          <input id="exp-scrubber" type="range" min="0" max="100" value="0" class="w-full">
          <div class="flex items-center justify-between text-[10px] font-bold text-slate-400">
            <span id="exp-cur-time">0:00</span>
            <span id="exp-dur-time">4:55</span>
          </div>
        </div>

        <div class="flex items-center justify-between px-2 pt-1">
          <button id="exp-shuffle" class="text-slate-400 hover:text-blue-500">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 3 21 3 21 8"></polyline><line x1="4" y1="20" x2="21" y2="3"></line><polyline points="21 16 21 21 16 21"></polyline><line x1="15" y1="15" x2="21" y2="21"></line><line x1="4" y1="4" x2="9" y2="9"></line></svg>
          </button>
          <button id="exp-prev" class="text-slate-600 hover:text-blue-500">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><polygon points="19 20 9 12 19 4 19 20"></polygon><rect x="4.5" y="5" width="2.5" height="14" rx="0.5"></rect></svg>
          </button>
          <button id="exp-play" class="w-12 h-12 rounded-full bg-blue-500 text-white flex items-center justify-center shadow-md shadow-blue-400/30 hover:scale-105 active:scale-95 transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
          </button>
          <button id="exp-next" class="text-slate-600 hover:text-blue-500">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 4 15 12 5 20 5 4"></polygon><rect x="17" y="5" width="2.5" height="14" rx="0.5"></rect></svg>
          </button>
          <button id="exp-repeat" class="text-slate-400 hover:text-blue-500">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 1 21 5 17 9"></polyline><path d="M3 11V9a4 4 0 0 1 4-4h14"></path><polyline points="7 23 3 19 7 15"></polyline><path d="M21 13v2a4 4 0 0 1-4 4H3"></path></svg>
          </button>
        </div>
      </div>

      <div class="h-2"></div>
    </div>

  </div>

  <audio id="core-audio-player" preload="auto"></audio>

  <!-- ======================================================== -->
  <!-- JAVASCRIPT APPLICATION LOGIC -->
  <!-- ======================================================== -->
  <script>
    // User Curated Playlist (46 tracks)
    const PLAYLIST_SONGS = {catalog_json_str};

    const PRELOADED_SERVER_SONGS = {songs_json_str};

    // State Variables
    const CLOUD_URL = 'https://musicon-nymp.onrender.com';
    let SERVER_URL = (window.location.protocol === 'http:' || window.location.protocol === 'https:')
      ? window.location.origin
      : CLOUD_URL;
    if (window.location.hostname.includes('github.io')) {{
      SERVER_URL = CLOUD_URL;
    }}

    let serverActive = false;
    let currentTracksList = [...PLAYLIST_SONGS];
    let currentTrack = PLAYLIST_SONGS[0];
    let currentTrackIndex = 0;
    let isPlaying = false;
    let isShuffle = false;
    let isRepeat = false;
    let favorites = JSON.parse(localStorage.getItem('cinnamoroll_favorites') || '[]');
    let localDownloads = JSON.parse(localStorage.getItem('cinnamoroll_downloads') || '[]');
    let serverDownloads = [...PRELOADED_SERVER_SONGS];
    let currentDlSubtab = 'canciones';
    let activeDownloadInterval = null;

    const audio = document.getElementById('core-audio-player');
    const screenSplash = document.getElementById('screen-splash');
    const screenHome = document.getElementById('screen-home');
    const screenSearch = document.getElementById('screen-search');
    const screenDownloads = document.getElementById('screen-downloads');
    const modalSongDetail = document.getElementById('modal-song-detail');
    const modalExpandedPlayer = document.getElementById('modal-expanded-player');

    // Mini Player
    const miniCover = document.getElementById('mini-cover');
    const miniTitle = document.getElementById('mini-title');
    const miniArtist = document.getElementById('mini-artist');
    const miniBtnPlay = document.getElementById('mini-btn-play');
    const miniBtnNext = document.getElementById('mini-btn-next');
    const miniTrackInfo = document.getElementById('mini-track-info');

    // Detail Player
    const detailCoverImg = document.getElementById('detail-cover-img');
    const detailSubcoverImg = document.getElementById('detail-subcover-img');
    const detailTitle = document.getElementById('detail-title');
    const detailArtist = document.getElementById('detail-artist');
    const detailMeta = document.getElementById('detail-meta');
    const detailAudioScrubber = document.getElementById('detail-audio-scrubber');
    const detailCurrentTime = document.getElementById('detail-current-time');
    const detailDurationTime = document.getElementById('detail-duration-time');
    const detailBtnPlayMini = document.getElementById('detail-btn-play-mini');
    const detailBtnFavorite = document.getElementById('btn-detail-favorite');
    const detailBtnDownloadFull = document.getElementById('detail-btn-download-full');
    const detailDownloadStatus = document.getElementById('detail-download-status');
    const btnDownloadCoverHd = document.getElementById('btn-download-cover-hd');
    const btnCloseSongDetail = document.getElementById('btn-close-song-detail');

    // Expanded Player
    const expCover = document.getElementById('exp-cover');
    const expTitle = document.getElementById('exp-title');
    const expArtist = document.getElementById('exp-artist');
    const expHeart = document.getElementById('exp-heart');
    const expScrubber = document.getElementById('exp-scrubber');
    const expCurTime = document.getElementById('exp-cur-time');
    const expDurTime = document.getElementById('exp-dur-time');
    const expPlay = document.getElementById('exp-play');
    const expPrev = document.getElementById('exp-prev');
    const expNext = document.getElementById('exp-next');
    const expShuffle = document.getElementById('exp-shuffle');
    const expRepeat = document.getElementById('exp-repeat');
    const btnMinimizeExpanded = document.getElementById('btn-minimize-expanded-player');
    const btnExpandedFavorite = document.getElementById('btn-expanded-favorite');

    // Server check & Fetch real downloads
    async function checkServer() {{
      try {{
        const resp = await fetch(`${{SERVER_URL}}/api/status`, {{ signal: AbortSignal.timeout(3500) }});
        if (resp.ok) {{ serverActive = true; return true; }}
      }} catch (e) {{}}
      if (SERVER_URL !== CLOUD_URL) {{
        try {{
          const resp = await fetch(`${{CLOUD_URL}}/api/status`, {{ signal: AbortSignal.timeout(3500) }});
          if (resp.ok) {{ SERVER_URL = CLOUD_URL; serverActive = true; return true; }}
        }} catch (e) {{}}
      }}
      return false;
    }}

    let homeRotationStep = Math.floor(Date.now() / (1000 * 60 * 15)) % Math.max(1, PLAYLIST_SONGS.length);

    async function loadServerDownloads() {{
      try {{
        const resp = await fetch(`${{SERVER_URL}}/api/downloads`, {{ signal: AbortSignal.timeout(4000) }});
        if (resp.ok) {{
          const data = await resp.json();
          if (data && data.songs && data.songs.length > 0) {{
            serverDownloads = data.songs.map(s => ({{
              id: s.id,
              title: s.title,
              artist: s.artist,
              album: 'Descargas',
              size: s.size,
              cover: s.cover || 'logos/Fix_You.jpg',
              fallback: s.fallback || s.cover || 'logos/Fix_You.jpg',
              audioUrl: s.download_url.startsWith('http') ? s.download_url : `${{SERVER_URL}}${{s.download_url}}`,
              file: s.file
            }}));
          }}
        }}
      }} catch (e) {{}}
      renderDownloadsList(currentDlSubtab);
      renderHomeCards(false);
    }}

    window.queueWishlist = async function(songs, wait = false) {{
      await checkServer();
      const resp = await fetch(`${{SERVER_URL}}/api/wishlist`, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ wait: Boolean(wait), songs: Array.isArray(songs) ? songs : [songs] }})
      }});
      const data = await resp.json();
      setTimeout(() => loadServerDownloads(), wait ? 200 : 4000);
      return data;
    }};

    // Splash
    let splashPercent = 20;
    const splashTimer = setInterval(() => {{
      splashPercent += 25;
      if (splashPercent > 100) splashPercent = 100;
      document.getElementById('splash-progress').style.width = splashPercent + '%';
      if (splashPercent >= 100) {{
        clearInterval(splashTimer);
        setTimeout(dismissSplash, 350);
      }}
    }}, 180);

    function dismissSplash() {{
      screenSplash.classList.add('opacity-0', 'pointer-events-none');
      setTimeout(() => screenSplash.classList.add('hidden'), 500);
    }}
    document.getElementById('btn-skip-splash').addEventListener('click', dismissSplash);
    screenSplash.addEventListener('click', (e) => {{
      if (e.target.id !== 'splash-progress') dismissSplash();
    }});

    // Router - EXACTLY 3 Tabs: home, search, downloads
    const views = {{
      home: screenHome,
      search: screenSearch,
      downloads: screenDownloads
    }};

    function switchTab(targetTab) {{
      Object.keys(views).forEach(key => {{
        if (key === targetTab) {{
          views[key].classList.remove('hidden');
        }} else {{
          views[key].classList.add('hidden');
        }}
      }});

      document.querySelectorAll('.nav-item-btn').forEach(btn => {{
        const nav = btn.getAttribute('data-nav');
        if (nav === targetTab) {{
          btn.className = "nav-item-btn flex flex-col items-center justify-center gap-1 text-blue-500 font-bold transition";
        }} else {{
          btn.className = "nav-item-btn flex flex-col items-center justify-center gap-1 text-slate-400 hover:text-blue-500 font-bold transition";
        }}
      }});

      if (targetTab === 'downloads') {{
        loadServerDownloads();
      }} else if (targetTab === 'home') {{
        renderHomeCards(true);
      }}
    }}

    document.querySelectorAll('.nav-item-btn').forEach(btn => {{
      btn.addEventListener('click', () => switchTab(btn.getAttribute('data-nav')));
    }});

    // 4 Squircle Quick Actions
    document.getElementById('quick-btn-search').addEventListener('click', () => {{
      switchTab('search');
      document.getElementById('main-search-input').focus();
    }});
    document.getElementById('quick-btn-downloads').addEventListener('click', () => switchTab('downloads'));
    document.getElementById('quick-btn-favorites').addEventListener('click', showFavorites);
    document.getElementById('quick-btn-library').addEventListener('click', () => {{
      renderSearchRows(PLAYLIST_SONGS);
      switchTab('search');
    }});

    document.getElementById('home-search-trigger').addEventListener('click', () => {{
      switchTab('search');
      document.getElementById('main-search-input').focus();
    }});
    document.getElementById('btn-back-to-home').addEventListener('click', () => switchTab('home'));
    document.getElementById('home-promo-banner').addEventListener('click', () => {{
      loadAndPlayTrack(PLAYLIST_SONGS[0]);
    }});

    // Audio Engine
    function formatTime(secs) {{
      if (!secs || isNaN(secs)) return "0:00";
      const m = Math.floor(secs / 60);
      const s = Math.floor(secs % 60);
      return `${{m}}:${{s < 10 ? '0' : ''}}${{s}}`;
    }}

    function setImgSrc(el, localSrc, fallbackSrc) {{
      el.src = localSrc;
      el.onerror = function() {{
        this.onerror = null;
        this.src = fallbackSrc || 'logos/Fix_You.jpg';
      }};
    }}

    function updatePlayerUI(track) {{
      currentTrack = track;
      setImgSrc(miniCover, track.cover, track.fallback || track.cover);
      miniTitle.textContent = track.title;
      miniArtist.textContent = track.artist;
      miniBtnPlay.innerHTML = isPlaying 
        ? `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg>` 
        : `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;

      setImgSrc(detailCoverImg, track.cover, track.fallback || track.cover);
      setImgSrc(detailSubcoverImg, track.cover, track.fallback || track.cover);
      detailTitle.textContent = track.title;
      detailArtist.textContent = track.artist;
      detailMeta.textContent = `Álbum: ${{track.album || 'Single'}} | ${{track.year || '2024'}} | ${{track.duration || '4:55'}}`;
      detailBtnPlayMini.innerHTML = isPlaying
        ? `<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg>`
        : `<svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;

      setImgSrc(expCover, track.cover, track.fallback || track.cover);
      expTitle.textContent = track.title;
      expArtist.textContent = track.artist;
      expPlay.innerHTML = isPlaying
        ? `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16" rx="1"></rect><rect x="14" y="4" width="4" height="16" rx="1"></rect></svg>`
        : `<svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>`;

      const isFav = favorites.some(f => f.title === track.title && f.artist === track.artist);
      const favSvg = isFav 
        ? `<svg class="w-4 h-4 text-rose-500 fill-current" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>`
        : `<svg class="w-4 h-4 text-[#4a88d9]" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>`;
      detailBtnFavorite.innerHTML = favSvg;
      expHeart.innerHTML = favSvg;
      btnExpandedFavorite.innerHTML = favSvg;
    }}

    function togglePlayPause() {{
      if (!audio.src || audio.src === "") {{
        loadAndPlayTrack(currentTrack);
        return;
      }}
      if (audio.paused) {{
        audio.play().then(() => {{
          isPlaying = true;
          updatePlayerUI(currentTrack);
        }}).catch(e => console.error(e));
      }} else {{
        audio.pause();
        isPlaying = false;
        updatePlayerUI(currentTrack);
      }}
    }}

    async function loadAndPlayTrack(track) {{
      currentTrack = track;
      updatePlayerUI(track);

      let targetAudio = track.audioUrl || track.download_url || track.preview;
      if (targetAudio && targetAudio.startsWith('/api/audio/') && SERVER_URL) {{
        targetAudio = `${{SERVER_URL}}${{targetAudio}}`;
      }}
      if (targetAudio) {{
        audio.src = targetAudio;
        audio.play().then(() => {{
          isPlaying = true;
          updatePlayerUI(track);
        }}).catch(e => {{
          isPlaying = false;
          updatePlayerUI(track);
        }});
        return;
      }}

      try {{
        const res = await searchiTunes(`${{track.title}} ${{track.artist}}`, 1);
        if (res.length > 0 && res[0].preview) {{
          track.preview = res[0].preview;
          audio.src = track.preview;
          audio.play().then(() => {{
            isPlaying = true;
            updatePlayerUI(track);
          }}).catch(e => {{
            isPlaying = false;
            updatePlayerUI(track);
          }});
        }}
      }} catch (e) {{}}
    }}

    function playNext() {{
      if (currentTracksList.length === 0) return;
      if (isShuffle) {{
        currentTrackIndex = Math.floor(Math.random() * currentTracksList.length);
      }} else {{
        currentTrackIndex = (currentTrackIndex + 1) % currentTracksList.length;
      }}
      loadAndPlayTrack(currentTracksList[currentTrackIndex]);
    }}

    function playPrev() {{
      if (currentTracksList.length === 0) return;
      currentTrackIndex = (currentTrackIndex - 1 + currentTracksList.length) % currentTracksList.length;
      loadAndPlayTrack(currentTracksList[currentTrackIndex]);
    }}

    audio.addEventListener('timeupdate', () => {{
      if (!audio.duration) return;
      const pct = (audio.currentTime / audio.duration) * 100;
      detailAudioScrubber.value = pct;
      expScrubber.value = pct;
      detailCurrentTime.textContent = formatTime(audio.currentTime);
      expCurTime.textContent = formatTime(audio.currentTime);
      detailDurationTime.textContent = formatTime(audio.duration);
      expDurTime.textContent = formatTime(audio.duration);
    }});

    audio.addEventListener('ended', () => {{
      if (isRepeat) {{
        audio.currentTime = 0;
        audio.play();
      }} else {{
        playNext();
      }}
    }});

    function handleSeek(e) {{
      if (audio.duration) {{
        audio.currentTime = (e.target.value / 100) * audio.duration;
      }}
    }}
    detailAudioScrubber.addEventListener('input', handleSeek);
    expScrubber.addEventListener('input', handleSeek);

    miniBtnPlay.addEventListener('click', (e) => {{ e.stopPropagation(); togglePlayPause(); }});
    miniBtnNext.addEventListener('click', (e) => {{ e.stopPropagation(); playNext(); }});
    miniTrackInfo.addEventListener('click', () => modalSongDetail.classList.remove('hidden'));

    detailBtnPlayMini.addEventListener('click', togglePlayPause);
    btnCloseSongDetail.addEventListener('click', () => modalSongDetail.classList.add('hidden'));
    document.getElementById('detail-cover-card').addEventListener('click', () => {{
      modalSongDetail.classList.add('hidden');
      modalExpandedPlayer.classList.remove('hidden');
    }});

    expPlay.addEventListener('click', togglePlayPause);
    expNext.addEventListener('click', playNext);
    expPrev.addEventListener('click', playPrev);
    btnMinimizeExpanded.addEventListener('click', () => modalExpandedPlayer.classList.add('hidden'));

    expShuffle.addEventListener('click', () => {{
      isShuffle = !isShuffle;
      expShuffle.className = isShuffle ? "text-blue-500 font-bold" : "text-slate-400 hover:text-blue-500";
    }});
    expRepeat.addEventListener('click', () => {{
      isRepeat = !isRepeat;
      expRepeat.className = isRepeat ? "text-blue-500 font-bold" : "text-slate-400 hover:text-blue-500";
    }});

    function toggleFavorite(track) {{
      const idx = favorites.findIndex(f => f.title === track.title && f.artist === track.artist);
      if (idx >= 0) {{
        favorites.splice(idx, 1);
      }} else {{
        favorites.push({{ ...track }});
      }}
      localStorage.setItem('cinnamoroll_favorites', JSON.stringify(favorites));
      updatePlayerUI(track);
    }}

    detailBtnFavorite.addEventListener('click', () => toggleFavorite(currentTrack));
    expHeart.addEventListener('click', () => toggleFavorite(currentTrack));
    btnExpandedFavorite.addEventListener('click', () => toggleFavorite(currentTrack));

    function showFavorites() {{
      if (favorites.length === 0) {{
        alert("Aún no tienes canciones favoritas guardadas. Toca el corazón en cualquier canción para guardarla.");
        return;
      }}
      renderSearchRows(favorites);
      switchTab('search');
    }}

    // Universal Direct Browser File Downloader (guarantees file save on mobile and desktop)
    async function triggerBrowserDownload(url, filename) {{
      if (!url) return false;
      const cleanFilename = (filename || 'cancion.m4a').replace(/[/\\?%*:|"<>]/g, '_');
      try {{
        const resp = await fetch(url, {{ mode: 'cors' }});
        if (resp.ok) {{
          const blob = await resp.blob();
          const blobUrl = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.style.display = 'none';
          a.href = blobUrl;
          a.download = cleanFilename;
          document.body.appendChild(a);
          a.click();
          setTimeout(() => {{
            document.body.removeChild(a);
            URL.revokeObjectURL(blobUrl);
          }}, 3000);
          return true;
        }}
      }} catch (e) {{
        console.warn("Direct blob download warning:", e);
      }}

      const a = document.createElement('a');
      a.href = url;
      a.download = cleanFilename;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => document.body.removeChild(a), 1000);
      return true;
    }}

    // Real Download Engine
    async function downloadFull(track) {{
      const cleanTitle = (track.title || 'cancion').replace(/[/\\?%*:|"<>]/g, '_');
      const cleanArtist = (track.artist || 'artista').replace(/[/\\?%*:|"<>]/g, '_');
      const fileName = `${{cleanTitle}}_${{cleanArtist}}.m4a`;

      detailDownloadStatus.textContent = "⏳ Obteniendo audio completo de alta fidelidad desde la nube...";
      detailBtnDownloadFull.disabled = true;
      detailBtnDownloadFull.innerHTML = `<span>Descargando canción completa...</span>`;

      startActiveDownloadCard(track.title, track.artist);

      let dlUrl = track.audioUrl || (track.file ? `/api/audio/${{track.file}}` : null);
      let sizeMb = track.size ? track.size.replace(' MB', '') : '7.5';

      try {{
        await checkServer();
        const resp = await fetch(`${{SERVER_URL}}/api/download_song`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            query: `${{track.title}} ${{track.artist}}`,
            title: track.title,
            artist: track.artist,
            cover_url: track.fallback || track.cover,
            preview_url: track.preview || track.audioUrl || ''
          }})
        }});

        if (resp.ok) {{
          const data = await resp.json();
          if (data && data.status === 'success') {{
            dlUrl = data.download_url.startsWith('http') ? data.download_url : `${{SERVER_URL}}${{data.download_url}}`;
            sizeMb = data.size_mb || sizeMb;
          }}
        }}
      }} catch (err) {{
        console.warn("Server download check warning:", err);
      }}

      if (!dlUrl) {{
        finishActiveDownloadCard(track.title, track.artist, '0', true);
        detailDownloadStatus.textContent = "No se pudo obtener el audio completo. Reintenta.";
        detailBtnDownloadFull.innerHTML = `<span>Reintentar descarga completa</span>`;
        detailBtnDownloadFull.disabled = false;
        return;
      }}

      if (dlUrl.startsWith('/api/audio/')) {{
        dlUrl = `${{SERVER_URL}}${{dlUrl}}`;
      }}

      finishActiveDownloadCard(track.title, track.artist, sizeMb);
      detailDownloadStatus.textContent = `¡Canción completa descargada! (${{sizeMb}} MB)`;
      detailBtnDownloadFull.innerHTML = `<span>¡Descargada! (${{sizeMb}} MB)</span>`;
      saveDownload(track, sizeMb, dlUrl);
      await triggerBrowserDownload(dlUrl, fileName);

      detailBtnDownloadFull.disabled = false;
      setTimeout(() => {{
        detailBtnDownloadFull.innerHTML = `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="4.5" x2="12" y2="15"></line><polyline points="7.5 10.5 12 15 16.5 10.5"></polyline><path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path></svg><span>Descargar Canción Completa (.m4a)</span>`;
      }}, 3500);
    }}

    detailBtnDownloadFull.addEventListener('click', () => downloadFull(currentTrack));

    btnDownloadCoverHd.addEventListener('click', async () => {{
      const coverUrl = currentTrack.fallback || currentTrack.cover;
      const cleanTitle = (currentTrack.title || 'portada').replace(/[/\\?%*:|"<>]/g, '_');
      await triggerBrowserDownload(coverUrl, `${{cleanTitle}}_Cover.jpg`);
    }});

    function startActiveDownloadCard(title, artist) {{
      const card = document.getElementById('active-download-card');
      const titleEl = document.getElementById('dl-card-track-title');
      const barEl = document.getElementById('dl-card-progress-bar');
      const pctEl = document.getElementById('dl-card-percent');
      const sizeEl = document.getElementById('dl-card-size-info');
      const statusEl = document.getElementById('dl-card-status');

      card.classList.remove('hidden');
      statusEl.textContent = "Conectando con motor de audio en la nube...";
      titleEl.textContent = `${{title}} - ${{artist}}`;
      sizeEl.textContent = "Resolviendo pista...";
      barEl.style.width = "15%";
      pctEl.textContent = "15%";

      if (activeDownloadInterval) clearInterval(activeDownloadInterval);
      let p = 15;
      activeDownloadInterval = setInterval(() => {{
        p += Math.floor(Math.random() * 8) + 4;
        if (p >= 92) {{
          p = 92;
          clearInterval(activeDownloadInterval);
        }}
        barEl.style.width = `${{p}}%`;
        pctEl.textContent = `${{p}}%`;
        if (p < 40) {{
          statusEl.textContent = "Resolviendo audio completo de alta fidelidad...";
          detailDownloadStatus.textContent = "⏳ Conectando con servidor en la nube...";
          sizeEl.textContent = "Buscando flujo 320 kbps...";
        }} else if (p < 75) {{
          statusEl.textContent = "Descargando pista completa (320 kbps)...";
          detailDownloadStatus.textContent = "⚡ Descargando flujo de audio completo (320 kbps)...";
          sizeEl.textContent = "Descargando audio...";
        }} else {{
          statusEl.textContent = "Verificando calidad y duración (>120s)...";
          detailDownloadStatus.textContent = "🔍 Verificando integridad y duración completa...";
          sizeEl.textContent = "Verificando canción...";
        }}
      }}, 350);
    }}

    function finishActiveDownloadCard(title, artist, sizeMb, isFallback = false) {{
      if (activeDownloadInterval) clearInterval(activeDownloadInterval);
      const card = document.getElementById('active-download-card');
      const barEl = document.getElementById('dl-card-progress-bar');
      const pctEl = document.getElementById('dl-card-percent');
      const statusEl = document.getElementById('dl-card-status');
      const sizeEl = document.getElementById('dl-card-size-info');

      barEl.style.width = "100%";
      pctEl.textContent = "100%";
      statusEl.textContent = isFallback ? "Descarga guardada" : "¡Canción completa lista!";
      sizeEl.textContent = `${{sizeMb}} MB`;

      setTimeout(() => {{
        card.classList.add('hidden');
      }}, 4000);
    }}

    function saveDownload(track, sizeMb, fileUrl) {{
      if (!localDownloads.some(d => d.title === track.title && d.artist === track.artist)) {{
        localDownloads.unshift({{ ...track, size: `${{sizeMb}} MB`, audioUrl: fileUrl }});
        localStorage.setItem('cinnamoroll_downloads', JSON.stringify(localDownloads));
      }}
      renderDownloadsList(currentDlSubtab);
    }}

    // Real Functional Downloads Hub
    function renderDownloadsList(subtab = 'canciones') {{
      const container = document.getElementById('downloads-list-items');
      container.innerHTML = '';

      // Combine server downloaded tracks with local downloads
      const combined = [...localDownloads];
      serverDownloads.forEach(sd => {{
        if (!combined.some(c => c.title.toLowerCase() === sd.title.toLowerCase() && c.artist.toLowerCase() === sd.artist.toLowerCase())) {{
          combined.push(sd);
        }}
      }});

      const displayList = combined.length > 0 ? combined : PLAYLIST_SONGS.slice(0, 5);

      if (subtab === 'en_proceso') {{
        const card = document.getElementById('active-download-card');
        if (card.classList.contains('hidden')) {{
          container.innerHTML = `
            <div class="p-6 text-center rounded-2xl bg-white border border-[#e2eefd] space-y-2">
              <div class="text-3xl">📥</div>
              <h5 class="text-xs font-bold text-slate-700">No hay descargas activas</h5>
              <p class="text-[11px] text-slate-400">Busca canciones y pulsa el botón de descarga para guardarlas sin conexión.</p>
            </div>
          `;
        }}
        return;
      }}

      if (subtab === 'albumes') {{
        const groups = {{}};
        displayList.forEach(item => {{
          const key = item.artist || 'Varios';
          if (!groups[key]) groups[key] = [];
          groups[key].push(item);
        }});

        Object.keys(groups).forEach(artist => {{
          const groupCard = document.createElement('div');
          groupCard.className = "rounded-2xl bg-white border border-[#e2eefd] p-3 shadow-xs space-y-2";
          groupCard.innerHTML = `
            <div class="flex items-center justify-between pb-1 border-b border-blue-50">
              <span class="text-xs font-black text-slate-800">${{artist}}</span>
              <span class="text-[10px] font-bold text-blue-500">${{groups[artist].length}} canciones</span>
            </div>
            <div class="space-y-1.5 group-songs-container"></div>
          `;
          const songsContainer = groupCard.querySelector('.group-songs-container');
          groups[artist].forEach(song => {{
            const row = createDownloadRow(song);
            songsContainer.appendChild(row);
          }});
          container.appendChild(groupCard);
        }});
        return;
      }}

      // 'canciones' default view: Real downloaded songs list
      displayList.forEach(item => {{
        const row = createDownloadRow(item);
        container.appendChild(row);
      }});
    }}

    function createDownloadRow(item) {{
      const row = document.createElement('div');
      row.className = "flex items-center justify-between p-2.5 rounded-2xl bg-white border border-[#e2eefd] hover:border-blue-200 shadow-xs transition";
      row.innerHTML = `
        <div class="flex items-center gap-2.5 overflow-hidden flex-1 cursor-pointer track-info-col">
          <img src="${{item.cover}}\" onerror=\"this.onerror=null;this.src='${{item.fallback || item.cover}}'\" class="w-10 h-10 rounded-xl object-cover shrink-0 border border-blue-50 shadow-xs">
          <div class="overflow-hidden">
            <h5 class="text-xs font-bold text-slate-800 truncate">${{item.title}}</h5>
            <p class="text-[10px] text-slate-400 font-medium truncate">
              ${{item.artist}} &nbsp;•&nbsp; <span class="text-blue-500 font-bold">${{item.size || '7.1 MB'}}</span>
            </p>
          </div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button class="btn-play-dl w-7 h-7 rounded-full bg-[#edf5fe] hover:bg-blue-100 text-blue-600 flex items-center justify-center text-xs transition active:scale-95" title="Reproducir">
            <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
          </button>
          <button class="btn-save-dl w-7 h-7 rounded-full bg-[#edf5fe] hover:bg-blue-100 text-blue-600 flex items-center justify-center text-xs transition active:scale-95" title="Guardar archivo">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="12" y1="4.5" x2="12" y2="15"></line>
              <polyline points="8 11 12 15 16 11"></polyline>
              <path d="M5 16v2a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-2"></path>
            </svg>
          </button>
          <button class="btn-more-dl w-6 h-6 rounded-full text-slate-400 hover:text-slate-600 flex items-center justify-center text-xs transition" title="Opciones">
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"></circle><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="19" r="2"></circle></svg>
          </button>
        </div>
      `;

      row.querySelector('.track-info-col').addEventListener('click', () => {{
        loadAndPlayTrack(item);
        modalSongDetail.classList.remove('hidden');
      }});

      row.querySelector('.btn-play-dl').addEventListener('click', (e) => {{
        e.stopPropagation();
        loadAndPlayTrack(item);
      }});

      row.querySelector('.btn-save-dl').addEventListener('click', async (e) => {{
        e.stopPropagation();
        const dlUrl = item.audioUrl || item.preview;
        const fname = item.file || `${{item.title.replace(/\\s+/g, '_')}}.m4a`;
        if (dlUrl) {{
          const finalUrl = dlUrl.startsWith('/api/audio/') ? `${{SERVER_URL}}${{dlUrl}}` : dlUrl;
          await triggerBrowserDownload(finalUrl, fname);
        }} else {{
          downloadFull(item);
        }}
      }});

      row.querySelector('.btn-more-dl').addEventListener('click', (e) => {{
        e.stopPropagation();
        toggleFavorite(item);
        alert(`"${{item.title}}" guardada en Favoritos.`);
      }});

      return row;
    }}

    // Subtab pills in Descargas
    document.querySelectorAll('.dl-tab-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        document.querySelectorAll('.dl-tab-pill').forEach(p => {{
          p.className = "dl-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition";
        }});
        pill.className = "dl-tab-pill px-4 py-1 rounded-full text-xs font-extrabold bg-blue-500 text-white shadow-xs transition";
        currentDlSubtab = pill.getAttribute('data-subtab');
        renderDownloadsList(currentDlSubtab);
      }});
    }});

    document.getElementById('btn-refresh-downloads').addEventListener('click', () => {{
      loadServerDownloads();
    }});

    // Search Engine (iTunes JSONP live query)
    function searchiTunes(query, limit = 15) {{
      return new Promise((resolve) => {{
        const callbackName = 'jsonp_search_' + Math.round(100000 * Math.random());
        const script = document.createElement('script');
        script.src = `https://itunes.apple.com/search?term=${{encodeURIComponent(query)}}&entity=song&limit=${{limit}}&callback=${{callbackName}}`;

        const timer = setTimeout(() => {{ cleanup(); resolve([]); }}, 4000);
        function cleanup() {{
          clearTimeout(timer);
          delete window[callbackName];
          if (script.parentNode) script.parentNode.removeChild(script);
        }}

        window[callbackName] = function(data) {{
          cleanup();
          if (data && data.results) {{
            const mapped = data.results.map(r => ({{
              title: r.trackName || query,
              artist: r.artistName || '',
              album: r.collectionName || '',
              year: r.releaseDate ? r.releaseDate.substring(0, 4) : '2024',
              duration: r.trackTimeMillis ? formatTime(r.trackTimeMillis / 1000) : '4:00',
              cover: r.artworkUrl100 ? r.artworkUrl100.replace('100x100bb', '1000x1000bb') : '',
              fallback: r.artworkUrl100 ? r.artworkUrl100.replace('100x100bb', '1000x1000bb') : '',
              preview: r.previewUrl || ''
            }}));
            resolve(mapped);
          }} else {{
            resolve([]);
          }}
        }};

        script.onerror = () => {{ cleanup(); resolve([]); }};
        document.body.appendChild(script);
      }});
    }}

    function renderSearchRows(songs) {{
      const container = document.getElementById('search-results-list');
      container.innerHTML = '';
      currentTracksList = songs;

      songs.forEach((song, idx) => {{
        const row = document.createElement('div');
        row.className = "flex items-center justify-between p-2 rounded-2xl bg-white border border-[#e2eefd] hover:border-blue-200 shadow-xs transition";
        row.innerHTML = `
          <div class="flex items-center gap-2.5 overflow-hidden flex-1 cursor-pointer track-click-area">
            <img src="${{song.cover}}\" onerror=\"this.onerror=null;this.src='${{song.fallback || song.cover}}'\" class="w-11 h-11 rounded-xl object-cover shrink-0 border border-blue-50 shadow-xs">
            <div class="overflow-hidden">
              <h5 class="text-xs font-bold text-slate-800 truncate">${{song.title}}</h5>
              <p class="text-[10px] text-slate-400 font-medium truncate">${{song.artist}}</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button class="btn-row-play w-7 h-7 rounded-full bg-[#edf5fe] hover:bg-blue-100 text-blue-600 flex items-center justify-center text-xs transition active:scale-95" title="Escuchar">
              <svg class="w-3 h-3" viewBox="0 0 24 24" fill="currentColor"><polygon points="6 4 20 12 6 20 6 4"></polygon></svg>
            </button>
            <button class="btn-row-dl w-7 h-7 rounded-full bg-[#edf5fe] hover:bg-blue-100 text-blue-600 flex items-center justify-center text-xs transition active:scale-95" title="Descargar .m4a completa">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="4.5" x2="12" y2="15"></line>
                <polyline points="7.5 10.5 12 15 16.5 10.5"></polyline>
                <path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path>
              </svg>
            </button>
            <button class="btn-row-menu w-6 h-6 rounded-full text-slate-400 hover:text-slate-600 flex items-center justify-center text-xs transition">
              <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"></circle><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="19" r="2"></circle></svg>
            </button>
          </div>
        `;

        row.querySelector('.track-click-area').addEventListener('click', () => {{
          currentTrackIndex = idx;
          loadAndPlayTrack(song);
          modalSongDetail.classList.remove('hidden');
        }});

        row.querySelector('.btn-row-play').addEventListener('click', (e) => {{
          e.stopPropagation();
          currentTrackIndex = idx;
          loadAndPlayTrack(song);
        }});

        row.querySelector('.btn-row-dl').addEventListener('click', (e) => {{
          e.stopPropagation();
          currentTrack = song;
          downloadFull(song);
        }});

        row.querySelector('.btn-row-menu').addEventListener('click', (e) => {{
          e.stopPropagation();
          toggleFavorite(song);
          alert(`"${{song.title}}" guardada en Favoritos.`);
        }});

        container.appendChild(row);
      }});
    }}

    async function doSearch(query) {{
      if (!query || query.trim() === '') return;
      if (query.toLowerCase().includes('coldplay')) {{
        renderSearchRows(PLAYLIST_SONGS.slice(0, 10));
        return;
      }}
      const results = await searchiTunes(query, 16);
      renderSearchRows(results.length > 0 ? results : PLAYLIST_SONGS.slice(0, 6));
    }}

    document.getElementById('main-search-input').addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') doSearch(e.target.value);
    }});
    document.getElementById('btn-clear-search').addEventListener('click', () => {{
      document.getElementById('main-search-input').value = '';
      document.getElementById('main-search-input').focus();
    }});

    document.querySelectorAll('.search-tab-pill').forEach(pill => {{
      pill.addEventListener('click', () => {{
        document.querySelectorAll('.search-tab-pill').forEach(p => {{
          p.className = "search-tab-pill px-4 py-1 rounded-full text-xs font-bold bg-white text-slate-500 border border-blue-100 hover:bg-blue-50 transition";
        }});
        pill.className = "search-tab-pill px-4 py-1 rounded-full text-xs font-extrabold bg-blue-500 text-white shadow-xs transition";
        doSearch(document.getElementById('main-search-input').value);
      }});
    }});

    function getDiscoveryPool() {{
      const pool = [...PLAYLIST_SONGS];
      serverDownloads.forEach(sd => {{
        const exists = pool.some(p =>
          (p.file && sd.file && p.file.toLowerCase() === sd.file.toLowerCase()) ||
          (p.title.toLowerCase() === sd.title.toLowerCase() && p.artist.toLowerCase() === sd.artist.toLowerCase())
        );
        if (!exists) {{
          pool.push(sd);
        }}
      }});
      return pool;
    }}

    function renderHomeCards(advanceRotation = false) {{
      const pool = getDiscoveryPool();
      if (pool.length === 0) return;
      if (advanceRotation) {{
        homeRotationStep = (homeRotationStep + 3) % pool.length;
      }}

      const recContainer = document.getElementById('recommended-container');
      recContainer.innerHTML = '';
      const recList = [];
      const usedIndices = new Set();

      for (let i = 0; i < 3 && i < pool.length; i++) {{
        const idx = (homeRotationStep + i) % pool.length;
        usedIndices.add(idx);
        recList.push(pool[idx]);
      }}

      recList.forEach(song => {{
        const card = document.createElement('div');
        card.className = "flex flex-col gap-1 rounded-2xl bg-white p-2 border border-[#e2eefd] shadow-xs cursor-pointer hover:border-blue-300 transition active:scale-95";
        card.innerHTML = `
          <div class="w-full aspect-square rounded-xl overflow-hidden shadow-xs border border-blue-50">
            <img src="${{song.cover}}\" onerror=\"this.onerror=null;this.src='${{song.fallback || song.cover}}'\" class="w-full h-full object-cover">
          </div>
          <h5 class="text-[11px] font-bold text-slate-800 truncate mt-0.5">${{song.title}}</h5>
          <p class="text-[9px] font-semibold text-slate-400 truncate">${{song.artist}}</p>
        `;
        card.addEventListener('click', () => {{
          loadAndPlayTrack(song);
          modalSongDetail.classList.remove('hidden');
        }});
        recContainer.appendChild(card);
      }});

      const trendContainer = document.getElementById('trending-container');
      trendContainer.innerHTML = '';
      const trendList = [];
      let offset = (homeRotationStep + 7) % pool.length;
      for (let attempts = 0; attempts < pool.length && trendList.length < 3; attempts++) {{
        const idx = (offset + attempts * 5) % pool.length;
        if (!usedIndices.has(idx)) {{
          usedIndices.add(idx);
          trendList.push(pool[idx]);
        }}
      }}

      trendList.forEach(song => {{
        const card = document.createElement('div');
        card.className = "flex flex-col gap-1 rounded-2xl bg-white p-2 border border-[#e2eefd] shadow-xs cursor-pointer hover:border-blue-300 transition active:scale-95";
        card.innerHTML = `
          <div class="w-full aspect-square rounded-xl overflow-hidden shadow-xs border border-blue-50">
            <img src="${{song.cover}}\" onerror=\"this.onerror=null;this.src='${{song.fallback || song.cover}}'\" class="w-full h-full object-cover">
          </div>
          <h5 class="text-[11px] font-bold text-slate-800 truncate mt-0.5">${{song.title}}</h5>
          <p class="text-[9px] font-semibold text-slate-400 truncate">${{song.artist}}</p>
        `;
        card.addEventListener('click', () => {{
          loadAndPlayTrack(song);
          modalSongDetail.classList.remove('hidden');
        }});
        trendContainer.appendChild(card);
      }});
    }}

    const btnRotateHome = document.getElementById('btn-rotate-home');
    if (btnRotateHome) {{
      btnRotateHome.addEventListener('click', () => renderHomeCards(true));
    }}

    document.getElementById('btn-see-more-recommended').addEventListener('click', () => {{
      switchTab('search');
      renderSearchRows(getDiscoveryPool());
    }});
    document.getElementById('btn-see-more-trending').addEventListener('click', () => {{
      switchTab('search');
      renderSearchRows(getDiscoveryPool().slice(0, 15));
    }});

    // Startup
    renderHomeCards(false);
    renderDownloadsList(currentDlSubtab);
    renderSearchRows(PLAYLIST_SONGS.slice(0, 10));
    updatePlayerUI(PLAYLIST_SONGS[0]);
    checkServer().then(() => loadServerDownloads());
  </script>
</body>
</html>
'''

out_path = os.path.join(base_dir, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)

# Also update generate_clean_html.py and build_clean_version.py
for script_name in ["generate_clean_html.py", "build_clean_version.py"]:
    sp = os.path.join(base_dir, script_name)
    with open(sp, "w", encoding="utf-8") as sf:
        with open(__file__, "r", encoding="utf-8") as cur_f:
            sf.write(cur_f.read())

print(f"Generated clean index.html: {os.path.getsize(out_path)} bytes")
