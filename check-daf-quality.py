#!/usr/bin/env python3
"""
DaF HTML Quality Checker — Prüfskript für alle DaF-Übungsdateien
================================================================
Prüft HTML-Dateien gegen die verbindlichen Skill-Spezifikationen:
  - daf-html-layout (Layout, Nav, Footer, Container)
  - satzbau-drag-drop (Chip-CSS, satzbauData, Komma-Handling, Lösungen-Button)
  - daf-uebungsformen (Live-Feedback, Wortschatz-Pattern)
  - daf-pluralendungen (Umlaut-Konvention)
  - Allgemein: Timer-IDs, Anführungszeichen, Responsive

Aufruf:
  python3 check-daf-quality.py DATEI.html
  python3 check-daf-quality.py *.html
  python3 check-daf-quality.py --summary *.html
"""

import sys, re, os, glob, json
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════
# FARBEN
# ═══════════════════════════════════════════════════════════════════════
GREEN  = '\033[92m'
RED    = '\033[91m'
YELLOW = '\033[93m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

def ok(msg):    return f"  {GREEN}✓{RESET} {msg}"
def fail(msg):  return f"  {RED}✗{RESET} {msg}"
def warn(msg):  return f"  {YELLOW}⚠{RESET} {msg}"
def info(msg):  return f"  {CYAN}ℹ{RESET} {msg}"

# ═══════════════════════════════════════════════════════════════════════
# HILFSFUNKTIONEN
# ═══════════════════════════════════════════════════════════════════════

def extract_style_block(html):
    """Extrahiere den gesamten <style>-Block."""
    m = re.search(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ''

def extract_script_block(html):
    """Extrahiere den gesamten <script>-Block."""
    m = re.search(r'<script[^>]*>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ''

def has_css_prop(css, selector, prop, value=None):
    """Prüfe ob ein CSS-Selektor eine bestimmte Property hat."""
    # Einfache Regex-basierte Prüfung
    pattern = re.escape(selector) + r'\s*\{([^}]*)\}'
    m = re.search(pattern, css, re.DOTALL)
    if not m:
        return False
    block = m.group(1)
    if value is None:
        return prop in block
    return re.search(re.escape(prop) + r'\s*:\s*' + re.escape(value), block) is not None

def css_contains(css, text):
    """Prüfe ob der CSS-Block einen bestimmten Text enthält."""
    return text in css

# ═══════════════════════════════════════════════════════════════════════
# PRÜFMODULE
# ═══════════════════════════════════════════════════════════════════════

def check_layout(html, css, js, results):
    """Prüfungen aus daf-html-layout Skill."""
    cat = 'Layout'

    # Body-Hintergrund: lila Gradient
    if 'linear-gradient(135deg, #667eea' in css and '#764ba2' in css:
        results['pass'].append((cat, 'Body: lila Gradient vorhanden'))
    else:
        results['fail'].append((cat, 'Body: lila Gradient fehlt (linear-gradient(135deg, #667eea 0%, #764ba2 100%))'))

    # Container
    if 'max-width: 1000px' in css or 'max-width:1000px' in css:
        results['pass'].append((cat, 'Container: max-width 1000px'))
    else:
        results['fail'].append((cat, 'Container: max-width 1000px fehlt'))

    if 'border-radius: 12px' in css or 'border-radius:12px' in css:
        results['pass'].append((cat, 'Container: border-radius 12px'))
    elif 'border-radius: 16px' in css or 'border-radius:16px' in css:
        results['fail'].append((cat, 'Container: border-radius 16px (sollte 12px sein)'))

    if 'overflow: hidden' in css or 'overflow:hidden' in css:
        results['pass'].append((cat, 'Container: overflow hidden'))
    else:
        results['fail'].append((cat, 'Container: overflow hidden fehlt'))

    if '0 10px 40px rgba(0,0,0,0.2)' in css:
        results['pass'].append((cat, 'Container: box-shadow korrekt'))
    elif 'box-shadow' in css:
        results['warn'].append((cat, 'Container: box-shadow vorhanden aber möglicherweise abweichend'))
    else:
        results['fail'].append((cat, 'Container: box-shadow fehlt'))

    # Header — kein Foto
    if re.search(r'\.header\s*\{[^}]*background-image', css, re.DOTALL):
        results['fail'].append((cat, 'Header: background-image im Header (VERBOTEN)'))
    else:
        results['pass'].append((cat, 'Header: kein Foto im Header'))

    # Header Font
    if 'Georgia' in css and 'serif' in css:
        results['pass'].append((cat, 'Header: Georgia serif Schrift'))
    else:
        results['warn'].append((cat, 'Header: Georgia serif Schrift nicht erkannt'))

def check_nav(html, css, js, results):
    """Prüfungen der Nav-Leiste."""
    cat = 'Navigation'

    # Nav flex-wrap: nowrap
    nav_match = re.search(r'\.nav\s*\{([^}]*)\}', css, re.DOTALL)
    if nav_match:
        nav_css = nav_match.group(1)
        if 'flex-wrap: nowrap' in nav_css or 'flex-wrap:nowrap' in nav_css:
            results['pass'].append((cat, 'Nav: flex-wrap: nowrap'))
        elif 'flex-wrap: wrap' in nav_css or 'flex-wrap:wrap' in nav_css:
            results['fail'].append((cat, 'Nav: flex-wrap: wrap (sollte nowrap sein, wrap nur in @media)'))

        # Nav Borders
        if 'border-top' in nav_css:
            results['pass'].append((cat, 'Nav: border-top vorhanden'))
        else:
            results['fail'].append((cat, 'Nav: border-top fehlt'))

        if 'border-left' in nav_css:
            results['pass'].append((cat, 'Nav: border-left vorhanden'))
        else:
            results['fail'].append((cat, 'Nav: border-left fehlt'))
    else:
        results['fail'].append((cat, 'Nav: .nav CSS-Block nicht gefunden'))

    # Nav-Btn: Emoji über Text (flex-direction: column)
    navbtn_match = re.search(r'\.nav-btn\s*\{([^}]*)\}', css, re.DOTALL)
    if navbtn_match:
        navbtn_css = navbtn_match.group(1)
        if 'flex-direction: column' in navbtn_css or 'flex-direction:column' in navbtn_css:
            results['pass'].append((cat, 'Nav-Btn: flex-direction column (Emoji über Text)'))
        else:
            results['fail'].append((cat, 'Nav-Btn: flex-direction column fehlt'))

        if 'border-right' in navbtn_css and 'border-bottom' in navbtn_css:
            results['pass'].append((cat, 'Nav-Btn: border-right + border-bottom'))
        else:
            results['fail'].append((cat, 'Nav-Btn: border-right und/oder border-bottom fehlt'))

    # Nav-Emoji und Nav-Label Spans im HTML
    if '<span class="nav-emoji">' in html:
        results['pass'].append((cat, 'Nav: <span class="nav-emoji"> Struktur'))
    else:
        results['warn'].append((cat, 'Nav: <span class="nav-emoji"> nicht gefunden (Emoji evtl. inline)'))

    if '<span class="nav-label">' in html:
        results['pass'].append((cat, 'Nav: <span class="nav-label"> Struktur'))
    else:
        results['warn'].append((cat, 'Nav: <span class="nav-label"> nicht gefunden'))

    # Nav-Btn active: border-bottom: 3px solid #667eea
    if re.search(r'\.nav-btn\.active\s*\{[^}]*border-bottom:\s*3px\s+solid\s+#667eea', css, re.DOTALL):
        results['pass'].append((cat, 'Nav-Btn active: border-bottom 3px solid #667eea'))
    else:
        results['warn'].append((cat, 'Nav-Btn active: border-bottom 3px solid #667eea nicht erkannt'))

    # Mobile Responsive
    if '@media' in css and 'max-width' in css:
        results['pass'].append((cat, 'Mobile: @media Query vorhanden'))
        if 'flex: 1 1 33%' in css:
            results['pass'].append((cat, 'Mobile: flex: 1 1 33% für Nav-Buttons'))
        else:
            results['warn'].append((cat, 'Mobile: flex: 1 1 33% nicht gefunden'))
    else:
        results['fail'].append((cat, 'Mobile: @media Query fehlt komplett'))

def check_footer(html, css, js, results):
    """Prüfungen des Footers."""
    cat = 'Footer'

    if 'author-footer' in html:
        results['pass'].append((cat, 'Footer: .author-footer vorhanden'))
    else:
        results['fail'].append((cat, 'Footer: .author-footer fehlt'))
        return

    if 'Frank Burkert' in html:
        results['pass'].append((cat, 'Footer: © Frank Burkert'))
    else:
        results['warn'].append((cat, 'Footer: Frank Burkert nicht gefunden'))

    # Footer innerhalb Container (vor </div><!-- /container -->)
    # Einfache Heuristik: author-footer kommt VOR dem letzten </div> vor <script>
    footer_pos = html.find('author-footer')
    script_pos = html.find('<script')
    container_end = html.rfind('</div>', 0, script_pos) if script_pos > 0 else -1

    if footer_pos > 0 and container_end > 0 and footer_pos < container_end:
        results['pass'].append((cat, 'Footer: innerhalb von .container'))
    else:
        results['warn'].append((cat, 'Footer: Position relativ zu Container nicht eindeutig prüfbar'))

def check_satzbau(html, css, js, results):
    """Prüfungen aus satzbau-drag-drop Skill."""
    cat = 'Satzbau'

    # Prüfe ob Satzbau-Tab überhaupt existiert
    if 'satzbauData' not in js and 'satzbauData' not in html:
        results['info'].append((cat, 'Kein Satzbau-Tab in dieser Datei'))
        return

    results['info'].append((cat, 'Satzbau-Tab erkannt'))

    # 1. Chip-CSS: weiß + #667eea Rand
    chip_match = re.search(r'\.chip\s*\{([^}]*)\}', css, re.DOTALL)
    if chip_match:
        chip_css = chip_match.group(1)
        if 'background: white' in chip_css or 'background:white' in chip_css:
            results['pass'].append((cat, 'Chip: background white'))
        elif 'linear-gradient' in chip_css:
            results['fail'].append((cat, 'Chip: linear-gradient (VERBOTEN — muss white sein)'))
        else:
            results['warn'].append((cat, 'Chip: background nicht als "white" erkannt'))

        if '#667eea' in chip_css:
            results['pass'].append((cat, 'Chip: #667eea Rand/Farbe'))
        else:
            results['fail'].append((cat, 'Chip: #667eea fehlt in .chip CSS'))
    else:
        results['fail'].append((cat, 'Chip: .chip CSS-Block nicht gefunden'))

    # 2. Chip correct/incorrect: solid grün/rot mit weißem Text
    if re.search(r'\.chip\.correct\s*\{[^}]*background:\s*#27ae60', css, re.DOTALL):
        results['pass'].append((cat, 'Chip correct: solid grün (#27ae60)'))
    else:
        results['fail'].append((cat, 'Chip correct: solid #27ae60 nicht gefunden'))

    if re.search(r'\.chip\.incorrect\s*\{[^}]*background:\s*#e74c3c', css, re.DOTALL):
        results['pass'].append((cat, 'Chip incorrect: solid rot (#e74c3c)'))
    else:
        results['fail'].append((cat, 'Chip incorrect: solid #e74c3c nicht gefunden'))

    # 3. satzbauData Kapitalisierung prüfen
    sb_match = re.search(r'var\s+satzbauData\s*=\s*\[(.*?)\];', js, re.DOTALL)
    if not sb_match:
        sb_match = re.search(r'var\s+satzbauData\s*=\s*\[(.*?)\];', html, re.DOTALL)

    if sb_match:
        sb_block = sb_match.group(1)
        # Extrahiere parts-Arrays
        parts_matches = re.findall(r"parts:\s*\[([^\]]+)\]", sb_block)
        cap_errors = []
        for pm in parts_matches:
            words = re.findall(r"'([^']*)'", pm)
            for w in words:
                if not w or w in [',', ';']:
                    continue
                first = w[0]
                # Nomen/Eigennamen: großgeschrieben ist OK
                # Alles andere: muss klein sein
                # Heuristik: Wenn es mit Großbuchstabe beginnt, sollte es ein Nomen sein
                # Kritischer Test: Verben, Artikel, Pronomen, Adverbien die groß sind
                lowercase_words = ['ich', 'du', 'er', 'sie', 'es', 'wir', 'ihr', 'mich', 'dich', 'sich',
                                   'der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einen', 'einem', 'einer',
                                   'und', 'oder', 'aber', 'denn', 'weil', 'dass', 'wenn', 'als', 'ob', 'obwohl',
                                   'nicht', 'kein', 'keine', 'keinen', 'keinem', 'sehr', 'ganz', 'schon', 'noch',
                                   'auch', 'nur', 'immer', 'nie', 'oft', 'hier', 'dort', 'wo', 'wie', 'was', 'wer',
                                   'bin', 'bist', 'ist', 'sind', 'seid', 'hat', 'habe', 'haben', 'wird', 'werden',
                                   'kann', 'muss', 'soll', 'will', 'darf', 'mag', 'möchte',
                                   'mit', 'von', 'zu', 'bei', 'nach', 'aus', 'für', 'über', 'unter', 'in', 'an', 'auf',
                                   'vor', 'hinter', 'zwischen', 'neben', 'ohne', 'gegen', 'um', 'durch', 'wegen',
                                   'dieser', 'diese', 'dieses', 'diesem', 'diesen', 'jeder', 'jede', 'jedes',
                                   'mein', 'dein', 'sein', 'ihr', 'unser', 'euer',
                                   'am', 'im', 'zum', 'zur', 'vom', 'beim', 'ins', 'ans',
                                   'es', 'man', 'etwas', 'alles', 'nichts', 'viel', 'wenig',
                                   'dann', 'danach', 'davor', 'zuerst', 'zuletzt', 'leider', 'wirklich',
                                   'so', 'ja', 'nein', 'doch']
                if w.lower() in lowercase_words and w[0].isupper():
                    # Sie (Höflichkeitsform) darf groß sein
                    if w == 'Sie':
                        continue
                    cap_errors.append(w)

        if cap_errors:
            results['fail'].append((cat, f'satzbauData Kapitalisierung: {", ".join(set(cap_errors))} — sollte(n) klein geschrieben sein'))
        else:
            results['pass'].append((cat, 'satzbauData: Kapitalisierung korrekt'))

        # 4. Komma als eigener Chip prüfen
        # Suche nach Wörtern mit angehängtem Komma
        glued_commas = re.findall(r"'(\w+[,;])'", sb_block)
        if glued_commas:
            results['fail'].append((cat, f'Komma am Wort geklebt: {", ".join(glued_commas)} — Komma muss eigener Chip sein'))
        else:
            results['pass'].append((cat, 'satzbauData: keine angeklebten Kommas'))

        # Prüfe ob Kommas in parts sind → dann muss punct-chip CSS vorhanden sein
        has_commas = "',' " in sb_block or "','" in sb_block
        if has_commas:
            if 'punct-chip' in css:
                results['pass'].append((cat, 'punct-chip CSS vorhanden (Komma in Daten)'))
            else:
                results['fail'].append((cat, 'Kommas in satzbauData aber KEIN punct-chip CSS'))

            # sbMakeChip muss punct-chip setzen
            if "punct-chip" in js or "punct-chip" in html:
                results['pass'].append((cat, 'sbMakeChip: punct-chip Klasse wird gesetzt'))
            else:
                results['fail'].append((cat, 'sbMakeChip: punct-chip Klasse wird NICHT gesetzt'))

            # sbUpdateCapitalization muss Komma skippen
            if ("orig === ','" in js or "orig === ','" in html or
                'orig === \\x27,\\x27' in js):
                results['pass'].append((cat, 'sbUpdateCapitalization: Komma-Skip vorhanden'))
            else:
                # Auch alternativen Regex-Check
                if re.search(r"orig\s*===?\s*['\"][\,;]['\"]", js) or re.search(r"orig\s*===?\s*['\"][\,;]['\"]", html):
                    results['pass'].append((cat, 'sbUpdateCapitalization: Komma-Skip vorhanden'))
                else:
                    results['fail'].append((cat, 'sbUpdateCapitalization: Komma-Skip FEHLT'))
    else:
        results['fail'].append((cat, 'satzbauData nicht gefunden'))

    # 5. sb-label (Satz 1, Satz 2...)
    if 'sb-label' in js or 'sb-label' in html:
        results['pass'].append((cat, 'sb-label: dynamisch erzeugt'))
    else:
        results['fail'].append((cat, 'sb-label: nicht gefunden — "Satz 1", "Satz 2" fehlt'))

    # 6. Globaler Lösungen-Button: kein .sb-row Selector
    # Suche nach dem Satzbau-Lösungen-Button
    if "querySelectorAll('.sb-row')" in html or "querySelectorAll('.sb-row')" in js:
        results['fail'].append((cat, 'Lösungen-Button: verwendet .sb-row (existiert nicht!) — muss for-loop oder satzbauData.forEach verwenden'))
    else:
        results['pass'].append((cat, 'Lösungen-Button: kein fehlerhafter .sb-row-Selektor'))

    # 7. satzbauContainer vorhanden
    if 'satzbauContainer' in html:
        results['pass'].append((cat, 'satzbauContainer: div vorhanden'))
    else:
        results['fail'].append((cat, 'satzbauContainer: div fehlt'))

    # 8. Pflichtfunktionen
    for fn in ['sbShowSolution', 'sbResetOne', 'sbCheckAuto', 'sbColorRow', 'sbUpdateCapitalization', 'sbMakeChip', 'initSatzbau']:
        source = js if fn in js else html
        if fn in source:
            results['pass'].append((cat, f'Funktion {fn}() vorhanden'))
        else:
            results['fail'].append((cat, f'Funktion {fn}() FEHLT'))

    # 9. Chip-Granularität: Suche nach zusammengesetzten Chips (Verb+Pronomen)
    if sb_match:
        sb_block = sb_match.group(1)
        multi_word_chips = []
        words_in_parts = re.findall(r"'([^']*)'", sb_block)
        for w in words_in_parts:
            if w in [',', ';', '']:
                continue
            # Mehr als ein Wort? (Ausnahme: Artikel+Nomen ist OK)
            parts = w.split()
            if len(parts) > 1:
                # Erlaubt: Artikel + Nomen (der Brief, das Paket)
                articles = ['der', 'die', 'das', 'den', 'dem', 'des', 'ein', 'eine', 'einen', 'einem', 'einer', 'kein', 'keine', 'keinen']
                if parts[0].lower() in articles and len(parts) == 2:
                    continue
                multi_word_chips.append(w)

        if multi_word_chips:
            results['warn'].append((cat, f'Mehrteilige Chips: {", ".join(multi_word_chips[:5])} — prüfe ob auftrennbar'))
        else:
            results['pass'].append((cat, 'Chip-Granularität: keine mehrteiligen Chips'))

def check_timer(html, css, js, results):
    """Prüfungen der Timer-Verdrahtung."""
    cat = 'Timer'

    # Timer-IDs: timer-N und best-N (mit Bindestrich)
    timer_ids = re.findall(r'id="(timer[^"]*)"', html)
    best_ids = re.findall(r'id="(best[^"]*)"', html)

    # Alte IDs ohne Bindestrich?
    old_timer = [t for t in timer_ids if re.match(r'^timer\d+$', t)]  # timer5 statt timer-5
    old_best = [b for b in best_ids if re.match(r'^best\d+$', b)]

    correct_timer = [t for t in timer_ids if re.match(r'^timer-\d+$', t)]
    correct_best = [b for b in best_ids if re.match(r'^best-\d+$', b)]

    if old_timer:
        results['fail'].append((cat, f'Alte Timer-IDs ohne Bindestrich: {", ".join(old_timer)} (korrekt: timer-N)'))
    if old_best:
        results['fail'].append((cat, f'Alte Best-IDs ohne Bindestrich: {", ".join(old_best)} (korrekt: best-N)'))

    if correct_timer:
        results['pass'].append((cat, f'Timer-IDs korrekt: {", ".join(correct_timer)}'))
    if correct_best:
        results['pass'].append((cat, f'Best-IDs korrekt: {", ".join(correct_best)}'))

    # Alte t0/b0 Pattern
    old_t = re.findall(r'id="(t\d+)"', html)
    old_b = re.findall(r'id="(b\d+)"', html)
    if old_t:
        results['fail'].append((cat, f'VERBOTEN: id="tN" Pattern: {", ".join(old_t)} (korrekt: timer-N)'))
    if old_b:
        results['fail'].append((cat, f'VERBOTEN: id="bN" Pattern: {", ".join(old_b)} (korrekt: best-N)'))

    # fmtTime vs timerFmt — Warnung statt Fehler (A2.2 verwendet durchgängig timerFmt)
    if 'timerFmt' in js or 'timerFmt' in html:
        if 'fmtTime' not in js and 'fmtTime' not in html:
            results['warn'].append((cat, 'timerFmt() statt fmtTime() — bei nächster Migration angleichen'))
        else:
            results['warn'].append((cat, 'Sowohl timerFmt() als auch fmtTime() vorhanden — bereinigen'))

    # loadBests vs loadBestTimes
    if 'loadBests' in js and 'loadBestTimes' not in js:
        results['fail'].append((cat, 'VERBOTEN: loadBests() — korrekt ist loadBestTimes()'))

def check_wortschatz(html, css, js, results):
    """Prüfungen des Wortschatz-Tabs."""
    cat = 'Wortschatz'

    if 'WORTSCHATZ' not in js and 'WORTSCHATZ' not in html:
        results['info'].append((cat, 'Kein Wortschatz-Tab in dieser Datei'))
        return

    results['info'].append((cat, 'Wortschatz-Tab erkannt'))

    # Verbotene alte Patterns
    for old_class in ['ws-table', 'ws-inp', 'ws-en', 'ws-row', 'ws-grid']:
        if old_class in css or old_class in html:
            results['fail'].append((cat, f'VERBOTEN: .{old_class} — altes Wortschatz-Pattern'))

    if '<table' in html and 'wortschatz' in html.lower():
        # Nur warnen wenn table im Wortschatz-Kontext
        results['warn'].append((cat, 'HTML <table> gefunden — Wortschatz sollte div-basiert sein'))

    # vocabContainer oder wortschatzContainer
    if 'vocabContainer' in html or 'wortschatzContainer' in html:
        results['pass'].append((cat, 'Wortschatz-Container: div vorhanden'))
    else:
        results['warn'].append((cat, 'vocabContainer/wortschatzContainer nicht gefunden'))

    # Placeholder: Artikel (nicht der/die/das)
    if re.search(r"placeholder\s*[:=]\s*['\"]der/die/das['\"]", html) or \
       re.search(r"placeholder\s*[:=]\s*['\"]der/die/das['\"]", js):
        results['fail'].append((cat, 'Placeholder "der/die/das" VERBOTEN — muss "Artikel" sein'))

    # wortschatzCheck statt liveCheck im Wortschatz
    if 'wortschatzCheck' in js or 'wortschatzCheck' in html:
        results['pass'].append((cat, 'wortschatzCheck() verwendet (case-sensitive für Nomen)'))
    elif 'vocabLiveCheck' in js or 'vocabLiveCheck' in html:
        results['pass'].append((cat, 'vocabLiveCheck() verwendet'))
    elif 'WORTSCHATZ' in js or 'WORTSCHATZ' in html:
        results['warn'].append((cat, 'Wortschatz vorhanden aber keine dedizierte Check-Funktion erkannt'))

def check_lueckentext(html, css, js, results):
    """Prüfungen des Lückentext-Tabs."""
    cat = 'Lückentext'

    if 'luecken-inp' not in html and 'luecken-inp' not in css:
        results['info'].append((cat, 'Kein Lückentext-Tab erkannt'))
        return

    results['info'].append((cat, 'Lückentext-Tab erkannt'))

    # Live-Feedback CSS
    if '.luecken-inp.ok' in css or '.luecken-inp.ok' in html:
        results['pass'].append((cat, 'CSS .luecken-inp.ok (grün) vorhanden'))
    elif '.ok' in css:
        results['pass'].append((cat, 'CSS .ok vorhanden (generisch)'))
    else:
        results['warn'].append((cat, '.luecken-inp.ok CSS nicht gefunden'))

    if '.luecken-inp.no' in css or '.luecken-inp.no' in html:
        results['pass'].append((cat, 'CSS .luecken-inp.no (rot) vorhanden'))
    elif '.no' in css:
        results['pass'].append((cat, 'CSS .no vorhanden (generisch)'))

def check_genus(html, css, js, results):
    """Prüfungen des Genus-Tabs (Drag-and-Drop der/die/das)."""
    cat = 'Genus'

    # Erkenne Genus-Tab anhand typischer Marker
    has_genus = ('genusData' in js or 'genusData' in html or
                 'der/die/das' in html.lower() or
                 'genus' in html.lower())

    if not has_genus:
        results['info'].append((cat, 'Kein Genus-Tab erkannt'))
        return

    results['info'].append((cat, 'Genus-Tab erkannt'))

def check_anfuehrungszeichen(html, results):
    """Prüfe deutsche Anführungszeichen."""
    cat = 'Anführungszeichen'

    # Suche nach „ (U+201E) gefolgt von " (U+0022) oder " (U+201D) — falsch
    # Korrekt: „ (U+201E) + " (U+201C)

    # Finde alle „..."-Paare
    correct_pairs = len(re.findall(r'\u201e[^\u201c\u201d\u0022]{1,200}\u201c', html))
    wrong_ascii = len(re.findall(r'\u201e[^\u201c\u201d\u0022]{1,200}"', html))
    wrong_english = len(re.findall(r'\u201e[^\u201c\u201d\u0022]{1,200}\u201d', html))

    if correct_pairs > 0:
        results['pass'].append((cat, f'{correct_pairs} korrekte „…\u201c Paare'))

    if wrong_ascii > 0:
        results['fail'].append((cat, f'{wrong_ascii}× „…" — ASCII-Schließzeichen statt \u201c'))

    if wrong_english > 0:
        results['fail'].append((cat, f'{wrong_english}× „…\u201d — englisches Schließzeichen statt \u201c'))

def check_pluralendungen(html, js, results):
    """Prüfe Pluralendungen-Konvention (Combining Diaeresis U+0308)."""
    cat = 'Pluralendungen'

    # Suche nach Pluralhinweisen in JS-Daten
    # Falsch: -äe, -öer, etc.
    wrong_patterns = re.findall(r'["\']-(ä|ö|ü)(e|er|en|n)["\']', js + html)
    if wrong_patterns:
        results['fail'].append((cat, f'Falsche Pluralendung: -{wrong_patterns[0][0]}{wrong_patterns[0][1]} — muss -\\u0308{wrong_patterns[0][1]} sein'))

    # Korrekt: \u0308 verwendet
    if '\\u0308' in js or '\\u0308' in html or '\u0308' in html:
        results['pass'].append((cat, 'Combining Diaeresis (U+0308) wird verwendet'))

def check_control_bar(html, css, js, results):
    """Prüfe control-bar Pattern (Buttons links, Timer rechts, eine Zeile)."""
    cat = 'Control-Bar'

    if 'control-bar' in css or 'control-bar' in html:
        results['pass'].append((cat, 'control-bar Pattern erkannt'))
    elif 'timer-bar' in css or 'timer-bar' in html:
        results['warn'].append((cat, 'timer-bar statt control-bar — möglicherweise altes Pattern'))
    elif 'timer-row' in css or 'timer-row' in html:
        results['warn'].append((cat, 'timer-row — möglicherweise getrenntes Timer/Button-Layout'))

def check_images(html, results):
    """Prüfe Bildanzahl und -qualität."""
    cat = 'Bilder'

    # Zähle Base64-Bilder
    base64_count = len(re.findall(r'src="data:image/', html))
    # Zähle externe Bilder (Pexels etc.)
    pexels_count = len(re.findall(r'src="https://images\.pexels\.com/', html))
    ext_count = len(re.findall(r'src="https?://', html))

    total_images = base64_count + ext_count

    if total_images >= 8:
        results['pass'].append((cat, f'{total_images} Bilder (min. 8 Pflicht): {base64_count} Base64, {ext_count} extern'))
    elif total_images > 0:
        results['warn'].append((cat, f'Nur {total_images} Bilder (Pflicht: min. 8): {base64_count} Base64, {ext_count} extern'))
    else:
        results['warn'].append((cat, 'Keine Bilder gefunden'))

    # Externe Bilder müssen als Base64 eingebettet sein (Pexels-Skill)
    if pexels_count > 0:
        results['fail'].append((cat, f'{pexels_count} externe Pexels-Bilder gefunden — müssen als Base64 eingebettet werden'))
    elif base64_count > 0:
        results['pass'].append((cat, f'Alle Bilder als Base64 eingebettet (keine externen Pexels-URLs)'))

    # Prüfe doppelte Bilder (Base64-Hashes vergleichen — 200 Zeichen statt 50 für echte Unterscheidung)
    b64_images = re.findall(r'src="(data:image/[^"]{100,200})', html)
    if len(b64_images) != len(set(b64_images)):
        results['warn'].append((cat, 'Mögliche Bild-Duplikate erkannt (gleiche Base64-Daten)'))

def check_showsection(html, js, results):
    """Prüfe showSection-Funktion."""
    cat = 'Tabs'

    if 'showSection' in js or 'showSection' in html:
        results['pass'].append((cat, 'showSection() Funktion vorhanden'))
    elif 'showTab' in js or 'showTab' in html:
        results['pass'].append((cat, 'showTab() Funktion vorhanden (Alternative zu showSection)'))
    else:
        results['fail'].append((cat, 'showSection()/showTab() fehlt'))

    # Zähle Sections und Nav-Buttons
    sections = len(re.findall(r'class="section', html))
    navbtns = len(re.findall(r'class="nav-btn', html))

    results['info'].append((cat, f'{sections} Sections, {navbtns} Nav-Buttons'))

    if sections > 0 and navbtns > 0 and sections != navbtns:
        results['warn'].append((cat, f'Mismatch: {sections} Sections vs. {navbtns} Nav-Buttons'))

# ═══════════════════════════════════════════════════════════════════════
# HAUPTLOGIK
# ═══════════════════════════════════════════════════════════════════════

def check_file(filepath):
    """Führe alle Prüfungen für eine Datei durch."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    css = extract_style_block(html)
    js = extract_script_block(html)

    results = {
        'pass': [],
        'fail': [],
        'warn': [],
        'info': []
    }

    # Alle Module ausführen
    check_layout(html, css, js, results)
    check_nav(html, css, js, results)
    check_footer(html, css, js, results)
    check_satzbau(html, css, js, results)
    check_timer(html, css, js, results)
    check_wortschatz(html, css, js, results)
    check_lueckentext(html, css, js, results)
    check_genus(html, css, js, results)
    check_anfuehrungszeichen(html, results)
    check_pluralendungen(html, js, results)
    check_control_bar(html, css, js, results)
    check_images(html, results)
    check_showsection(html, js, results)

    return results

def print_results(filepath, results):
    """Ergebnisse formatiert ausgeben."""
    filename = os.path.basename(filepath)
    n_pass = len(results['pass'])
    n_fail = len(results['fail'])
    n_warn = len(results['warn'])

    print(f"\n{BOLD}{'═' * 70}{RESET}")
    print(f"{BOLD}  {filename}{RESET}")
    print(f"{'═' * 70}")

    # Info
    if results['info']:
        for cat, msg in results['info']:
            print(info(f"[{cat}] {msg}"))
        print()

    # Fehler
    if results['fail']:
        print(f"  {RED}{BOLD}FEHLER ({n_fail}):{RESET}")
        for cat, msg in results['fail']:
            print(fail(f"[{cat}] {msg}"))
        print()

    # Warnungen
    if results['warn']:
        print(f"  {YELLOW}{BOLD}WARNUNGEN ({n_warn}):{RESET}")
        for cat, msg in results['warn']:
            print(warn(f"[{cat}] {msg}"))
        print()

    # Bestanden
    if results['pass']:
        print(f"  {GREEN}{BOLD}BESTANDEN ({n_pass}):{RESET}")
        for cat, msg in results['pass']:
            print(ok(f"[{cat}] {msg}"))

    # Zusammenfassung
    print()
    if n_fail == 0 and n_warn == 0:
        print(f"  {GREEN}{BOLD}✓ ALLES OK — {n_pass} Prüfungen bestanden{RESET}")
    elif n_fail == 0:
        print(f"  {YELLOW}{BOLD}⚠ {n_pass} bestanden, {n_warn} Warnungen{RESET}")
    else:
        print(f"  {RED}{BOLD}✗ {n_fail} FEHLER, {n_warn} Warnungen, {n_pass} bestanden{RESET}")

    return n_fail, n_warn, n_pass

def print_summary(all_results):
    """Gesamtübersicht für alle Dateien."""
    print(f"\n{BOLD}{'═' * 70}{RESET}")
    print(f"{BOLD}  GESAMTÜBERSICHT{RESET}")
    print(f"{'═' * 70}\n")

    total_fail = 0
    total_warn = 0
    total_pass = 0

    for filepath, (n_fail, n_warn, n_pass) in all_results:
        filename = os.path.basename(filepath)
        total_fail += n_fail
        total_warn += n_warn
        total_pass += n_pass

        if n_fail == 0 and n_warn == 0:
            status = f"{GREEN}✓ OK{RESET}"
        elif n_fail == 0:
            status = f"{YELLOW}⚠ {n_warn}W{RESET}"
        else:
            status = f"{RED}✗ {n_fail}F {n_warn}W{RESET}"

        print(f"  {status}  {filename}  ({n_pass}✓)")

    print(f"\n  {'─' * 50}")
    print(f"  {BOLD}Gesamt: {total_pass} ✓  {total_fail} ✗  {total_warn} ⚠  ({len(all_results)} Dateien){RESET}")

    if total_fail == 0:
        print(f"  {GREEN}{BOLD}Alle Dateien fehlerfrei!{RESET}")
    else:
        print(f"  {RED}{BOLD}{total_fail} Fehler müssen behoben werden.{RESET}")

# ═══════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    args = sys.argv[1:]

    if not args:
        print(f"{YELLOW}Aufruf: python3 check-daf-quality.py [--summary] DATEI.html [DATEI2.html ...]{RESET}")
        print(f"  --summary  Nur Gesamtübersicht (ohne Details)")
        sys.exit(1)

    summary_only = '--summary' in args
    files = [a for a in args if a != '--summary']

    # Glob-Expansion
    expanded = []
    for f in files:
        if '*' in f:
            expanded.extend(glob.glob(f))
        else:
            expanded.append(f)

    files = [f for f in expanded if f.endswith('.html') and not f.endswith('.backup.html')]

    if not files:
        print(f"{RED}Keine HTML-Dateien gefunden.{RESET}")
        sys.exit(1)

    all_results = []
    for filepath in sorted(files):
        if not os.path.exists(filepath):
            print(f"{RED}Datei nicht gefunden: {filepath}{RESET}")
            continue

        results = check_file(filepath)

        if not summary_only:
            counts = print_results(filepath, results)
        else:
            counts = (len(results['fail']), len(results['warn']), len(results['pass']))

        all_results.append((filepath, counts))

    if len(all_results) > 1 or summary_only:
        print_summary(all_results)
