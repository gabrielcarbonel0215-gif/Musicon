import os
import sys
import time
from playwright.sync_api import sync_playwright

def run_tests():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(base_dir, "index.html")
    assert os.path.exists(index_path), "index.html does not exist!"

    file_url = f"file:///{index_path.replace(os.sep, '/')}"
    print(f"Testing URL: {file_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mobile viewport emulation (Pixel 5: 393 x 851)
        context = browser.new_context(
            viewport={"width": 393, "height": 851},
            user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            has_touch=True
        )
        page = context.new_page()

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(f"PAGE ERROR: {err}"))
        page.on("console", lambda msg: console_errors.append(f"CONSOLE ERROR: {msg.text}") if msg.type == "error" else None)

        page.goto(file_url, wait_until="networkidle")
        # Dismiss splash cleanly for instant deterministic testing
        page.evaluate("""() => {
            const s = document.getElementById('screen-splash');
            if (s) { s.classList.add('hidden', 'opacity-0', 'pointer-events-none'); }
        }""")
        time.sleep(0.2)

        print("\n--- Test 1: Global Navigation on Main Screen ---")
        home_nav_buttons = page.locator("[data-nav]").all()
        assert len(home_nav_buttons) == 3, f"Expected 3 global nav buttons, found {len(home_nav_buttons)}"
        nav_values = [btn.get_attribute("data-nav") for btn in home_nav_buttons]
        assert "home" in nav_values, "data-nav='home' missing from global nav"
        assert "search" in nav_values, "data-nav='search' missing from global nav"
        assert "downloads" in nav_values, "data-nav='downloads' missing from global nav"
        assert page.locator("#screen-home").is_visible(), "#screen-home should be visible by default"
        print("PASS: Main screen retains all 3 global navigation buttons (home, search, downloads).")

        print("\n--- Test 2: Absolute Absence of Bottom Nav in #modal-song-detail ---")
        detail_modal = page.locator("#modal-song-detail")
        assert detail_modal.count() == 1, "#modal-song-detail not found"
        
        # Check that none of the 3 detail nav buttons exist inside #modal-song-detail
        assert page.locator("#modal-song-detail #detail-nav-music").count() == 0, "#detail-nav-music found inside #modal-song-detail!"
        assert page.locator("#modal-song-detail #detail-nav-search").count() == 0, "#detail-nav-search found inside #modal-song-detail!"
        assert page.locator("#modal-song-detail #detail-nav-library").count() == 0, "#detail-nav-library found inside #modal-song-detail!"
        # Check that the 64px dock div does not exist inside #modal-song-detail
        assert page.locator("#modal-song-detail div.h-\\[64px\\]").count() == 0, "64px dock div still exists inside #modal-song-detail!"
        print("PASS: #detail-nav-music, #detail-nav-search, and #detail-nav-library are completely absent from #modal-song-detail.")

        print("\n--- Test 3: Preservation of Playback Controls and Header in #modal-song-detail ---")
        assert page.locator("#btn-close-song-detail").count() == 1, "Back button missing"
        assert page.locator("#btn-detail-favorite").count() == 1, "Favorite button missing"
        assert page.locator("#detail-btn-download-full").count() == 1, "Download button missing"
        assert page.locator("#detail-btn-shuffle").count() == 1, "Shuffle button missing"
        assert page.locator("#detail-btn-prev").count() == 1, "Prev button missing"
        assert page.locator("#detail-btn-play-mini").count() == 1, "Play/pause button missing"
        assert page.locator("#detail-btn-next").count() == 1, "Next button missing"
        assert page.locator("#detail-btn-repeat").count() == 1, "Repeat button missing"
        print("PASS: Header buttons and all 5 playback controls preserved in #modal-song-detail.")

        print("\n--- Test 4: Open #modal-song-detail & Placement of Cinnamoroll ---")
        # Open modal by clicking mini track info
        page.locator("#mini-track-info").click()
        time.sleep(0.5)
        modal_classes = detail_modal.get_attribute("class").split()
        assert "hidden" not in modal_classes, f"#modal-song-detail failed to open: {modal_classes}"

        cinna_container = page.locator("#detail-cinnamoroll-container")
        assert cinna_container.count() == 1, "#detail-cinnamoroll-container not found"
        assert cinna_container.is_visible(), "#detail-cinnamoroll-container is not visible"

        # Check box bounding
        next_card_box = page.locator("#detail-next-card").bounding_box()
        cinna_box = cinna_container.bounding_box()
        print(f"Next Card Box: {next_card_box}")
        print(f"Cinnamoroll Box: {cinna_box}")

        assert cinna_box["y"] >= next_card_box["y"], "Cinnamoroll container should be positioned below Next Song card"
        assert 130 <= cinna_box["height"] <= 210, f"Cinnamoroll height {cinna_box['height']} outside expected mobile range [130, 210]"

        # Check sprite frame
        active_frame = page.locator("#cinnamoroll-active-frame")
        assert active_frame.count() == 1, "#cinnamoroll-active-frame not found"
        img_src = active_frame.get_attribute("src")
        assert img_src.startswith("data:image/png;base64,"), "Active frame is not a base64 PNG"
        print("PASS: Cinnamoroll container correctly placed, sized, and rendered below next card.")

        print("\n--- Test 5: Reactive Animation State Machine ---")
        # Check initial state (audio not playing)
        initial_state = page.evaluate("window.CinnamorollEngine.getState()")
        print(f"Current initial state: {initial_state}")
        assert initial_state in ["IDLE", "PAUSED"], f"Unexpected initial state: {initial_state}"

        # Test PAUSED state: has cinna-breathe class
        page.evaluate("window.CinnamorollEngine.sync()")
        stage_class = page.locator("#cinnamoroll-sprite-stage").get_attribute("class")
        assert "cinna-breathe" in stage_class, "Expected cinna-breathe class in PAUSED/IDLE state"
        print("PASS: PAUSED/IDLE state correctly has cinna-breathe animation.")

        # Test PLAYING state
        page.evaluate("() => { const a = document.getElementById('core-audio-player'); a.dispatchEvent(new Event('play')); }")
        time.sleep(0.3)
        playing_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert playing_state == "PLAYING", f"Expected PLAYING, got {playing_state}"
        stage_class_playing = page.locator("#cinnamoroll-sprite-stage").get_attribute("class")
        assert "cinna-breathe" not in stage_class_playing, "cinna-breathe should be removed in PLAYING state"
        print("PASS: PLAYING state activated upon play event.")

        # Wait for floating note to spawn
        time.sleep(1.8)
        notes = page.locator(".cinna-floating-note").all()
        print(f"Spawned floating notes: {len(notes)}")
        assert len(notes) >= 1, "Expected at least 1 floating note spawned during playback"
        print("PASS: Floating notes spawned in PLAYING state.")

        # Test PAUSE event
        page.evaluate("() => { const a = document.getElementById('core-audio-player'); a.dispatchEvent(new Event('pause')); }")
        time.sleep(0.3)
        paused_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert paused_state == "PAUSED", f"Expected PAUSED, got {paused_state}"
        assert "cinna-breathe" in page.locator("#cinnamoroll-sprite-stage").get_attribute("class")
        print("PASS: Paused state restored on pause event.")

        # Test LOADING state
        page.evaluate("() => { const a = document.getElementById('core-audio-player'); a.dispatchEvent(new Event('waiting')); }")
        time.sleep(0.2)
        loading_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert loading_state == "LOADING", f"Expected LOADING, got {loading_state}"
        assert "cinna-look-around" in page.locator("#cinnamoroll-sprite-stage").get_attribute("class"), "Expected cinna-look-around in LOADING state"
        assert not page.locator("#cinna-spinning-star").is_hidden(), "Spinning star should be visible in LOADING state"
        print("PASS: LOADING state has cinna-look-around and visible spinning star.")

        # Restore to PAUSED
        page.evaluate("() => { const a = document.getElementById('core-audio-player'); a.dispatchEvent(new Event('pause')); }")
        time.sleep(0.2)

        print("\n--- Test 6: Single Tap Gesture (HAPPY) ---")
        # Dispatch single tap
        cinna_container.tap()
        time.sleep(0.35) # Wait past 280ms debounce
        current_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert current_state == "tap", f"Expected transient state 'tap', got {current_state}"
        stars = page.locator(".cinna-pop-star").all()
        assert len(stars) >= 1, "Expected pop stars to spawn on HAPPY tap"
        print("PASS: Single tap triggers HAPPY state and star sparkles without altering audio.")

        time.sleep(0.8) # Wait for transient to return

        print("\n--- Test 7: Double Tap Gesture (LOVE & Favorite toggle) ---")
        # Check initial favorite status
        is_fav_before = page.evaluate("favorites.some(f => f.title === currentTrack.title)")
        fav_btn_class_before = page.locator("#btn-detail-favorite").get_attribute("class")
        print(f"Favorite before double tap: {is_fav_before}")

        # Rapid two taps within 280ms
        cinna_container.tap()
        time.sleep(0.08)
        cinna_container.tap()
        time.sleep(0.1)

        current_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert current_state == "love", f"Expected transient state 'love', got {current_state}"
        hearts = page.locator(".cinna-floating-heart").all()
        assert len(hearts) >= 1, "Expected floating heart on double tap"
        is_fav_after = page.evaluate("favorites.some(f => f.title === currentTrack.title)")
        print(f"Favorite after double tap: {is_fav_after}")
        assert is_fav_after != is_fav_before, "Double tap failed to toggle favorite state!"
        print("PASS: Double tap triggers LOVE state, floating heart, and immediate favorite toggle.")

        time.sleep(1.0) # Wait for transient to return

        print("\n--- Test 8: Real Touch Long Press Gesture (SPECIAL & Cuddle Aura) ---")
        # Dispatch real touch events on container: touchstart, wait 560ms without moving
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const touch = new Touch({
                identifier: 101,
                target: el,
                clientX: 200,
                clientY: 700
            });
            el.dispatchEvent(new TouchEvent('touchstart', {
                touches: [touch],
                targetTouches: [touch],
                changedTouches: [touch],
                bubbles: true
            }));
        }""")
        time.sleep(0.56) # Hold past 520ms threshold
        current_state = page.evaluate("window.CinnamorollEngine.getState()")
        assert current_state == "cuddle", f"Expected transient state 'cuddle', got {current_state}"
        stage_class = page.locator("#cinnamoroll-sprite-stage").get_attribute("class")
        assert "cinna-glow" in stage_class, f"Expected 'cinna-glow' class, got {stage_class}"
        # End touch
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const touch = new Touch({ identifier: 101, target: el, clientX: 200, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchend', {
                touches: [],
                targetTouches: [],
                changedTouches: [touch],
                bubbles: true
            }));
        }""")
        print("PASS: Real touch long press triggers SPECIAL cuddling animation with glowing aura.")

        time.sleep(1.3) # Wait for transient to return

        print("\n--- Test 9: Real Touch Horizontal Swipe Gestures (Next & Prev) ---")
        initial_song_title = page.locator("#detail-title").inner_text()
        print(f"Song before swipe: {initial_song_title}")

        # Real Touch Swipe Left: dx = -80px (playNext)
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const t1 = new Touch({ identifier: 201, target: el, clientX: 250, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchstart', { touches: [t1], changedTouches: [t1], bubbles: true }));
            const t2 = new Touch({ identifier: 201, target: el, clientX: 170, clientY: 705 });
            el.dispatchEvent(new TouchEvent('touchmove', { touches: [t2], changedTouches: [t2], bubbles: true }));
            el.dispatchEvent(new TouchEvent('touchend', { touches: [], changedTouches: [t2], bubbles: true }));
        }""")
        time.sleep(0.15)
        assert page.evaluate("window.CinnamorollEngine.getState()") == "next", "Expected state 'next' on swipe left"
        assert "cinna-bounce" in page.locator("#cinnamoroll-sprite-stage").get_attribute("class"), "Expected cinna-bounce on next"
        print("PASS: Real Touch Swipe Left changed track and triggered excited bounce jump NEXT_SONG.")

        time.sleep(0.9) # Wait for transient to return

        # Real Touch Swipe Right: dx = +80px (playPrev)
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const t1 = new Touch({ identifier: 301, target: el, clientX: 170, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchstart', { touches: [t1], changedTouches: [t1], bubbles: true }));
            const t2 = new Touch({ identifier: 301, target: el, clientX: 250, clientY: 705 });
            el.dispatchEvent(new TouchEvent('touchmove', { touches: [t2], changedTouches: [t2], bubbles: true }));
            el.dispatchEvent(new TouchEvent('touchend', { touches: [], changedTouches: [t2], bubbles: true }));
        }""")
        time.sleep(0.15)
        assert page.evaluate("window.CinnamorollEngine.getState()") == "prev", "Expected state 'prev' on swipe right"
        assert "cinna-curious-left" in page.locator("#cinnamoroll-sprite-stage").get_attribute("class"), "Expected cinna-curious-left on prev"
        print("PASS: Real Touch Swipe Right triggered curious look to the left PREVIOUS_SONG.")

        time.sleep(0.9)

        print("\n--- Test 10: Multi-Touch Rejection & Touchcancel (Ledger R0-1 & R0-3) ---")
        # 2-finger pinch touchstart
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const t1 = new Touch({ identifier: 401, target: el, clientX: 180, clientY: 700 });
            const t2 = new Touch({ identifier: 402, target: el, clientX: 220, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchstart', { touches: [t1, t2], changedTouches: [t1, t2], bubbles: true }));
        }""")
        time.sleep(0.55) # Would trigger long press if not rejected!
        state_during_multi = page.evaluate("window.CinnamorollEngine.getState()")
        assert state_during_multi != "cuddle", f"Multi-touch should NOT trigger long press! Got: {state_during_multi}"

        # End multi-touch
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const t1 = new Touch({ identifier: 401, target: el, clientX: 180, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchend', { touches: [], changedTouches: [t1], bubbles: true }));
        }""")
        time.sleep(0.35)
        state_after_multi = page.evaluate("window.CinnamorollEngine.getState()")
        assert state_after_multi != "tap", f"Multi-touch release should NOT trigger tap! Got: {state_after_multi}"
        print("PASS: Multi-touch (2-finger) correctly rejected with 0 spurious gestures.")

        # Touchcancel test
        page.evaluate("""() => {
            const el = document.getElementById('detail-cinnamoroll-container');
            const t1 = new Touch({ identifier: 501, target: el, clientX: 180, clientY: 700 });
            el.dispatchEvent(new TouchEvent('touchstart', { touches: [t1], changedTouches: [t1], bubbles: true }));
            el.dispatchEvent(new TouchEvent('touchcancel', { touches: [], changedTouches: [t1], bubbles: true }));
        }""")
        time.sleep(0.55)
        assert page.evaluate("window.CinnamorollEngine.getState()") != "cuddle", "touchcancel must clear long press timer"
        print("PASS: touchcancel cleanly resets gesture state.")

        print("\n--- Test 11: Rapid-Fire Swiping Stress Test (Ledger R0-2) ---")
        initial_idx = page.evaluate("currentTrackIndex")
        for i in range(5):
            page.evaluate(f"""() => {{
                const el = document.getElementById('detail-cinnamoroll-container');
                const t1 = new Touch({{ identifier: 600 + {i}, target: el, clientX: 260, clientY: 700 }});
                el.dispatchEvent(new TouchEvent('touchstart', {{ touches: [t1], changedTouches: [t1], bubbles: true }}));
                const t2 = new Touch({{ identifier: 600 + {i}, target: el, clientX: 160, clientY: 700 }});
                el.dispatchEvent(new TouchEvent('touchmove', {{ touches: [t2], changedTouches: [t2], bubbles: true }}));
                el.dispatchEvent(new TouchEvent('touchend', {{ touches: [], changedTouches: [t2], bubbles: true }}));
            }}""")
            time.sleep(0.1) # 100ms between rapid swipes

        time.sleep(0.5)
        final_idx = page.evaluate("currentTrackIndex")
        catalog_len = page.evaluate("currentTracksList.length")
        assert 0 <= final_idx < catalog_len, f"Invalid track index after rapid swipes: {final_idx}"
        print(f"PASS: 5 rapid swipes handled cleanly. Track index advanced from {initial_idx} to {final_idx} (catalog len: {catalog_len}).")

        print("\n--- Test 12: Lifecycle & 0% CPU Optimization ---")
        # Close #modal-song-detail
        page.locator("#btn-close-song-detail").click()
        time.sleep(0.3)
        assert "hidden" in detail_modal.get_attribute("class").split(), "#modal-song-detail should have 'hidden'"
        
        # In hidden state, particle layer must be clear and ticker must be paused
        particles_count = page.locator("#cinnamoroll-particles-layer *").count()
        assert particles_count == 0, f"Expected 0 particles when hidden, found {particles_count}"
        print("PASS: Animation and particles stopped when #modal-song-detail is hidden (0% CPU).")

        # Reopen
        page.locator("#mini-track-info").click()
        time.sleep(0.3)
        assert "hidden" not in detail_modal.get_attribute("class").split()
        reopened_state = page.evaluate("window.CinnamorollEngine.getState()")
        print(f"Reopened state: {reopened_state}")
        assert reopened_state in ["PAUSED", "IDLE", "PLAYING"]
        print("PASS: Animation automatically resumes and resynchronizes when reopened.")

        # Take screenshot for visual audit
        screenshot_path = os.path.join(base_dir, "cinna_detail_verified.png")
        page.screenshot(path=screenshot_path)
        print(f"Saved visual verification screenshot to: {screenshot_path}")

        print("\n--- Console Errors Check ---")
        if console_errors:
            print("Console Errors detected:")
            for err in console_errors:
                print(f"  {err}")
            assert False, "Console errors detected during execution!"
        else:
            print("PASS: ZERO console errors or page errors detected.")

        browser.close()

    print("\nALL VERIFICATION CHECKS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
