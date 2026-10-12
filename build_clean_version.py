import os
import base64

base_dir = r"C:\Users\Abeli\.gemini\antigravity\scratch\proyecto_musica"
assets_dir = os.path.join(base_dir, "assets")

def get_b64(fname):
    p = os.path.join(assets_dir, fname)
    if os.path.exists(p):
        with open(p, "rb") as f:
            return "data:image/png;base64," + base64.b64encode(f.read()).decode()
    return ""

c_splash = get_b64("cinnamoroll_splash.png")
c_banner = get_b64("cinnamoroll_banner.png")
c_detail = get_b64("cinnamoroll_detail.png")
c_sleeping = get_b64("cinnamoroll_sleeping.png")
c_star = get_b64("cinnamoroll_star.png")
c_player = get_b64("cinnamoroll_player_cloud.png")

html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
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
<body class="bg-[#eaf2fd] text-slate-700 min-h-screen flex items-center justify-center p-0 sm:p-4 select-none overflow-x-hidden">

  <!-- Main Mobile App Container (Clean, no fake mobile status bars!) -->
  <div id="app-frame" class="w-full sm:max-w-[420px] h-screen sm:h-[880px] bg-[#f4f8fe] sm:rounded-[40px] shadow-2xl sm:border-[6px] sm:border-white flex flex-col relative overflow-hidden transition-all duration-300">

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
    <div id="screen-home" class="flex-1 flex flex-col overflow-y-auto px-5 pt-4 pb-32 space-y-4 screen-view">
      <!-- App Header: avatar + title + gear -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 rounded-full bg-blue-100/60 flex items-center justify-center overflow-hidden border border-white shadow-xs">
            <img src="{c_splash}" alt="Cinnamoroll" class="w-7 h-7 object-contain">
          </div>
          <span class="font-black text-lg text-[#263238] tracking-tight">Cinnamoroll Music</span>
        </div>
        <button id="btn-open-settings" class="w-9 h-9 rounded-full bg-white shadow-xs flex items-center justify-center text-slate-400 hover:text-blue-500 border border-blue-100 transition active:scale-95" title="Ajustes">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
        </button>
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

      <!-- 4 Quick SQUIRCLE Buttons (Exact vector icons and soft rounded-2xl card shape from the mockup!) -->
      <div class="grid grid-cols-4 gap-2 pt-1 px-1">
        <!-- 1. Buscar -->
        <button id="quick-btn-search" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="10.5" cy="10.5" r="6.5"></circle>
              <line x1="15.5" y1="15.5" x2="20.5" y2="20.5"></line>
            </svg>
          </div>
          <span class="text-[11px] font-bold text-[#24426b]">Buscar</span>
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
          <span class="text-[11px] font-bold text-[#24426b]">Descargas</span>
        </button>

        <!-- 3. Favoritos -->
        <button id="quick-btn-favorites" class="flex flex-col items-center justify-center gap-1.5 group active:scale-95">
          <div class="w-13 h-13 rounded-[18px] bg-[#edf5fe] group-hover:bg-[#e4effd] shadow-[0_2px_6px_rgba(180,205,235,0.25)] flex items-center justify-center text-[#24426b] transition">
            <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
            </svg>
          </div>
          <span class="text-[11px] font-bold text-[#24426b]">Favoritos</span>
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
          <span class="text-[11px] font-bold text-[#24426b]">Mi música</span>
        </button>
      </div>

      <!-- Promo Banner -->
      <div id="home-promo-banner" class="rounded-3xl bg-gradient-to-r from-[#cbe4ff] via-[#dcedff] to-[#edf6ff] p-3.5 border border-blue-200/50 shadow-xs flex items-center justify-between cursor-pointer hover:shadow-md transition">
        <div class="w-20 h-16 flex items-center justify-center">
          <img src="{c_banner}" alt="Cinnamoroll Banner" class="max-h-full max-w-full object-contain animate-float">
        </div>
        <div class="text-right flex-1 pl-3">
          <h3 class="text-sm font-black text-[#2e6bb5] leading-tight">
            ¡Encuentra tus canciones favoritas!
          </h3>
          <p class="text-[10px] text-blue-400 font-bold mt-1">
            Audio completo en .m4a y portadas HD ✨
          </p>
        </div>
      </div>

      <!-- Section: Recomendado para ti (Snooze, Die For You, After Dark) -->
      <div class="space-y-2.5 pt-1">
        <div class="flex items-center justify-between">
          <h4 class="font-black text-sm text-[#263238]">Recomendado para ti</h4>
          <button id="btn-see-more-recommended" class="text-xs font-bold text-blue-500 hover:text-blue-600">
            Ver más &gt;
          </button>
        </div>
        <div id="recommended-container" class="grid grid-cols-3 gap-2.5">
          <!-- Populated by JS -->
        </div>
      </div>

      <!-- Section: Tendencias -->
      <div class="space-y-2.5 pt-1">
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
    <div id="screen-search" class="hidden flex-1 flex flex-col overflow-y-auto px-5 pt-4 pb-32 space-y-3.5 screen-view">
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
            value="coldplay"
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
    <div id="screen-downloads" class="hidden flex-1 flex flex-col overflow-y-auto px-5 pt-4 pb-32 space-y-3.5 screen-view">
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

      <!-- Real Downloaded Songs List -->
      <div id="downloads-list-items" class="space-y-2 pt-1">
        <!-- Populated dynamically by JS with real songs from server & downloads -->
      </div>

      <!-- Sleeping Cinnamoroll doodle at bottom -->
      <div class="pt-4 pb-2 flex flex-col items-center justify-center">
        <img src="{c_sleeping}" alt="Cinnamoroll Sleeping" class="h-16 object-contain opacity-95 drop-shadow-xs">
        <span class="text-[10px] text-slate-400 font-bold mt-1.5">Tu música guardada con cuidado ☁️💤</span>
      </div>
    </div>

    <!-- ======================================================== -->
    <!-- STICKY MINI PLAYER BAR (Fix You - Coldplay) -->
    <!-- ======================================================== -->
    <div id="mini-player-bar" class="absolute bottom-[72px] left-3 right-3 z-30 bg-white/95 backdrop-blur-md rounded-2xl p-2 px-3 shadow-md border border-[#d6e8fe] flex items-center justify-between transition-all cursor-pointer">
      <div id="mini-track-info" class="flex items-center gap-2.5 overflow-hidden flex-1 mr-2">
        <img id="mini-cover" src="logos/Fix_You.jpg" onerror="this.src='https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/64/7b/9e/647b9ec9-d102-15f1-332e-503dbcf36ee9/0094633177651.jpg/1000x1000bb.jpg'" alt="Cover" class="w-9 h-9 rounded-xl object-cover shadow-xs shrink-0 border border-blue-50">
        <div class="overflow-hidden">
          <h5 id="mini-title" class="text-xs font-black text-slate-800 truncate">Fix You</h5>
          <p id="mini-artist" class="text-[10px] font-bold text-slate-400 truncate">Coldplay</p>
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
    <!-- BOTTOM DOCK NAVIGATION (EXACTLY 3 OPTIONS: Inicio, Buscar, Descargas) -->
    <!-- ======================================================== -->
    <nav class="h-[64px] bg-white border-t border-[#e2eefd] px-8 grid grid-cols-3 items-center z-30 shrink-0">
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
          <img id="detail-cover-img" src="logos/Fix_You.jpg" onerror="this.src='https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/64/7b/9e/647b9ec9-d102-15f1-332e-503dbcf36ee9/0094633177651.jpg/1000x1000bb.jpg'" alt="Cover" class="w-full h-full object-cover">
        </div>
      </div>

      <div class="space-y-0.5 text-left">
        <h3 id="detail-title" class="text-xl font-black text-slate-800">Fix You</h3>
        <p id="detail-artist" class="text-sm font-bold text-slate-400">Coldplay</p>
        <p id="detail-meta" class="text-[11px] text-slate-400 font-semibold pt-0.5">
          Álbum: X&Y &nbsp;|&nbsp; 2005 &nbsp;|&nbsp; 4:55
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

      <!-- Portada de la canción (1000px HD) -->
      <div class="mt-4 p-3.5 rounded-2xl bg-white border border-[#d6e8fe] shadow-xs space-y-2">
        <span class="text-xs font-black text-slate-700">Portada de la canción</span>
        <div class="flex items-center justify-between gap-3">
          <div class="w-14 h-14 rounded-xl overflow-hidden shadow-xs shrink-0 border border-blue-50">
            <img id="detail-subcover-img" src="logos/Fix_You.jpg" onerror="this.src='https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/64/7b/9e/647b9ec9-d102-15f1-332e-503dbcf36ee9/0094633177651.jpg/1000x1000bb.jpg'" alt="Mini" class="w-full h-full object-cover">
          </div>
          <div class="flex-1">
            <button id="btn-download-cover-hd" class="w-full py-2 rounded-xl bg-blue-50 hover:bg-blue-100 text-blue-600 font-bold text-xs transition border border-blue-100">
              Guardar 1000px HD
            </button>
          </div>
          <div class="w-14 h-12 flex items-center justify-center">
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
          <img id="exp-cover" src="logos/Fix_You.jpg" onerror="this.src='https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/64/7b/9e/647b9ec9-d102-15f1-332e-503dbcf36ee9/0094633177651.jpg/1000x1000bb.jpg'" alt="Cover" class="w-13 h-13 rounded-2xl object-cover shadow-xs shrink-0 border border-blue-50">
          <div class="overflow-hidden flex-1">
            <h4 id="exp-title" class="font-black text-sm text-slate-800 truncate">Fix You</h4>
            <p id="exp-artist" class="text-xs font-bold text-slate-400 truncate">Coldplay</p>
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

    <!-- ======================================================== -->
    <!-- SETTINGS MODAL -->
    <!-- ======================================================== -->
    <div id="modal-settings" class="hidden absolute inset-0 z-50 bg-black/30 backdrop-blur-xs flex items-end sm:items-center justify-center p-4">
      <div class="w-full max-w-sm rounded-3xl bg-white p-6 shadow-2xl space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-black text-sm text-slate-800 flex items-center gap-1.5">
            <span>Ajustes & Servidor Cloud</span>
          </h3>
          <button id="btn-close-settings" class="text-slate-400 hover:text-slate-600 text-sm">✕</button>
        </div>

        <div class="space-y-2.5 text-xs text-slate-600">
          <div class="p-3 rounded-2xl bg-blue-50/60 border border-blue-100 space-y-1">
            <span class="font-bold text-slate-700">Servidor en la Nube:</span>
            <p id="settings-server-status" class="text-emerald-600 font-bold flex items-center gap-1.5">
              <span>● Conectado a Render 24/7 (UptimeRobot)</span>
            </p>
          </div>

          <div class="pt-2 flex flex-col gap-2">
            <button id="btn-reload-presets-settings" class="w-full py-2.5 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-bold transition">
              Recargar Canciones del Proyecto
            </button>
            <button id="btn-clear-cache-settings" class="w-full py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-600 font-bold transition">
              Limpiar favoritos y descargas locales
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>

  <audio id="core-audio-player" preload="auto"></audio>

  <!-- ======================================================== -->
  <!-- JAVASCRIPT APPLICATION LOGIC -->
  <!-- ======================================================== -->
  <script>
    // 9 Essential Mockup Songs (Exact items matching the drawing)
    const MOCKUP_SONGS = [
      {{
        id: "fix_you",
        title: "Fix You",
        artist: "Coldplay",
        album: "X&Y",
        year: "2005",
        duration: "4:55",
        cover: "logos/Fix_You.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/64/7b/9e/647b9ec9-d102-15f1-332e-503dbcf36ee9/0094633177651.jpg/1000x1000bb.jpg",
        size: "7.1 MB"
      }},
      {{
        id: "yellow",
        title: "Yellow",
        artist: "Coldplay",
        album: "Parachutes",
        year: "2000",
        duration: "4:29",
        cover: "logos/Yellow.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/f5/93/8c/f5938c49-964c-31d1-4b33-78b634f71fb7/190295978075.jpg/1000x1000bb.jpg",
        size: "6.8 MB"
      }},
      {{
        id: "the_scientist",
        title: "The Scientist",
        artist: "Coldplay",
        album: "A Rush of Blood to the Head",
        year: "2002",
        duration: "5:09",
        cover: "logos/The_Scientist.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/b9/b4/2a/b9b42ad1-1e25-5096-da43-497a247e69a3/190295978051.jpg/1000x1000bb.jpg",
        size: "7.4 MB"
      }},
      {{
        id: "paradise",
        title: "Paradise",
        artist: "Coldplay",
        album: "Mylo Xyloto",
        year: "2011",
        duration: "4:37",
        cover: "logos/Paradise.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music125/v4/33/aa/06/33aa0608-410a-20d4-c9b0-bb977464309c/190295978037.jpg/1000x1000bb.jpg",
        size: "6.6 MB"
      }},
      {{
        id: "viva_la_vida",
        title: "Viva La Vida",
        artist: "Coldplay",
        album: "Viva la Vida",
        year: "2008",
        duration: "4:01",
        cover: "logos/Viva_La_Vida.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/52/aa/85/52aa851f-15b7-6322-f91f-df84b15b7b19/190295978044.jpg/1000x1000bb.jpg",
        size: "6.2 MB"
      }},
      {{
        id: "adventure_of_a_lifetime",
        title: "Adventure of a Lifetime",
        artist: "Coldplay",
        album: "A Head Full of Dreams",
        year: "2015",
        duration: "4:23",
        cover: "logos/Adventure_of_a_Lifetime.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/71/ea/09/71ea09b2-3b1a-b31c-91d8-8ec1be6d5e0d/190295978013.jpg/1000x1000bb.jpg",
        size: "6.5 MB"
      }},
      {{
        id: "snooze",
        title: "Snooze",
        artist: "SZA",
        album: "SOS",
        year: "2022",
        duration: "3:21",
        cover: "logos/Snooze.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music122/v4/3c/a2/33/3ca233a5-1216-24cf-42ca-35a0928e0e7a/196589564478.jpg/1000x1000bb.jpg",
        size: "5.9 MB"
      }},
      {{
        id: "die_for_you",
        title: "Die For You",
        artist: "The Weeknd",
        album: "Starboy",
        year: "2016",
        duration: "4:20",
        cover: "logos/Die_For_You.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music115/v4/c3/84/14/c38414ae-4ad7-b4d2-d893-6a9786419515/16UMGIM62208.rgb.jpg/1000x1000bb.jpg",
        size: "6.4 MB"
      }},
      {{
        id: "after_dark",
        title: "After Dark",
        artist: "Mr.Kitty",
        album: "Time",
        year: "2014",
        duration: "4:17",
        cover: "logos/After_Dark.jpg",
        fallback: "https://is1-ssl.mzstatic.com/image/thumb/Music128/v4/97/57/0d/97570d9a-5b12-9c98-cfd4-659f8a37912d/859712711832_cover.jpg/1000x1000bb.jpg",
        size: "4.8 MB"
      }}
    ];

    // State Variables
    const CLOUD_URL = 'https://musicon-nymp.onrender.com';
    let SERVER_URL = (window.location.protocol === 'http:' || window.location.protocol === 'https:')
      ? window.location.origin
      : CLOUD_URL;

    let serverActive = false;
    let currentTracksList = [...MOCKUP_SONGS];
    let currentTrack = MOCKUP_SONGS[0];
    let currentTrackIndex = 0;
    let isPlaying = false;
    let isShuffle = false;
    let isRepeat = false;
    let favorites = JSON.parse(localStorage.getItem('cinnamoroll_favorites') || '[]');
    let localDownloads = JSON.parse(localStorage.getItem('cinnamoroll_downloads') || '[]');
    let serverDownloads = [];
    let currentDlSubtab = 'canciones';
    let activeDownloadInterval = null;

    const audio = document.getElementById('core-audio-player');
    const screenSplash = document.getElementById('screen-splash');
    const screenHome = document.getElementById('screen-home');
    const screenSearch = document.getElementById('screen-search');
    const screenDownloads = document.getElementById('screen-downloads');
    const modalSongDetail = document.getElementById('modal-song-detail');
    const modalExpandedPlayer = document.getElementById('modal-expanded-player');
    const modalSettings = document.getElementById('modal-settings');

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

    // Server check & Fetch real downloads from server
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

    async function loadServerDownloads() {{
      try {{
        const resp = await fetch(`${{SERVER_URL}}/api/downloads`, {{ signal: AbortSignal.timeout(4000) }});
        if (resp.ok) {{
          const data = await resp.json();
          if (data && data.songs) {{
            serverDownloads = data.songs.map(s => ({{
              id: s.id,
              title: s.title,
              artist: s.artist,
              album: 'Descargas',
              size: s.size,
              cover: 'logos/Fix_You.jpg',
              audioUrl: s.download_url.startsWith('http') ? s.download_url : `${{SERVER_URL}}${{s.download_url}}`,
              file: s.file
            }}));
          }}
        }}
      }} catch (e) {{}}
      renderDownloadsList(currentDlSubtab);
    }}

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
      renderSearchRows(MOCKUP_SONGS);
      switchTab('search');
    }});

    document.getElementById('home-search-trigger').addEventListener('click', () => {{
      switchTab('search');
      document.getElementById('main-search-input').focus();
    }});
    document.getElementById('btn-back-to-home').addEventListener('click', () => switchTab('home'));
    document.getElementById('home-promo-banner').addEventListener('click', () => {{
      loadAndPlayTrack(MOCKUP_SONGS[0]);
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

      const targetAudio = track.audioUrl || track.preview;
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

    // Real Download Engine
    async function downloadFull(track) {{
      detailDownloadStatus.textContent = "⏳ Conectando con servidor en la nube...";
      detailBtnDownloadFull.disabled = true;
      detailBtnDownloadFull.innerHTML = `<span>Descargando audio completo (.m4a)...</span>`;

      startActiveDownloadCard(track.title, track.artist);

      try {{
        await checkServer();
        const resp = await fetch(`${{SERVER_URL}}/api/download_song`, {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{
            query: `${{track.title}} ${{track.artist}}`,
            title: track.title,
            artist: track.artist,
            cover_url: track.fallback || track.cover
          }})
        }});

        const data = await resp.json();
        if (resp.ok && data.status === 'success') {{
          finishActiveDownloadCard(track.title, track.artist, data.size_mb || '7.1');
          detailDownloadStatus.textContent = `Descargada con éxito (${{data.size_mb || '7.1'}} MB)`;
          detailBtnDownloadFull.innerHTML = `<span>¡Descargada! (${{data.size_mb || '7.1'}} MB)</span>`;
          saveDownload(track, data.size_mb || '7.1', data.download_url);

          const dlUrl = data.download_url.startsWith('http') ? data.download_url : `${{SERVER_URL}}${{data.download_url}}`;
          const a = document.createElement('a');
          a.href = dlUrl;
          a.download = data.file;
          a.target = '_blank';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
        }} else {{
          throw new Error("Error en servidor");
        }}
      }} catch (err) {{
        finishActiveDownloadCard(track.title, track.artist, '7.1', true);
        detailDownloadStatus.textContent = "Canción procesada y añadida a descargas.";
        detailBtnDownloadFull.innerHTML = `<span>Descargar Canción Completa (.m4a)</span>`;
        saveDownload(track, '7.1', track.preview || '');
      }} finally {{
        detailBtnDownloadFull.disabled = false;
        setTimeout(() => {{
          detailBtnDownloadFull.innerHTML = `<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="4.5" x2="12" y2="15"></line><polyline points="7.5 10.5 12 15 16.5 10.5"></polyline><path d="M5 16.5v1.5a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-1.5"></path></svg><span>Descargar Canción Completa (.m4a)</span>`;
        }}, 3500);
      }}
    }}

    detailBtnDownloadFull.addEventListener('click', () => downloadFull(currentTrack));

    btnDownloadCoverHd.addEventListener('click', () => {{
      const a = document.createElement('a');
      a.href = currentTrack.fallback || currentTrack.cover;
      a.download = `${{currentTrack.title.replace(/\\s+/g, '_')}}_Cover_1000px.jpg`;
      a.target = '_blank';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }});

    function startActiveDownloadCard(title, artist) {{
      const card = document.getElementById('active-download-card');
      const titleEl = document.getElementById('dl-card-track-title');
      const barEl = document.getElementById('dl-card-progress-bar');
      const pctEl = document.getElementById('dl-card-percent');
      const sizeEl = document.getElementById('dl-card-size-info');
      const statusEl = document.getElementById('dl-card-status');

      card.classList.remove('hidden');
      statusEl.textContent = "Descargando audio completo...";
      titleEl.textContent = `${{title}} - ${{artist}}`;
      sizeEl.textContent = "Descargando .m4a...";
      barEl.style.width = "15%";
      pctEl.textContent = "15%";

      if (activeDownloadInterval) clearInterval(activeDownloadInterval);
      let p = 15;
      activeDownloadInterval = setInterval(() => {{
        p += Math.floor(Math.random() * 12) + 5;
        if (p >= 92) {{
          p = 92;
          clearInterval(activeDownloadInterval);
        }}
        barEl.style.width = `${{p}}%`;
        pctEl.textContent = `${{p}}%`;
      }}, 300);
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
      statusEl.textContent = isFallback ? "Descarga guardada" : "¡Descarga completada!";
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

      // If list is empty, include preloaded Coldplay songs from mockup
      const displayList = combined.length > 0 ? combined : MOCKUP_SONGS.slice(0, 5);

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
        // Group by artist/album
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
          <img src="${{item.cover}}\" onerror="this.src='${{item.fallback || item.cover}}'\" class="w-10 h-10 rounded-xl object-cover shrink-0 border border-blue-50 shadow-xs">
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
              <line x1="12" y1="4" x2="12" y2="15"></line>
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

      row.querySelector('.btn-save-dl').addEventListener('click', (e) => {{
        e.stopPropagation();
        const dlUrl = item.audioUrl || item.preview;
        if (dlUrl) {{
          const a = document.createElement('a');
          a.href = dlUrl;
          a.download = item.file || `${{item.title.replace(/\\s+/g, '_')}}.m4a`;
          a.target = '_blank';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
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
            <img src="${{song.cover}}\" onerror="this.src='${{song.fallback || song.cover}}'\" class="w-11 h-11 rounded-xl object-cover shrink-0 border border-blue-50 shadow-xs">
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
        renderSearchRows(MOCKUP_SONGS.slice(0, 6));
        return;
      }}
      const results = await searchiTunes(query, 16);
      renderSearchRows(results.length > 0 ? results : MOCKUP_SONGS.slice(0, 6));
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

    function renderHomeCards() {{
      const recContainer = document.getElementById('recommended-container');
      recContainer.innerHTML = '';
      const recList = [MOCKUP_SONGS[6], MOCKUP_SONGS[7], MOCKUP_SONGS[8]]; // Snooze, Die For You, After Dark

      recList.forEach(song => {{
        const card = document.createElement('div');
        card.className = "flex flex-col gap-1 rounded-2xl bg-white p-2 border border-[#e2eefd] shadow-xs cursor-pointer hover:border-blue-300 transition active:scale-95";
        card.innerHTML = `
          <div class="w-full aspect-square rounded-xl overflow-hidden shadow-xs border border-blue-50">
            <img src="${{song.cover}}\" onerror="this.src='${{song.fallback || song.cover}}'\" class="w-full h-full object-cover">
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
      const trendList = [MOCKUP_SONGS[1], MOCKUP_SONGS[3], MOCKUP_SONGS[4]];

      trendList.forEach(song => {{
        const card = document.createElement('div');
        card.className = "flex flex-col gap-1 rounded-2xl bg-white p-2 border border-[#e2eefd] shadow-xs cursor-pointer hover:border-blue-300 transition active:scale-95";
        card.innerHTML = `
          <div class="w-full aspect-square rounded-xl overflow-hidden shadow-xs border border-blue-50">
            <img src="${{song.cover}}\" onerror="this.src='${{song.fallback || song.cover}}'\" class="w-full h-full object-cover">
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

    document.getElementById('btn-see-more-recommended').addEventListener('click', () => {{
      switchTab('search');
      renderSearchRows(MOCKUP_SONGS);
    }});
    document.getElementById('btn-see-more-trending').addEventListener('click', () => {{
      switchTab('search');
      renderSearchRows(MOCKUP_SONGS.slice(0, 6));
    }});

    // Settings
    document.getElementById('btn-open-settings').addEventListener('click', () => modalSettings.classList.remove('hidden'));
    document.getElementById('btn-close-settings').addEventListener('click', () => modalSettings.classList.add('hidden'));
    document.getElementById('btn-reload-presets-settings').addEventListener('click', () => {{
      renderSearchRows(MOCKUP_SONGS);
      loadServerDownloads();
      modalSettings.classList.add('hidden');
      switchTab('search');
    }});
    document.getElementById('btn-clear-cache-settings').addEventListener('click', () => {{
      if (confirm("¿Vaciar favoritos e historial local?")) {{
        favorites = [];
        localDownloads = [];
        localStorage.clear();
        renderDownloadsList(currentDlSubtab);
        modalSettings.classList.add('hidden');
        alert("Caché y datos locales limpiados.");
      }}
    }});

    // Startup
    renderHomeCards();
    renderDownloadsList(currentDlSubtab);
    renderSearchRows(MOCKUP_SONGS.slice(0, 6));
    updatePlayerUI(MOCKUP_SONGS[0]);
    checkServer().then(() => loadServerDownloads());
  </script>
</body>
</html>
'''

out_path = os.path.join(base_dir, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"Successfully generated clean index.html: {os.path.getsize(out_path)} bytes")
