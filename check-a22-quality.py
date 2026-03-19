#!/usr/bin/env python3
"""
Umfassendes Qualitäts-Prüfskript für A2.2 DaF-HTML-Dateien.
Prüft ALLE Regeln aus dem Masterplan und den Skills:
- Layout (daf-html-layout)
- Live-Feedback (daf-uebungsformen)
- Satzbau (satzbau-drag-drop)
- Timer-System
- Wortschatz-Tab
- Plural-Notation (daf-pluralendungen)
- Footer / Copyright
- Placeholder-Regeln
- Nav-Button-Struktur (Emoji über Text)
- Mobile Responsive
- Kein Prüfen-Button
"""

import re
import sys
import os
import glob

# ─── Farben ───────────────────────────────────────────────
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
RESET = '\033[0m'

def ok(msg):
    return f"  {GREEN}✓{RESET} {msg}"

def fail(msg):
    return f"  {RED}✗{RESET} {msg}"

def warn(msg):
    return f"  {YELLOW}⚠{RESET} {msg}"


def check_file(filepath):
    filename = os.path.basename(filepath)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []
    passes = []

    # ─── Dateityp erkennen ────────────────────────────────
    typ = None
    m = re.search(r'DE_A2_\d{4}([VXGRSWC])', filename)
    if m:
        typ = m.group(1)

    print(f"\n{BOLD}{'═'*60}{RESET}")
    print(f"{BOLD}Datei:{RESET} {filename}  (Typ: {typ or '?'})")
    print(f"{'═'*60}")

    # ═══════════════════════════════════════════════════════
    # 1. LAYOUT (daf-html-layout Skill)
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[1] Layout (daf-html-layout){RESET}")

    # Body: lila Verlauf
    if re.search(r'background:\s*linear-gradient\(135deg,\s*#667eea\s+0%,\s*#764ba2\s+100%\)', content):
        passes.append(ok("Body: lila Verlauf korrekt"))
    else:
        errors.append(fail("Body: lila Verlauf FEHLT oder falsch"))

    # Container: max-width 1000px
    if re.search(r'max-width:\s*1000px', content):
        passes.append(ok("Container: max-width: 1000px"))
    else:
        errors.append(fail("Container: max-width: 1000px FEHLT"))

    # Container: border-radius 12px
    if re.search(r'border-radius:\s*12px', content):
        passes.append(ok("Container: border-radius: 12px"))
    else:
        errors.append(fail("Container: border-radius: 12px FEHLT"))

    # Container: overflow hidden
    if 'overflow: hidden' in content or 'overflow:hidden' in content:
        passes.append(ok("Container: overflow: hidden"))
    else:
        errors.append(fail("Container: overflow: hidden FEHLT"))

    # Container: box-shadow
    if re.search(r'box-shadow:\s*0\s+10px\s+40px\s+rgba\(0,\s*0,\s*0,\s*0\.2\)', content):
        passes.append(ok("Container: box-shadow korrekt"))
    else:
        errors.append(fail("Container: box-shadow FEHLT oder falsch"))

    # Nav: flex-wrap nowrap
    if re.search(r'\.nav\s*\{[^}]*flex-wrap:\s*nowrap', content):
        passes.append(ok("Nav: flex-wrap: nowrap"))
    else:
        errors.append(fail("Nav: flex-wrap: nowrap FEHLT"))

    # Nav: border-top
    if re.search(r'\.nav\s*\{[^}]*border-top:\s*1px\s+solid\s+#ddd', content):
        passes.append(ok("Nav: border-top: 1px solid #ddd"))
    else:
        errors.append(fail("Nav: border-top FEHLT"))

    # Nav-btn: border-right + border-bottom
    if re.search(r'\.nav-btn\s*\{[^}]*border-right:\s*1px\s+solid\s+#ddd', content):
        passes.append(ok("Nav-btn: border-right korrekt"))
    else:
        errors.append(fail("Nav-btn: border-right FEHLT"))

    # Nav-btn.active: background white + border-bottom 3px solid #667eea
    if re.search(r'\.nav-btn\.active\s*\{[^}]*background:\s*white', content):
        passes.append(ok("Nav-btn.active: background: white"))
    else:
        errors.append(fail("Nav-btn.active: background: white FEHLT"))

    if re.search(r'\.nav-btn\.active\s*\{[^}]*border-bottom:\s*3px\s+solid\s+#667eea', content):
        passes.append(ok("Nav-btn.active: border-bottom: 3px solid #667eea"))
    else:
        errors.append(fail("Nav-btn.active: border-bottom FEHLT"))

    # Mobile responsive
    if re.search(r'@media\s*\(\s*max-width:\s*600px\s*\)', content):
        passes.append(ok("@media (max-width: 600px) vorhanden"))
        # Check flex-wrap: wrap in media
        media_block = re.search(r'@media\s*\(\s*max-width:\s*600px\s*\)\s*\{(.+?)(?:\n\s*\}(?:\s*\n|\s*$))', content, re.DOTALL)
        if media_block:
            mb = media_block.group(1)
            if 'flex-wrap: wrap' in mb or 'flex-wrap:wrap' in mb:
                passes.append(ok("Media: Nav flex-wrap: wrap"))
            else:
                errors.append(fail("Media: Nav flex-wrap: wrap FEHLT"))
            if re.search(r'flex:\s*1\s+1\s+33%', mb):
                passes.append(ok("Media: Nav-btn flex: 1 1 33%"))
            else:
                errors.append(fail("Media: Nav-btn flex: 1 1 33% FEHLT"))
        else:
            # Broader search for media content
            if re.search(r'@media[^{]*600px[^{]*\{[^}]*flex-wrap:\s*wrap', content, re.DOTALL):
                passes.append(ok("Media: Nav flex-wrap: wrap"))
            else:
                errors.append(fail("Media: Nav flex-wrap: wrap FEHLT"))
            if re.search(r'@media[^{]*600px[^{]*\{[^}]*flex:\s*1\s+1\s+33%', content, re.DOTALL):
                passes.append(ok("Media: Nav-btn flex: 1 1 33%"))
            else:
                errors.append(fail("Media: Nav-btn flex: 1 1 33% FEHLT"))
    else:
        errors.append(fail("@media (max-width: 600px) FEHLT komplett"))

    # ═══════════════════════════════════════════════════════
    # 2. NAV-BUTTONS: Emoji über Text
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[2] Nav-Buttons (Emoji über Text){RESET}")

    nav_btns = re.findall(r'<(?:div|button)\s+class="nav-btn[^"]*"[^>]*>(.*?)(?:</div>|</button>)', content, re.DOTALL)
    if nav_btns:
        has_spans = all(
            re.search(r'<span\s+class="nav-emoji">', btn) and re.search(r'<span\s+class="nav-label">', btn)
            for btn in nav_btns
        )
        if has_spans:
            passes.append(ok(f"Alle {len(nav_btns)} Nav-Buttons haben nav-emoji + nav-label Spans"))
        else:
            errors.append(fail("Nav-Buttons: Nicht alle haben nav-emoji + nav-label Spans"))
    else:
        errors.append(fail("Keine Nav-Buttons gefunden"))

    # flex-direction: column in nav-btn
    if re.search(r'\.nav-btn\s*\{[^}]*flex-direction:\s*column', content):
        passes.append(ok("Nav-btn: flex-direction: column (Emoji über Text)"))
    else:
        errors.append(fail("Nav-btn: flex-direction: column FEHLT"))

    # nav-emoji + nav-label CSS
    if '.nav-emoji' in content and '.nav-label' in content:
        passes.append(ok("CSS-Klassen .nav-emoji und .nav-label definiert"))
    else:
        errors.append(fail("CSS-Klassen .nav-emoji / .nav-label FEHLEN"))

    # ═══════════════════════════════════════════════════════
    # 3. FOOTER / COPYRIGHT
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[3] Footer / Copyright{RESET}")

    if 'class="author-footer"' in content:
        passes.append(ok("author-footer vorhanden"))
    else:
        errors.append(fail("author-footer FEHLT"))

    if '&copy; Frank Burkert' in content or '© Frank Burkert' in content:
        passes.append(ok("© Frank Burkert vorhanden"))
    else:
        errors.append(fail("© Frank Burkert FEHLT"))

    if 'FrankBurkert@fabdaf.onmicrosoft.com' in content:
        passes.append(ok("Korrekte E-Mail-Adresse"))
    else:
        errors.append(fail("E-Mail FrankBurkert@fabdaf.onmicrosoft.com FEHLT"))

    # Footer innerhalb Container
    container_end = content.rfind('</div><!-- /container -->')
    if container_end == -1:
        container_end = content.rfind('</div><!--/container-->')
    footer_pos = content.find('class="author-footer"')
    if container_end > 0 and footer_pos > 0 and footer_pos < container_end:
        passes.append(ok("Footer ist innerhalb des Containers"))
    elif footer_pos > 0:
        warnings.append(warn("Footer-Position unklar (<!-- /container --> Kommentar prüfen)"))

    # ═══════════════════════════════════════════════════════
    # 4. KEIN PRÜFEN-BUTTON
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[4] Kein Prüfen-Button{RESET}")

    pruefen_matches = re.findall(r'(?i)(prüfen|prufen|check\s*answer|überprüfen|uberprüfen)', content)
    # Filter out false positives in comments or data
    real_buttons = [m for m in re.findall(r'<button[^>]*>([^<]*(?:prüfen|Prüfen|überprüfen|Überprüfen)[^<]*)</button>', content, re.IGNORECASE)]
    if real_buttons:
        errors.append(fail(f"PRÜFEN-BUTTON gefunden: {real_buttons}"))
    else:
        passes.append(ok("Kein Prüfen-Button gefunden"))

    # ═══════════════════════════════════════════════════════
    # 5. PLACEHOLDER-REGELN
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[5] Placeholder-Regeln{RESET}")

    # Verboten: placeholder="___" oder ähnlich
    bad_placeholders = re.findall(r'placeholder="([_\-\.]{2,})"', content)
    if bad_placeholders:
        errors.append(fail(f"Verbotene Placeholder gefunden: {bad_placeholders}"))
    else:
        passes.append(ok("Keine verbotenen Placeholder (___) gefunden"))

    # Verboten: placeholder="der/die/das"
    if re.search(r'placeholder="der/die/das"', content, re.IGNORECASE):
        errors.append(fail("placeholder='der/die/das' gefunden — verboten! Muss 'Artikel' sein"))
    else:
        passes.append(ok("Kein 'der/die/das' Placeholder"))

    # ═══════════════════════════════════════════════════════
    # 6. LIVE-FEEDBACK (daf-uebungsformen)
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[6] Live-Feedback{RESET}")

    # Prüfe ob der kritische Fehler vorhanden ist: startsWith VOR ===
    bad_pattern = re.search(r'if\s*\(\s*ans\.startsWith\(val\)\s*\)\s*return\s*;?\s*\n\s*inp\.classList\.add\(val\s*===\s*ans', content)
    if bad_pattern:
        errors.append(fail("KRITISCHER FEHLER: ans.startsWith(val) VOR val === ans — .ok wird nie gesetzt!"))
    else:
        passes.append(ok("Kein kritischer startsWith/=== Reihenfolgefehler"))

    # Prüfe ob .ok und .no CSS-Klassen definiert sind
    has_ok_css = bool(re.search(r'\.(luecken-inp|ws-inp)\.ok', content) or re.search(r'\.ok\s*\{', content))
    has_no_css = bool(re.search(r'\.(luecken-inp|ws-inp)\.no', content) or re.search(r'\.no\s*\{', content))
    if has_ok_css and has_no_css:
        passes.append(ok("CSS-Klassen .ok und .no definiert"))
    elif re.search(r'\.correct\s*\{', content) and re.search(r'\.wrong\s*\{', content):
        passes.append(ok("CSS-Klassen .correct und .wrong definiert (alternatives Pattern)"))
    else:
        warnings.append(warn("Live-Feedback CSS (.ok/.no oder .correct/.wrong) nicht eindeutig gefunden"))

    # ═══════════════════════════════════════════════════════
    # 7. TIMER-SYSTEM
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[7] Timer-System{RESET}")

    has_timer = bool(re.search(r'timerAutoStart|initTimer|startTimer|TIMER_PREFIX', content))
    has_timer_display = bool(re.search(r'id="timer-|class="timer"', content))

    if has_timer and has_timer_display:
        passes.append(ok("Timer-System vorhanden"))
    elif has_timer:
        warnings.append(warn("Timer-JS gefunden, aber kein Timer-Display im DOM"))
    else:
        # Timer ist Pflicht für Tabs mit Tipp- oder Drag-Übungen
        has_interactive = bool(re.search(r'luecken-inp|ws-inp|satzbauData|sentence-builder|chips-container', content))
        if has_interactive:
            warnings.append(warn("Interaktive Übungen ohne Timer-System — laut Masterplan Pflicht"))
        else:
            passes.append(ok("Kein Timer nötig (keine interaktiven Übungen)"))

    # ═══════════════════════════════════════════════════════
    # 8. SATZBAU (satzbau-drag-drop Skill)
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[8] Satzbau{RESET}")

    has_satzbau = 'satzbauData' in content
    if has_satzbau:
        # Pflicht-Bezeichner
        for name in ['sbDragged', 'sbMakeChip', 'sbRegisterZone', 'sbColorRow', 'sbCheckAuto', 'sbUpdateCapitalization', 'sbShowSolution']:
            if name in content:
                passes.append(ok(f"Satzbau: {name} vorhanden"))
            else:
                errors.append(fail(f"Satzbau: {name} FEHLT"))

        # Verbotene alte Bezeichner
        if '.drop-row' in content:
            errors.append(fail("Satzbau: Alter Bezeichner .drop-row gefunden (→ .sentence-builder)"))
        if 'showSatzbauLoesung' in content:
            errors.append(fail("Satzbau: Alter Bezeichner showSatzbauLoesung (→ sbShowSolution)"))

        # dataset.orig
        if 'dataset.orig' in content:
            passes.append(ok("Satzbau: dataset.orig verwendet"))
        else:
            errors.append(fail("Satzbau: dataset.orig FEHLT"))

        # .sentence-builder CSS
        if '.sentence-builder' in content:
            passes.append(ok("Satzbau: .sentence-builder CSS vorhanden"))
        else:
            errors.append(fail("Satzbau: .sentence-builder CSS FEHLT"))
    else:
        passes.append(ok("Kein Satzbau-Tab in dieser Datei"))

    # ═══════════════════════════════════════════════════════
    # 9. WORTSCHATZ-TAB (nur V-Dateien)
    # ═══════════════════════════════════════════════════════
    if typ == 'V':
        print(f"\n{BOLD}[9] Wortschatz-Tab (V-Datei){RESET}")

        has_ws = 'WS_DATA' in content or 'WORTSCHATZ' in content or 'wortschatzContainer' in content
        if has_ws:
            passes.append(ok("Wortschatz-Daten vorhanden"))

            # Artikel-Placeholder
            if re.search(r"placeholder\s*[=:]\s*['\"]Artikel['\"]", content):
                passes.append(ok("Wortschatz: Artikel-Placeholder korrekt"))
            else:
                warnings.append(warn("Wortschatz: Placeholder 'Artikel' nicht gefunden"))

            # Artikel width 70px
            if re.search(r'\.art\s*\{[^}]*width:\s*70px', content) or re.search(r"width\s*[=:]\s*['\"]70px['\"]", content) or "'70px'" in content:
                passes.append(ok("Wortschatz: Artikel-Breite 70px"))
            else:
                warnings.append(warn("Wortschatz: Artikel-Breite 70px nicht gefunden"))
        else:
            warnings.append(warn("V-Datei ohne Wortschatz-Tab?"))

    # ═══════════════════════════════════════════════════════
    # 10. PLURAL-NOTATION (daf-pluralendungen)
    # ═══════════════════════════════════════════════════════
    if typ == 'V':
        print(f"\n{BOLD}[10] Plural-Notation{RESET}")

        # Verboten: -äe, -öer etc.
        bad_plural = re.findall(r'["\']-(ä|ö|ü)(e|er|en)["\']', content)
        if bad_plural:
            errors.append(fail(f"Falsche Plural-Notation gefunden: {bad_plural} — muss -\\u0308e sein"))
        else:
            passes.append(ok("Keine falsche Plural-Notation (-äe, -öer)"))

        # Korrekte Notation vorhanden?
        if '\\u0308' in content or '\u0308' in content:
            passes.append(ok("Korrekte Plural-Umlaut-Notation (U+0308) verwendet"))
        else:
            warnings.append(warn("Keine Umlaut-Plural-Notation gefunden (evtl. keine Umlaut-Plurale nötig)"))

    # ═══════════════════════════════════════════════════════
    # 11. HEADER-STRUKTUR
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[11] Header{RESET}")

    if re.search(r'class="header"', content):
        passes.append(ok("Header-Div vorhanden"))
    else:
        errors.append(fail("Header-Div FEHLT"))

    if re.search(r'class="big-emoji"', content):
        passes.append(ok("Big-Emoji vorhanden"))
    else:
        warnings.append(warn("Big-Emoji im Header fehlt"))

    # Georgia Schrift im Header
    if re.search(r'\.header\s+h1[^{]*\{[^}]*Georgia', content) or re.search(r'font-family:\s*Georgia', content):
        passes.append(ok("Georgia-Schrift im Header"))
    else:
        warnings.append(warn("Georgia-Schrift im Header nicht gefunden"))

    # ═══════════════════════════════════════════════════════
    # 12. toLowerCase() VERBOTEN
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[12] Case-Sensitivity{RESET}")

    # Suche nach toLowerCase() in liveCheck/wortschatzCheck Kontexten
    # liveCheckEndung ist explizit erlaubt (Endungen sind immer case-insensitive)
    has_lower = False
    for fn in ['wortschatzCheck', 'checkWs', 'makeWsInp']:
        if re.search(fn + r'[^}]*toLowerCase', content, re.DOTALL):
            has_lower = True
    # liveCheck nur flaggen wenn es als eigenständige Funktion vorliegt (nicht liveCheckEndung)
    if re.search(r'function liveCheck\s*\(', content):
        m_fn = re.search(r'function liveCheck\s*\(.*?\{(.*?)\n\}', content, re.DOTALL)
        if m_fn and 'toLowerCase' in m_fn.group(1):
            has_lower = True
    if has_lower:
        errors.append(fail("toLowerCase() in Feedback-Funktionen gefunden — VERBOTEN"))
    else:
        passes.append(ok("Kein toLowerCase() in Feedback-Funktionen"))

    # ═══════════════════════════════════════════════════════
    # 13. SECTION-KLASSEN
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[13] Section-Klassen{RESET}")

    sections = re.findall(r'class="section\b([^"]*)"', content)
    if sections:
        # Prüfe ob .active (nicht .aktiv)
        if any('aktiv' in s for s in sections):
            errors.append(fail("Klasse 'aktiv' statt 'active' gefunden"))
        else:
            passes.append(ok("Section-Klassen korrekt (active, nicht aktiv)"))

    # showSection/showTab Funktion
    if 'showSection' in content or 'showTab' in content:
        passes.append(ok("showSection()/showTab()-Funktion vorhanden"))
    else:
        errors.append(fail("showSection()/showTab()-Funktion FEHLT"))

    # ═══════════════════════════════════════════════════════
    # 14. TIMER-START-VERHALTEN
    # ═══════════════════════════════════════════════════════
    if has_timer:
        print(f"\n{BOLD}[14] Timer-Start-Verhalten{RESET}")

        # Satzbau: timerAutoStart muss in dragstart innerhalb sbMakeChip aufgerufen werden
        if has_satzbau:
            sb_func = re.search(r'function\s+sbMakeChip\b.*?^}', content, re.DOTALL | re.MULTILINE)
            if sb_func:
                sb_body = sb_func.group(0)
                ds_in_sb = re.search(r"addEventListener\('dragstart'.*?}\)", sb_body, re.DOTALL)
                if ds_in_sb and 'timerAutoStart' in ds_in_sb.group(0):
                    passes.append(ok("Satzbau-Timer startet beim ersten Drag"))
                elif ds_in_sb:
                    errors.append(fail("Satzbau-Timer startet NICHT beim Drag — timerAutoStart fehlt in sbMakeChip dragstart"))
                else:
                    errors.append(fail("Satzbau: kein dragstart in sbMakeChip gefunden"))

        # Lückentext: timerAutoStart muss VOR der Korrektheitscheck kommen
        # Pattern 1: timerAutoStart direkt am Anfang von liveCheck (gut)
        # Pattern 2: timerAutoStart nach if(!cmpVal) return (gut)
        # Pattern 3: timerAutoStart nur in correctness block (schlecht)
        luecken_match = re.search(r'function\s+liveCheck\b[^{]*\{(.*?)^}', content, re.DOTALL | re.MULTILINE)
        if luecken_match:
            lc_body = luecken_match.group(1)
            if 'timerAutoStart' in lc_body:
                # Check if timerAutoStart is called BEFORE correctness check
                timer_pos = lc_body.find('timerAutoStart')
                ok_pos = lc_body.find("classList.add('ok')")
                if ok_pos < 0:
                    ok_pos = lc_body.find('.add("ok")')
                if timer_pos >= 0 and ok_pos >= 0 and timer_pos < ok_pos:
                    passes.append(ok("Lückentext-Timer startet vor Korrektheitscheck"))
                elif timer_pos >= 0 and ok_pos >= 0 and timer_pos > ok_pos:
                    errors.append(fail("Lückentext-Timer startet NACH Korrektheitscheck — muss vorher kommen"))
                else:
                    passes.append(ok("Lückentext-Timer vorhanden"))
            elif re.search(r'timerAutoStart.*liveCheck|liveCheck.*timerAutoStart', content[:content.find('function liveCheck')]):
                passes.append(ok("Lückentext-Timer extern vor liveCheck aufgerufen"))
        elif re.search(r'oninput="liveCheck\(this,\s*function', content):
            # Callback-pattern: check if timerAutoStartFn is called early
            cb_lc = re.search(r'function\s+liveCheck\(inp,\s*timerAutoStartFn.*?\{(.*?)^}', content, re.DOTALL | re.MULTILINE)
            if cb_lc:
                lc_cb_body = cb_lc.group(1)
                timer_pos = lc_cb_body.find('timerAutoStartFn')
                ok_pos = lc_cb_body.find("classList.add('ok')")
                if timer_pos >= 0 and ok_pos >= 0 and timer_pos < ok_pos:
                    passes.append(ok("Lückentext-Timer (Callback) startet vor Korrektheitscheck"))
                elif timer_pos >= 0 and ok_pos >= 0:
                    errors.append(fail("Lückentext-Timer (Callback) startet NACH Korrektheitscheck"))

    # ═══════════════════════════════════════════════════════
    # 15. LAYOUT-QUALITÄT (Header, Nav, doppelter Footer)
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[15] Layout-Qualität{RESET}")

    # 15a: Kein doppelter Footer (<footer class="footer"> ist VERBOTEN)
    if re.search(r'<footer\s+class="footer"', content):
        errors.append(fail('Doppelter Footer: <footer class="footer"> gefunden — nur .author-footer erlaubt'))
    else:
        passes.append(ok("Kein doppelter Footer"))

    # 15b: Kein .footer CSS (veraltetes Muster)
    if re.search(r'\.footer\s*\{', content):
        errors.append(fail('.footer CSS gefunden — veraltetes Muster, nur .author-footer verwenden'))
    else:
        passes.append(ok("Kein .footer CSS (veraltetes Muster)"))

    # 15c: Header text-align: center
    header_css = re.search(r'\.header\s*\{([^}]*)\}', content, re.DOTALL)
    if header_css:
        if 'text-align: center' in header_css.group(1) or 'text-align:center' in header_css.group(1):
            passes.append(ok("Header: text-align: center"))
        else:
            errors.append(fail("Header: text-align: center FEHLT — Überschrift wird nicht zentriert"))
    else:
        errors.append(fail("Header CSS-Block nicht gefunden"))

    # 15d: Header padding: 30px (nicht 24px oder anderes)
    if header_css:
        hpad = re.search(r'padding:\s*(\d+px)', header_css.group(1))
        if hpad and hpad.group(1) == '30px':
            passes.append(ok("Header: padding: 30px"))
        elif hpad:
            warnings.append(warn(f"Header padding: {hpad.group(1)} — Skill-Standard ist 30px"))

    # 15e: big-emoji steht NACH dem <p>-Untertitel (nicht davor)
    h1_pos = content.find('<h1>')
    p_pos = content.find('<p ', h1_pos) if h1_pos >= 0 else -1
    emoji_pos = content.find('class="big-emoji"', h1_pos) if h1_pos >= 0 else -1
    if h1_pos >= 0 and p_pos >= 0 and emoji_pos >= 0:
        if emoji_pos > p_pos:
            passes.append(ok("big-emoji steht nach dem Untertitel (korrekte Reihenfolge)"))
        else:
            errors.append(fail("big-emoji steht VOR dem Untertitel — muss nach <p> kommen"))
    elif emoji_pos >= 0 and h1_pos >= 0:
        passes.append(ok("big-emoji vorhanden"))

    # 15f: Nav-Button <button> braucht border:none / appearance:none (Browser-Defaults verhindern)
    nav_btn_css = re.search(r'\.nav-btn\s*\{([^}]*)\}', content, re.DOTALL)
    if nav_btn_css:
        nb = nav_btn_css.group(1)
        if 'appearance: none' in nb or '-webkit-appearance: none' in nb or 'border: none' in nb:
            passes.append(ok("Nav-btn: Browser-Default-Border zurückgesetzt"))
        else:
            errors.append(fail("Nav-btn: border:none / appearance:none FEHLT — Browser rendert schwarze Linien bei <button>"))

    # 15g: Nav-btn flex:1 vorhanden
    if nav_btn_css:
        if 'flex: 1' in nav_btn_css.group(1) or 'flex:1' in nav_btn_css.group(1):
            passes.append(ok("Nav-btn: flex: 1 (Tabs gleichmäßig verteilt)"))
        else:
            errors.append(fail("Nav-btn: flex: 1 FEHLT — Tabs werden linksbündig geclustert"))

    # 15h: .btn darf NICHT ausgefüllt sein (background:#667eea = alter falscher Stil)
    btn_css = re.search(r'\.btn\s*\{([^}]+)\}', content)
    if btn_css:
        btn_body = btn_css.group(1)
        if re.search(r'background\s*:\s*#667eea|background\s*:\s*#5a6fd6', btn_body):
            errors.append(fail('.btn hat gefüllten lila Hintergrund (background:#667eea) — Skill-Standard: background:none, border:1px solid #ddd'))
        elif re.search(r'background\s*:\s*#9e9e9e|background\s*:\s*#757575', btn_body):
            errors.append(fail('.btn.secondary mit grauem Hintergrund — muss dezent sein (background:none)'))
        else:
            passes.append(ok('.btn dezent (kein gefüllter lila/grauer Hintergrund)'))

    # 15i: .btn-row button muss border haben (Skill-Standard)
    btnrow_btn = re.search(r'\.btn-row\s+button\s*\{([^}]+)\}', content)
    if btnrow_btn:
        if 'border' in btnrow_btn.group(1):
            passes.append(ok('.btn-row button mit border CSS (Skill-Standard)'))
        else:
            warnings.append(warn('.btn-row button CSS ohne border — Skill-Standard prüfen'))

    # 15j: .control-bar ist VERBOTEN — veraltetes Pattern statt .timer-bar
    if re.search(r'class="control-bar"|\.control-bar\s*\{', content):
        errors.append(fail('[15j] .control-bar gefunden — veraltetes Layout-Pattern\! Korrekt: .timer-bar (weiß, Schatten) + .btn-row (lila Outline-Buttons) als getrennte Divs'))
    else:
        passes.append(ok('Kein .control-bar (veraltetes Timer-Layout-Pattern)'))

    # 15k: .timer-bar CSS muss vorhanden sein wenn Timer-IDs vorhanden sind
    has_timer_ids = bool(re.search(r'id="timer-\d', content))
    has_timer_bar_css = bool(re.search(r'\.timer-bar\s*\{', content))
    if has_timer_ids:
        if has_timer_bar_css:
            passes.append(ok('.timer-bar CSS vorhanden (Skill-Standard Timer-Layout)'))
        else:
            errors.append(fail('[15k] Timer-IDs vorhanden, aber .timer-bar CSS FEHLT — Skill-Standard: .timer-bar mit background:white, box-shadow, border-radius:10px'))

    # 15l: .btn-row CSS muss vorhanden sein (für globale Steuer-Buttons)
    if re.search(r'\.btn-row\s*\{', content):
        passes.append(ok('.btn-row CSS vorhanden'))
    else:
        if has_timer_ids:
            errors.append(fail('[15l] .btn-row CSS FEHLT — Skill-Standard: getrennte Zeile unter .timer-bar mit Neustart- und Lösungen-Buttons'))

    # 15m: score-box darf NICHT in timer-bar stehen — Skill kennt kein Richtig/Falsch in der Timer-Bar
    # Prüft ob class="score-box" innerhalb eines timer-bar divs vorkommt
    import re as _re
    timer_bar_blocks = _re.findall(r'<div class="timer-bar"[^>]*>.*?</div>', content, _re.DOTALL)
    score_in_timer = any('score-box' in block for block in timer_bar_blocks)
    if score_in_timer:
        errors.append(fail('[15m] score-box innerhalb von .timer-bar gefunden — Skill-Standard: Timer-Bar enthält NUR ⏱ Timer + 🏆 Bestzeit, kein Richtig/Falsch'))
    else:
        passes.append(ok('Kein score-box in timer-bar (Skill-Standard: nur Timer + Bestzeit)'))

    # 15n: VERBOTEN — 'Satz 1/2/3' als Satzbau-Label (JS oder HTML)
    # Der User hat ausdrücklich verboten, Sätze nummeriert zu benennen.
    # Nur die spezifischen Label-Muster prüfen, NICHT Frage-Texte im Entdeckungslernen.
    import re as _re2
    satz_label_patterns = _re2.findall(
        r"lbl\.textContent\s*=\s*'Satz\s+'\s*\+|"
        r'<div class="sb-label">Satz\s+\d+|'
        r'<div class="label">Satz\s+\d+:',
        content
    )
    if satz_label_patterns:
        errors.append(fail(f"[15n] VERBOTEN: Satzbau-Label 'Satz 1/2/3...' als JS oder HTML-Label gefunden ({len(satz_label_patterns)}x) — kein Label oder thematischen Hinweis verwenden"))
    else:
        passes.append(ok('Kein verbotenes Satz-1/2/3-Label im Satzbau'))

    # ═══════════════════════════════════════════════════════
    # [16] daf-uebungsformen Skill-Regeln
    # ═══════════════════════════════════════════════════════
    print(f"\n{BOLD}[16] Übungsformen (daf-uebungsformen Skill){RESET}")

    import re as _re3

    # 16a: Kein Prüfen-Button — ABSOLUT VERBOTEN (gilt für alle Übungsformen)
    pruef_buttons = _re3.findall(
        r'<button[^>]*>[^<]*(?:Prüfen|Lösungen prüfen|Check)[^<]*</button>',
        content
    )
    if pruef_buttons:
        errors.append(fail(f"[16a] VERBOTEN: Prüfen-Button gefunden ({len(pruef_buttons)}x) — alle Übungen nutzen ausschließlich Live-Feedback"))
    else:
        passes.append(ok('Kein Prüfen-Button (Live-Feedback-Regel eingehalten)'))

    # 16b: score-box / Richtig-Anzeige darf NICHT in timer-bar stehen
    # (score-box in timer-bar wurde schon in 15m geprüft — hier prüfen wir
    # auch inline-Spans mit "Richtig:" Text in timer-bar)
    timer_bar_blocks = _re3.findall(r'<div class="timer-bar"[^>]*>.*?</div>\s*</div>', content, _re3.DOTALL)
    richtig_in_timer = any(('Richtig:' in b or 'score' in b.lower() and 'score-box' in b) for b in timer_bar_blocks)
    if richtig_in_timer:
        errors.append(fail('[16b] "Richtig:"-Anzeige in timer-bar gefunden — VERBOTEN: Timer-Bar enthält NUR Timer + Bestzeit'))
    else:
        passes.append(ok('Keine Richtig/Score-Anzeige in timer-bar'))

    # 16c: btn-row muss Lösungen-Button enthalten wenn lueckeReset/sbResetAll vorhanden
    has_luecke_reset = 'lueckeReset' in content or 'lueckeReset()' in content
    has_luecke_loesung = 'lueckeLoesung' in content or 'showLueckeLoesung' in content
    has_sb_reset = 'sbResetAll' in content
    has_sb_loesung = 'sbShowAllSolutions' in content or 'sbShowSolution' in content

    if has_luecke_reset and not has_luecke_loesung:
        errors.append(fail('[16c] Lückentext hat ↺ Neu aber KEINEN 💡 Lösungen-Button — Skill verlangt immer beide Buttons'))
    elif has_luecke_reset:
        passes.append(ok('Lückentext: Neu + Lösungen-Buttons vorhanden'))

    if has_sb_reset and not has_sb_loesung:
        errors.append(fail('[16d] Satzbau hat ↺ Neu aber KEINEN 💡 Lösungen-Button — Skill verlangt immer beide Buttons'))
    elif has_sb_reset:
        passes.append(ok('Satzbau: Neu + Lösungen-Buttons vorhanden'))

    # 16e: .luecken-inp oder .gap-inp CSS: border-bottom (kein border ringsherum)
    # Skill: border: none; border-bottom: 2px solid #c5cae9
    has_luecke_inp = '.luecken-inp' in content or '.gap-inp' in content
    if has_luecke_inp:
        has_border_bottom = 'border-bottom' in content and ('luecken-inp' in content or 'gap-inp' in content)
        has_wrong_border = _re3.search(r'\.(?:luecken-inp|gap-inp)\s*\{[^}]*border\s*:', content) is not None
        if has_border_bottom:
            passes.append(ok('Lückentext-Input: border-bottom CSS vorhanden'))
        else:
            errors.append(fail('[16e] Lückentext-Input: border-bottom fehlt — Skill: border:none; border-bottom:2px solid #c5cae9'))

    # 16f: .ok und .no CSS für Lückentext-Inputs (grün/rot Feedback)
    # Skill: .luecken-inp.ok → grün, .luecken-inp.no → rot
    # Alternativen: .correct/.wrong sind auch erlaubt (ältere Dateien)
    has_ok_no = ('.ok' in content and '.no' in content) or ('.correct' in content and '.wrong' in content)
    if not has_ok_no:
        errors.append(fail('[16f] Fehlende .ok/.no oder .correct/.wrong CSS-Klassen für Live-Feedback'))
    else:
        passes.append(ok('Live-Feedback CSS-Klassen (.ok/.no oder .correct/.wrong) vorhanden'))

    # 16g: Multiple-Choice Buttons: font-size 11px (kompakte Pills, nicht breite Balken)
    if '.mc-opt' in content:
        mc_font = _re3.search(r'\.mc-opt\s*\{[^}]*font-size\s*:\s*11px', content)
        mc_flex_col = _re3.search(r'\.mc-opts\s*\{[^}]*flex-direction\s*:\s*column', content)
        if mc_flex_col:
            errors.append(fail('[16g] .mc-opts mit flex-direction:column — VERBOTEN: Buttons müssen nebeneinander stehen (flex-wrap:wrap)'))
        elif not mc_font:
            warnings.append(warn('[16g] .mc-opt font-size sollte 11px sein (kompakte Pills, nicht breite Balken) — Skill-Empfehlung'))
        else:
            passes.append(ok('Multiple-Choice: kompakte Pill-Buttons (11px, flex-wrap)'))

    # 16h: Zuordnungsübung — kein Prüfen-Button, Live-Feedback
    if 'match-card' in content or 'matchDescCard' in content:
        if _re3.search(r'<button[^>]*>(?:Prüfen|Check|Auswerten)', content):
            errors.append(fail('[16h] Zuordnungsübung hat Prüfen-Button — VERBOTEN: sofortiges Live-Feedback via matchDescCard()'))
        else:
            passes.append(ok('Zuordnungsübung: kein Prüfen-Button (Live-Feedback)'))

    # 16i: Wortschatz-Tab: wortschatzCheck() verwenden, NICHT liveCheck()
    if 'wortschatzContainer' in content or 'wortschatzCheck' in content:
        has_ws_check = 'wortschatzCheck' in content
        if not has_ws_check:
            errors.append(fail('[16i] Wortschatz-Tab ohne wortschatzCheck() — VERBOTEN: liveCheck() ist case-insensitive, Nomen müssen case-sensitive geprüft werden'))
        else:
            passes.append(ok('Wortschatz-Tab: wortschatzCheck() vorhanden (case-sensitive für Nomen)'))

    # ═══════════════════════════════════════════════════════
    # ZUSAMMENFASSUNG
    # ═══════════════════════════════════════════════════════
    print(f"\n{'─'*60}")
    for p in passes:
        print(p)
    for w in warnings:
        print(w)
    for e in errors:
        print(e)

    print(f"\n{'─'*60}")
    total_err = len(errors)
    total_warn = len(warnings)
    total_pass = len(passes)

    if total_err == 0 and total_warn == 0:
        print(f"{GREEN}{BOLD}✓ PERFEKT — {total_pass} Checks bestanden, 0 Fehler, 0 Warnungen{RESET}")
    elif total_err == 0:
        print(f"{YELLOW}{BOLD}⚠ OK — {total_pass} bestanden, {total_warn} Warnung(en), 0 Fehler{RESET}")
    else:
        print(f"{RED}{BOLD}✗ {total_err} FEHLER, {total_warn} Warnung(en), {total_pass} bestanden{RESET}")

    return total_err, total_warn, total_pass


# ─── Main ─────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) < 2:
        # Alle HTML-Dateien im aktuellen Verzeichnis
        files = sorted(glob.glob('DE_A2_2*.html'))
        # Backup-Dateien ausschließen
        files = [f for f in files if '.backup.' not in f]
    else:
        files = sys.argv[1:]

    if not files:
        print("Keine Dateien gefunden.")
        sys.exit(1)

    total_files = len(files)
    total_errors = 0
    total_warnings = 0
    file_results = []

    for f in files:
        errs, warns, passes = check_file(f)
        total_errors += errs
        total_warnings += warns
        file_results.append((os.path.basename(f), errs, warns, passes))

    # Gesamtübersicht
    print(f"\n\n{'═'*60}")
    print(f"{BOLD}GESAMTÜBERSICHT — {total_files} Dateien geprüft{RESET}")
    print(f"{'═'*60}")

    for name, errs, warns, passes in file_results:
        status = f"{GREEN}✓{RESET}" if errs == 0 else f"{RED}✗{RESET}"
        warn_str = f" {YELLOW}({warns} ⚠){RESET}" if warns > 0 else ""
        print(f"  {status} {name}: {passes} ✓, {errs} ✗{warn_str}")

    print(f"\n  Gesamt: {RED}{total_errors} Fehler{RESET}, {YELLOW}{total_warnings} Warnungen{RESET}")

    if total_errors > 0:
        print(f"\n{RED}{BOLD}✗ NICHT BEREIT — Fehler müssen erst behoben werden!{RESET}")
        sys.exit(1)
    else:
        print(f"\n{GREEN}{BOLD}✓ ALLE DATEIEN BESTANDEN{RESET}")
        sys.exit(0)
