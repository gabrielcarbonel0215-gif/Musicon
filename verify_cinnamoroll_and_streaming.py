import os
import sys
import time

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

def verify_all():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "index.html")
    assert os.path.exists(index_path), "index.html does not exist!"
    file_url = f"file:///{index_path.replace(os.sep, '/')}"

    artifact_dir = r"C:\Users\Abeli\.gemini\antigravity\brain\7ea9ff39-7e52-41c9-a49e-872891088da8"

    viewports_to_test = [
        {"name": "Pixel_5", "width": 393, "height": 851},
        {"name": "Standard_Android", "width": 360, "height": 740},
        {"name": "Compact_Android", "width": 360, "height": 680},
    ]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for vp in viewports_to_test:
            print(f"\n==========================================")
            print(f"Testing Viewport: {vp['name']} ({vp['width']} x {vp['height']})")
            print(f"==========================================")
            context = browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                user_agent="Mozilla/5.0 (Linux; Android 13) Mobile Safari/537.36",
                has_touch=True
            )
            page = context.new_page()

            console_errors = []
            page.on("pageerror", lambda err: console_errors.append(f"PAGE ERROR: {err}"))

            page.goto(file_url, wait_until="networkidle")

            # Dismiss splash
            page.evaluate("""() => {
                const s = document.getElementById('screen-splash');
                if (s) { s.classList.add('hidden', 'opacity-0', 'pointer-events-none'); }
            }""")
            time.sleep(0.2)

            # Open #modal-song-detail
            page.locator("#mini-track-info").click()
            time.sleep(0.3)

            modal = page.locator("#modal-song-detail")
            assert modal.is_visible(), "Modal song detail did not open"

            cinna_container = page.locator("#detail-cinnamoroll-container")
            cinna_frame = page.locator("#cinnamoroll-active-frame")
            assert cinna_container.is_visible(), "Cinnamoroll container is not visible"
            assert cinna_frame.is_visible(), "Cinnamoroll active frame is not visible"

            c_box = cinna_container.bounding_box()
            f_box = cinna_frame.bounding_box()
            print(f"[{vp['name']}] Viewport Height: {vp['height']}px")
            print(f"[{vp['name']}] Cinnamoroll Container Box: y={c_box['y']:.1f}, h={c_box['height']:.1f}, bottom={c_box['y']+c_box['height']:.1f}px")
            print(f"[{vp['name']}] Cinnamoroll Sprite Box: y={f_box['y']:.1f}, h={f_box['height']:.1f}, bottom={f_box['y']+f_box['height']:.1f}px")

            # Verify that the sprite and container bottom is within viewport height (or max +5px safe inset)
            is_sprite_fully_visible = (f_box['y'] + f_box['height']) <= vp['height']
            print(f"[{vp['name']}] Cinnamoroll Sprite fully visible without scroll: {is_sprite_fully_visible}")
            assert is_sprite_fully_visible, f"Cinnamoroll sprite bottom ({f_box['y'] + f_box['height']}) exceeds viewport height ({vp['height']})!"

            # Take high quality screenshot
            shot_path = os.path.join(artifact_dir, f"cinna_detail_{vp['name'].lower()}.png")
            page.screenshot(path=shot_path)
            print(f"[{vp['name']}] Saved verification screenshot to: {shot_path}")
            context.close()

        # Functional Test: Smart Audio Resolver
        print(f"\n==========================================")
        print("Testing Smart Audio Resolver Engine")
        print(f"==========================================")
        context = browser.new_context(viewport={"width": 393, "height": 851}, has_touch=True)
        page = context.new_page()
        page.goto(file_url, wait_until="networkidle")
        page.evaluate("() => { const s = document.getElementById('screen-splash'); if (s) s.classList.add('hidden'); }")
        time.sleep(0.2)

        # 1. Test playing a preloaded catalog track
        page.evaluate("""() => {
            loadAndPlayTrack(PLAYLIST_SONGS[0]);
        }""")
        time.sleep(0.3)
        status_text = page.locator("#detail-download-status").text_content()
        print(f"Preloaded track status: '{status_text}'")
        assert "320 kbps" in status_text, f"Expected 320 kbps status, got '{status_text}'"
        print("PASS: Preloaded catalog track plays as full 320 kbps song.")

        # 2. Test Smart Audio Resolver with simulated external search track
        test_track_js = """() => {
            window.__download_requested = false;
            // Mock fetch to simulate /api/download_song
            const origFetch = window.fetch;
            window.fetch = async function(url, opts) {
                if (url.includes('/api/status')) {
                    return { ok: true, json: async () => ({ status: 'ok', server: 'online' }) };
                }
                if (url.includes('/api/download_song')) {
                    window.__download_requested = true;
                    return {
                        ok: true,
                        json: async () => ({
                            status: 'success',
                            download_url: '/api/audio/Levitating_Dua_Lipa.m4a',
                            filename: 'Levitating_Dua_Lipa.m4a',
                            size_mb: '7.8 MB',
                            duration_s: 203
                        })
                    };
                }
                return origFetch(url, opts);
            };

            const externalTrack = {
                id: 'ext_test_123',
                title: 'Dance The Night',
                artist: 'Dua Lipa',
                album: 'Barbie The Album',
                preview: 'data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA='
            };
            loadAndPlayTrack(externalTrack);
        }"""
        page.evaluate(test_track_js)
        time.sleep(0.6)

        dl_requested = page.evaluate("() => window.__download_requested")
        print(f"Background /api/download_song requested: {dl_requested}")
        assert dl_requested is True, "Smart Audio Resolver failed to call /api/download_song!"

        audio_src = page.evaluate("() => document.getElementById('core-audio-player').src")
        print(f"Active Audio src: {audio_src}")
        assert "Dance_The_Night_Dua_Lipa.m4a" in audio_src or "Levitating_Dua_Lipa.m4a" in audio_src, f"Audio src was not hot-swapped to full song: {audio_src}"

        status_text_ext = page.locator("#detail-download-status").text_content()
        print(f"Resolved track status: '{status_text_ext}'")
        assert "Canción completa activa" in status_text_ext, f"Unexpected status text: '{status_text_ext}'"
        print("PASS: Smart Audio Resolver hot-swaps preview to full song with active status!")

        browser.close()
        print("\nALL VERIFICATIONS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    verify_all()
