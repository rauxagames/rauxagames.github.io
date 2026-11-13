"""Genera les pàgines estàtiques per idioma de la landing (SEO).

Font de veritat: ../index.html (estructura + diccionari JS `I18N`).
Sortides (no editar a mà, es regeneren):
  index.html        arrel = x-default, contingut estàtic en anglès; el JS hi detecta l'idioma
  <xx>/index.html   una pàgina per idioma amb el text ja traduït a l'HTML (el que indexa Google)
  sitemap.xml       amb les alternatives hreflang

Ús (des de l'arrel del repo):  py tools/build_i18n.py
Cal tornar-lo a executar sempre que es toqui index.html (textos, diccionari, estructura).
És idempotent: tot el que canvia per idioma es reescriu des del diccionari.
"""
import html
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://rauxagames.github.io/"
PLAY = "https://play.google.com/store/apps/details?id=com.rauxagames.antdefender"
LASTMOD = "2026-11-13"
ROOT_LANG = "en"   # contingut estàtic de l'arrel (coincideix amb el que veu Googlebot amb JS)

LANGS = ["ca", "en", "es", "fr", "de", "pt", "ru", "ja", "zh", "hi", "ar"]
NATIVE = {"ca": "Català", "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch",
          "pt": "Português", "ru": "Русский", "ja": "日本語", "zh": "简体中文", "hi": "हिन्दी",
          "ar": "العربية"}
OG_LOCALE = {"ca": "ca_ES", "en": "en_US", "es": "es_ES", "fr": "fr_FR", "de": "de_DE",
             "pt": "pt_PT", "ru": "ru_RU", "ja": "ja_JP", "zh": "zh_CN", "hi": "hi_IN", "ar": "ar_AR"}
PLAY_HL = {"pt": "pt-PT", "zh": "zh-CN"}   # igual que playUrl() del JS
PRIVACY_LANGS = ["ca", "en", "es"]

esc_t = lambda v: html.escape(v, quote=False)
esc_a = lambda v: html.escape(v, quote=False).replace('"', "&quot;")


def play_url(lang):
    ref = "utm_source%3Dweb%26utm_medium%3Dsite%26utm_campaign%3Dlanding_" + lang
    return PLAY + "&hl=" + PLAY_HL.get(lang, lang) + "&referrer=" + ref


def page_url(lang):
    return SITE if lang is None else SITE + lang + "/"


def parse_i18n(src):
    m = re.search(r"var I18N = \{\n(.*?)\n  \};", src, re.S)
    if not m:
        sys.exit("No trobo el diccionari I18N a index.html")
    out = {}
    for lm in re.finditer(r"^    (\w+): \{\n(.*?)\n    \}", m.group(1), re.S | re.M):
        d = {}
        for km in re.finditer(r'^      (\w+): ("(?:[^"\\]|\\.)*"),?$', lm.group(2), re.M):
            d[km.group(1)] = json.loads(km.group(2))
        out[lm.group(1)] = d
    missing = [l for l in LANGS if l not in out]
    if missing:
        sys.exit("Falten idiomes al diccionari: %s" % missing)
    return out


def fmt(text, attrs, d):
    w = re.search(r'data-w="(\w+)"', attrs)
    a = re.search(r'data-a="([^"]*)"', attrs)
    b = re.search(r'data-b="([^"]*)"', attrs)
    return (text.replace("{w}", d[w.group(1)] if w else "", 1)
                .replace("{a}", a.group(1) if a else "", 1)
                .replace("{b}", b.group(1) if b else "", 1))


def seo_block(lang, fixed, d, all_d, prefix):
    url = page_url(lang if fixed else None)
    title, desc = d["title"], d["metaDesc"]
    img = SITE + "img/og-image.jpg"
    L = []
    L.append("<title>%s</title>" % esc_t(title))
    L.append('<meta name="description" content="%s">' % esc_a(desc))
    L.append('<link rel="canonical" href="%s">' % url)
    for l in LANGS:
        L.append('<link rel="alternate" hreflang="%s" href="%s">' % (l, page_url(l)))
    L.append('<link rel="alternate" hreflang="x-default" href="%s">' % SITE)
    L.append('<link rel="icon" type="image/png" sizes="32x32" href="%simg/favicon-32.png">' % prefix)
    L.append('<link rel="apple-touch-icon" href="%simg/icon-192.png">' % prefix)
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
    org = {"@type": "Organization", "@id": SITE + "#org", "name": "Rauxa Games", "url": SITE,
           "logo": SITE + "img/icon-192.png", "email": "rauxa.antdefender@gmail.com",
           "address": {"@type": "PostalAddress", "addressCountry": "AD"}}
    game = {
        "@type": ["VideoGame", "MobileApplication"],
        "@id": SITE + "#antdefender",
        "name": "AntDefender",
        "alternateName": "AntDefender: Ant Tower Defense",
        "description": desc,
        "url": SITE,
        "image": img,
        "screenshot": [SITE + "img/shot-combat.webp", SITE + "img/shot-base.webp",
                       SITE + "img/shot-heroes.webp"],
        "genre": ["Tower defense", "Action", "Strategy"],
        "gamePlatform": "Android",
        "operatingSystem": "Android",
        "applicationCategory": "GameApplication",
        "playMode": "SinglePlayer",
        "inLanguage": LANGS,
        "installUrl": PLAY,
        "downloadUrl": PLAY,
        "sameAs": [PLAY],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
                   "availability": "https://schema.org/InStock", "url": PLAY},
        "author": {"@id": SITE + "#org"},
        "publisher": {"@id": SITE + "#org"},
    }
    site = {"@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
            "inLanguage": lang, "isPartOf": {"@type": "WebSite", "@id": SITE + "#site", "url": SITE,
                                            "name": "Rauxa Games", "publisher": {"@id": SITE + "#org"}},
            "about": {"@id": SITE + "#antdefender"}}
    ld = json.dumps({"@context": "https://schema.org", "@graph": [org, game, site]},
                    ensure_ascii=False, indent=1).replace("</", "<\\/")
    L.append('<script type="application/ld+json">\n%s\n</script>' % ld)
    return "\n".join(L) + "\n"


def lang_links(current, d, prefix):
    out = ['<nav class="lang-links" aria-label="%s">' % esc_a(d["langLabel"])]
    for l in LANGS:
        extra = ' dir="rtl"' if l == "ar" else ""
        cur = ' aria-current="page"' if l == current else ""
        out.append('    <a href="%s%s/" hreflang="%s" lang="%s"%s%s>%s</a>'
                   % (prefix, l, l, l, extra, cur, NATIVE[l]))
    out.append("  </nav>")
    return "\n  ".join(out)


def render(src, lang, fixed, all_d):
    d = all_d[lang]
    prefix = "../" if fixed else ""
    s = src

    # <html>
    attrs = 'lang="%s" dir="%s"' % (lang, "rtl" if lang == "ar" else "ltr")
    if fixed:
        attrs += ' data-fixed-lang="%s"' % lang
    s = re.sub(r"<html[^>]*>", "<html %s>" % attrs, s, count=1)

    # head
    s = re.sub(r"(<!-- SEO:BEGIN[^>]*-->\n).*?(<!-- SEO:END -->)",
               lambda m: m.group(1) + seo_block(lang, fixed, d, all_d, prefix) + m.group(2), s, count=1, flags=re.S)

    # Textos (elements fulla amb data-i18n). Fora del <script>.
    body_start = s.index("<body>")
    script_start = s.index("<script>", body_start)
    body = s[body_start:script_start]

    def txt(m):
        tag, attrs, key = m.group(1), m.group(2), m.group(3)
        if key not in d:
            return m.group(0)
        val = fmt(d[key], attrs, d)
        if key == "privacy" and "data-privacy-link" in attrs:
            val = d["privacy"] + d.get("privacyNote", "")   # peu: com fa el JS
        return "<%s%s>%s</%s>" % (tag, attrs, esc_t(val), tag)
    body = re.sub(r'<(\w+)(\s[^>]*?data-i18n="(\w+)"[^>]*)>(.*?)</\1>', txt, body, flags=re.S)

    def alt(m):
        tag = m.group(0)
        key = re.search(r'data-i18n-alt="(\w+)"', tag).group(1)
        return re.sub(r'alt="[^"]*"', 'alt="%s"' % esc_a(fmt(d[key], tag, d)), tag, count=1)
    body = re.sub(r"<img\s[^>]*data-i18n-alt=\"\w+\"[^>]*>", alt, body)

    priv = "privacy.html#" + (lang if lang in PRIVACY_LANGS else "en")
    body = re.sub(r'(<a href=")[^"]*("[^>]*data-privacy-link)', lambda m: m.group(1) + priv + m.group(2), body)
    body = re.sub(r'(<a [^>]*data-play-link href=")[^"]*(")',
                  lambda m: m.group(1) + esc_a(play_url(lang)) + m.group(2), body)

    # selector
    while re.search(r"<option [^>]*? selected", body):
        body = re.sub(r"(<option [^>]*?) selected", r"\1", body)
    body = body.replace('<option value="%s"' % lang, '<option value="%s" selected' % lang, 1)

    # enllaços d'idioma del peu
    body = re.sub(r"(<!-- LANGLINKS:BEGIN -->).*?(<!-- LANGLINKS:END -->)",
                  lambda m: m.group(1) + "\n  " + lang_links(lang if fixed else None, d, prefix) + "\n  " + m.group(2),
                  body, count=1, flags=re.S)

    s = s[:body_start] + body + s[script_start:]

    if fixed:   # rutes relatives des de /xx/
        s = s.replace('src="img/', 'src="../img/').replace('href="privacy.html', 'href="../privacy.html')
    return s


def sitemap():
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
           'xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for u in [None] + LANGS:
        out.append("  <url>")
        out.append("    <loc>%s</loc>" % page_url(u))
        out.append("    <lastmod>%s</lastmod>" % LASTMOD)
        for l in LANGS:
            out.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, page_url(l)))
        out.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % SITE)
        out.append("  </url>")
    out.append("  <url>\n    <loc>%sprivacy</loc>\n    <lastmod>%s</lastmod>\n  </url>" % (SITE, LASTMOD))
    out.append("</urlset>")
    return "\n".join(out) + "\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    os.replace(tmp, path)


def main():
    src_path = os.path.join(ROOT, "index.html")
    src = io.open(src_path, encoding="utf-8").read().replace("\r\n", "\n")
    all_d = parse_i18n(src)
    for l in LANGS:
        for k in ("title", "metaDesc", "h1Tag", "bannerAlt", "langLabel"):
            if k not in all_d[l]:
                sys.exit("Falta la clau %s a %s" % (k, l))
    write(src_path, render(src, ROOT_LANG, False, all_d))
    for l in LANGS:
        write(os.path.join(ROOT, l, "index.html"), render(src, l, True, all_d))
    write(os.path.join(ROOT, "sitemap.xml"), sitemap())
    print("OK: index.html + %d pàgines d'idioma + sitemap.xml" % len(LANGS))


if __name__ == "__main__":
    main()
