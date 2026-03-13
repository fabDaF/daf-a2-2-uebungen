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
    lower_matches = re.findall(r'(liveCheck|wortschatzCheck|checkWs|makeWsInp)[^}]*toLowerCase', content, re.DOTALL)
    if lower_matches:
        errors.append(fail(f"toLowerCase() in Feedback-Funktionen gefunden — VERBOTEN"))
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
