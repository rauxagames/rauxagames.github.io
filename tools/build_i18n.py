"""Genera les pàgines estàtiques per idioma de la web de Rauxa Games (SEO).

Fonts de veritat (estructura + diccionari JS `I18N` de cada pàgina):
  src/estudi.html       la portada de l'estudi (tots els jocs)   → /            i /<xx>/
  src/antdefender.html  AntDefender                               → /antdefender/ i /antdefender/<xx>/
  src/cattower.html     Cat Tower                                 → /cattower/    i /cattower/<xx>/
Cada pàgina: la de sense idioma (x-default, contingut en anglès; el JS hi detecta l'idioma) i una per idioma amb el
text ja traduït a l'HTML (el que indexa Google). També escriu sitemap.xml (amb hreflang).
Les polítiques de privadesa no es generen: /privacy (AntDefender, l'URL que té la fitxa de Play: NO es mou) i
/cattower/privacy/.

Ús (des de l'arrel del repo):  py tools/build_i18n.py
Cal tornar-lo a executar sempre que es toqui una font de src/. És idempotent.
Joc nou: afegir-lo a GAMES i a PAGES, una font src/<joc>.html (es pot copiar cattower.html) i la seva fitxa a
src/estudi.html.

A les fonts, les rutes són des de l'arrel del lloc (img/..., privacy.html) i l'script les corregeix per a cada
carpeta. Atributs que entén:
  data-i18n="clau" (text), data-i18n-alt="clau" (alt d'una imatge), data-home-link (portada de l'estudi),
  data-game-link="joc" (pàgina d'un joc), data-play-link[="joc"] (Google Play), data-privacy-link[="joc"] (política).
"""
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://rauxagames.github.io/"
LASTMOD = "2026-11-13"
ROOT_LANG = "en"   # contingut estàtic de les pàgines x-default (coincideix amb el que veu Googlebot amb JS)
EMAIL = "rauxa.antdefender@gmail.com"

LANGS = ["ca", "en", "es", "fr", "de", "pt", "ru", "ja", "zh", "hi", "ar"]
NATIVE = {"ca": "Català", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch",
          "pt": "Português", "ru": "Русский", "ja": "日本語", "zh": "简体中文", "hi": "हिन्दी",
          "ar": "العربية"}
OG_LOCALE = {"ca": "ca_ES", "en": "en_US", "es": "es_ES", "fr": "fr_FR", "de": "de_DE",
             "pt": "pt_PT", "ru": "ru_RU", "ja": "ja_JP", "zh": "zh_CN", "hi": "hi_IN", "ar": "ar_AR"}
PLAY_HL = {"pt": "pt-PT", "zh": "zh-CN"}   # igual que playUrl() del JS

# Els jocs: paquet de Google Play (None = encara no hi és) i política de privadesa (ruta des de l'arrel)
GAMES = {
    "antdefender": {"name": "AntDefender", "package": "com.rauxagames.antdefender",
                    "privacy": "privacy.html", "privacy_langs": ["ca", "en", "es"], "languages": LANGS},
    "cattower": {"name": "Cat Tower", "package": None,   # posar "com.rauxagames.cattower" quan sigui a Play
                 "privacy": "cattower/privacy/", "privacy_langs": ["ca", "en", "es"],
                 "languages": ["ca"]},   # (el joc, de moment, només en català)
}
# Les pàgines: font, carpeta i imatge per compartir (1024 x 500)
PAGES = {
    "estudi": {"src": "src/estudi.html", "base": "", "og": "img/og-estudi.jpg"},
    "antdefender": {"src": "src/antdefender.html", "base": "antdefender/", "og": "img/og-image.jpg"},
    "cattower": {"src": "src/cattower.html", "base": "cattower/", "og": "img/cattower/og-image.jpg"},
}

esc_t = lambda v: html.escape(v, quote=False)
esc_a = lambda v: html.escape(v, quote=False).replace('"', "&quot;")


def play_base(game):
    pkg = GAMES[game]["package"]
    return "https://play.google.com/store/apps/details?id=" + pkg if pkg else None


def play_url(game, lang, page):
    base = play_base(game)
    if not base:
        return "#"
    ref = "utm_source%3Dweb%26utm_medium%3Dsite%26utm_campaign%3D" + ("landing_" if page == game else page + "_") + lang
    return base + "&hl=" + PLAY_HL.get(lang, lang) + "&referrer=" + ref


def page_url(page, lang):
    return SITE + PAGES[page]["base"] + (lang + "/" if lang else "")


def prefix_of(page, fixed):
    return "../" * (PAGES[page]["base"].count("/") + (1 if fixed else 0))


def privacy_href(game, lang, prefix):
    g = GAMES[game]
    return prefix + g["privacy"] + "#" + (lang if lang in g["privacy_langs"] else "en")


def parse_i18n(src, where):
    m = re.search(r"var I18N = \{\n(.*?)\n  \};", src, re.S)
    if not m:
        sys.exit("No trobo el diccionari I18N a " + where)
    out = {}
    for lm in re.finditer(r"^    (\w+): \{\n(.*?)\n    \}", m.group(1), re.S | re.M):
        d = {}
        for km in re.finditer(r'^      (\w+): ("(?:[^"\\]|\\.)*"),?$', lm.group(2), re.M):
            d[km.group(1)] = json.loads(km.group(2))
        out[lm.group(1)] = d
    missing = [l for l in LANGS if l not in out]
    if missing:
        sys.exit("Falten idiomes al diccionari de %s: %s" % (where, missing))
    keys = set(out["en"])
    for l in LANGS:
        falten = keys - set(out[l])
        if falten:
            sys.exit("A %s, l'idioma %s no té: %s" % (where, l, sorted(falten)))
    return out


def fmt(text, attrs, d):
    w = re.search(r'data-w="(\w+)"', attrs)
    a = re.search(r'data-a="([^"]*)"', attrs)
    b = re.search(r'data-b="([^"]*)"', attrs)
    return (text.replace("{w}", d[w.group(1)] if w else "", 1)
                .replace("{a}", a.group(1) if a else "", 1)
                .replace("{b}", b.group(1) if b else "", 1))


# ---------------------------------------------------------------- JSON-LD

def org():
    return {"@type": "Organization", "@id": SITE + "#org", "name": "Rauxa Games", "url": SITE,
            "logo": SITE + "img/rauxa-512.png", "email": EMAIL,
            "address": {"@type": "PostalAddress", "addressCountry": "AD"}}


def game_ld(game, desc):
    g = GAMES[game]
    url = page_url(game, None)
    play = play_base(game)
    if game == "antdefender":
        out = {"@type": ["VideoGame", "MobileApplication"], "@id": url + "#game", "name": "AntDefender",
               "alternateName": ["Ant Defender", "AntDefender: Ant Tower Defense"], "description": desc, "url": url,
               "image": SITE + "img/og-image.jpg",
               "screenshot": [SITE + "img/shot-combat.webp", SITE + "img/shot-base.webp", SITE + "img/shot-heroes.webp"],
               "genre": ["Tower defense", "Action", "Strategy"], "playMode": "SinglePlayer"}
    else:
        out = {"@type": ["VideoGame", "MobileApplication"], "@id": url + "#game", "name": "Cat Tower",
               "description": desc, "url": url, "image": SITE + "img/cattower/og-image.jpg",
               "screenshot": [SITE + "img/cattower/shot-%s.webp" % n for n in ("inici", "partida", "mapa", "cartes")],
               "genre": ["Strategy", "Casual", "Puzzle"], "playMode": ["SinglePlayer", "MultiPlayer"]}
    out.update({"gamePlatform": "Android", "operatingSystem": "Android", "applicationCategory": "GameApplication",
                "inLanguage": GAMES[game]["languages"], "author": {"@id": SITE + "#org"}, "publisher": {"@id": SITE + "#org"}})
    if play:
        out.update({"installUrl": play, "downloadUrl": play, "sameAs": [play],
                    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
                               "availability": "https://schema.org/InStock", "url": play}})
    return out


def ld_graph(page, lang, url, title, desc):
    site = {"@type": "WebSite", "@id": SITE + "#site", "url": SITE, "name": "Rauxa Games",
            "publisher": {"@id": SITE + "#org"}}
    webpage = {"@type": "WebPage", "@id": url + "#page", "url": url, "name": title, "inLanguage": lang,
               "isPartOf": {"@id": SITE + "#site"}}
    graph = [org(), site]
    if page == "estudi":
        webpage["about"] = {"@id": SITE + "#org"}
        graph.append({"@type": "ItemList", "@id": url + "#games", "name": "Rauxa Games",
                      "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": page_url(g, None),
                                           "name": GAMES[g]["name"]} for i, g in enumerate(GAMES)]})
    else:
        graph.append(game_ld(page, desc))
        webpage["about"] = {"@id": page_url(page, None) + "#game"}
    graph.append(webpage)
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1).replace("</", "<\\/")


def seo_block(page, lang, fixed, d, prefix):
    url = page_url(page, lang if fixed else None)
    title, desc = d["title"], d["metaDesc"]
    img = SITE + PAGES[page]["og"]
    # icona d'iPhone i favicon: el logo de l'estudi a la portada, la icona de cada joc a la seva pàgina
    icon, favicon = {"estudi": ("img/rauxa-192.png", "img/rauxa-favicon-32.png"),
                     "cattower": ("img/cattower/icon-192.png", "img/cattower/favicon-32.png")}.get(
                         page, ("img/icon-192.png", "img/favicon-32.png"))
    L = []
    L.append("<title>%s</title>" % esc_t(title))
    L.append('<meta name="description" content="%s">' % esc_a(desc))
    L.append('<link rel="canonical" href="%s">' % url)
    for l in LANGS:
        L.append('<link rel="alternate" hreflang="%s" href="%s">' % (l, page_url(page, l)))
    L.append('<link rel="alternate" hreflang="x-default" href="%s">' % page_url(page, None))
    L.append('<link rel="icon" type="image/png" sizes="32x32" href="%s%s">' % (prefix, favicon))
    L.append('<link rel="apple-touch-icon" href="%s%s">' % (prefix, icon))
    L.append('<meta name="theme-color" content="#b8541c">')
    L.append('<meta property="og:type" content="website">')
    L.append('<meta property="og:site_name" content="Rauxa Games">')
    L.append('<meta property="og:url" content="%s">' % url)
    L.append('<meta property="og:title" content="%s">' % esc_a(title))
    L.append('<meta property="og:description" content="%s">' % esc_a(desc))
    L.append('<meta property="og:locale" content="%s">' % OG_LOCALE[lang])
    for l in LANGS:
        if l != lang:
            L.append('<meta property="og:locale:alternate" content="%s">' % OG_LOCALE[l])
    L.append('<meta property="og:image" content="%s">' % img)
    L.append('<meta property="og:image:type" content="image/jpeg">')
    L.append('<meta property="og:image:width" content="1024">')
    L.append('<meta property="og:image:height" content="500">')
    L.append('<meta property="og:image:alt" content="%s">' % esc_a(d["bannerAlt"]))
    L.append('<meta name="twitter:card" content="summary_large_image">')
    L.append('<meta name="twitter:title" content="%s">' % esc_a(title))
    L.append('<meta name="twitter:description" content="%s">' % esc_a(desc))
    L.append('<meta name="twitter:image" content="%s">' % img)
    L.append('<meta name="twitter:image:alt" content="%s">' % esc_a(d["bannerAlt"]))
    L.append('<script type="application/ld+json">\n%s\n</script>' % ld_graph(page, lang, url, title, desc))
    return "\n".join(L) + "\n"


def lang_links(page, current, d, prefix):
    out = ['<nav class="lang-links" aria-label="%s">' % esc_a(d["langLabel"])]
    for l in LANGS:
        extra = ' dir="rtl"' if l == "ar" else ""
        cur = ' aria-current="page"' if l == current else ""
        out.append('    <a href="%s%s%s/" hreflang="%s" lang="%s"%s%s>%s</a>'
                   % (prefix, PAGES[page]["base"], l, l, l, extra, cur, NATIVE[l]))
    out.append("  </nav>")
    return "\n  ".join(out)


def render(src, page, lang, fixed, all_d):
    d = all_d[lang]
    prefix = prefix_of(page, fixed)
    s = src

    attrs = 'lang="%s" dir="%s" data-root="%s"' % (lang, "rtl" if lang == "ar" else "ltr", prefix)
    if fixed:
        attrs += ' data-fixed-lang="%s"' % lang
    s = re.sub(r"<html[^>]*>", "<html %s>" % attrs, s, count=1)
    s = re.sub(r"(<!-- SEO:BEGIN[^>]*-->\n).*?(<!-- SEO:END -->)",
               lambda m: m.group(1) + seo_block(page, lang, fixed, d, prefix) + m.group(2), s, count=1, flags=re.S)

    body_start = s.index("<body>")
    script_start = s.index("<script>", body_start)
    body = s[body_start:script_start]

    def txt(m):
        tag, attrs, key = m.group(1), m.group(2), m.group(3)
        if key not in d:
            return m.group(0)
        val = fmt(d[key], attrs, d)
        if "data-privacy-link" in attrs and "data-foot" in attrs:
            val = val + d.get("privacyNote", "")   # peu: com fa el JS
        return "<%s%s>%s</%s>" % (tag, attrs, esc_t(val), tag)
    body = re.sub(r'<(\w+)(\s[^>]*?data-i18n="(\w+)"[^>]*)>(.*?)</\1>', txt, body, flags=re.S)

    def alt(m):
        tag = m.group(0)
        key = re.search(r'data-i18n-alt="(\w+)"', tag).group(1)
        return re.sub(r'alt="[^"]*"', 'alt="%s"' % esc_a(fmt(d[key], tag, d)), tag, count=1)
    body = re.sub(r"<img\s[^>]*data-i18n-alt=\"\w+\"[^>]*>", alt, body)

    def yt(m):   # tràiler: l'enllaç, la miniatura i data-yt porten el vídeo de l'idioma (clau d'I18N, p. ex. videoId)
        vid = d[m.group(1)]
        return re.sub(r'(watch\?v=|/vi/|data-yt=")[A-Za-z0-9_-]{11}', lambda mm: mm.group(1) + vid, m.group(0))
    body = re.sub(r'<a\s[^>]*data-i18n-yt="(\w+)"[^>]*>.*?</a>', yt, body, flags=re.S)

    here = lang + "/" if fixed else ""

    def link(m):   # un <a ...> sencer amb algun dels atributs d'enllaç
        tag = m.group(0)
        g = re.search(r'data-privacy-link(?:="(\w*)")?', tag)
        if g:
            return re.sub(r'href="[^"]*"', 'href="%s"' % privacy_href(g.group(1) or page, lang, prefix), tag, count=1)
        g = re.search(r'data-play-link(?:="(\w*)")?', tag)
        if g:
            return re.sub(r'href="[^"]*"', 'href="%s"' % esc_a(play_url(g.group(1) or page, lang, page)), tag, count=1)
        g = re.search(r'data-game-link="(\w+)"', tag)
        if g:
            return re.sub(r'href="[^"]*"', 'href="%s%s/%s"' % (prefix, g.group(1), here), tag, count=1)
        if "data-home-link" in tag:
            return re.sub(r'href="[^"]*"', 'href="%s"' % ((prefix + here) or "./"), tag, count=1)
        return tag
    body = re.sub(r"<a\s[^>]*>", link, body)

    while re.search(r"<option [^>]*? selected", body):
        body = re.sub(r"(<option [^>]*?) selected", r"\1", body)
    body = body.replace('<option value="%s"' % lang, '<option value="%s" selected' % lang, 1)

    body = re.sub(r"(<!-- LANGLINKS:BEGIN -->).*?(<!-- LANGLINKS:END -->)",
                  lambda m: m.group(1) + "\n  " + lang_links(page, lang if fixed else None, d, prefix) + "\n  " + m.group(2),
                  body, count=1, flags=re.S)
    s = s[:body_start] + body + s[script_start:]

    # rutes de les imatges (a les fonts, des de l'arrel)
    s = re.sub(r'((?:src|srcset)=")(?:\.\./)*img/', lambda m: m.group(1) + prefix + "img/", s)
    s = re.sub(r'(<link rel="icon"[^>]*href=")(?:\.\./)*img/', lambda m: m.group(1) + prefix + "img/", s)
    return s


def sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for page in PAGES:
        for u in [None] + LANGS:
            out.append("  <url>")
            out.append("    <loc>%s</loc>" % page_url(page, u))
            out.append("    <lastmod>%s</lastmod>" % LASTMOD)
            for l in LANGS:
                out.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, page_url(page, l)))
            out.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % page_url(page, None))
            out.append("  </url>")
    for p in ("privacy", "cattower/privacy/"):
        out.append("  <url>\n    <loc>%s%s</loc>\n    <lastmod>%s</lastmod>\n  </url>" % (SITE, p, LASTMOD))
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main():
    n = 0
    for page, cfg in PAGES.items():
        src_path = os.path.join(ROOT, cfg["src"])
        src = io.open(src_path, encoding="utf-8").read().replace("\r\n", "\n")
        all_d = parse_i18n(src, cfg["src"])
        for l in LANGS:
            for k in ("title", "metaDesc", "bannerAlt", "langLabel"):
                if k not in all_d[l]:
                    sys.exit("Falta la clau %s a %s (%s)" % (k, l, cfg["src"]))
        out_dir = os.path.join(ROOT, cfg["base"])
        write(os.path.join(out_dir, "index.html"), render(src, page, ROOT_LANG, False, all_d))
        for l in LANGS:
            write(os.path.join(out_dir, l, "index.html"), render(src, page, l, True, all_d))
        n += 1 + len(LANGS)
    write(os.path.join(ROOT, "sitemap.xml"), sitemap())
    print("OK: %d pàgines (%s) + sitemap.xml" % (n, ", ".join(PAGES)))


if __name__ == "__main__":
    main()
