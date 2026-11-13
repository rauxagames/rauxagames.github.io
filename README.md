Web estàtica de **Rauxa Games**: la portada de l'estudi i una pàgina per a cada joc, en 11 idiomes (ca, en, es, fr, de,
pt, ru, ja, zh, hi, ar — àrab en RTL). Es publica amb GitHub Pages (`main` / `(root)`, vegeu [PUBLICAR.md](PUBLICAR.md)).

| Adreça | Què és | Font |
|---|---|---|
| `/` i `/<xx>/` | Portada de l'estudi: fitxa de cada joc | `src/estudi.html` |
| `/antdefender/` i `/antdefender/<xx>/` | AntDefender (galeria dels 10 mons) | `src/antdefender.html` |
| `/cattower/` i `/cattower/<xx>/` | Cat Tower (de moment «aviat a Google Play») | `src/cattower.html` |
| `/privacy` (`privacy.html` i `privacy/index.html`) | Política d'AntDefender (ca/en/es) | a mà |
| `/cattower/privacy/` | Política de Cat Tower (ca/en/es) | a mà |
| `/app-ads.txt` | AdMob (un sol compte per a tots els jocs) | a mà |

**No moure mai `/privacy` ni `/app-ads.txt`**: són les adreces que té la fitxa de Google Play d'AntDefender (i la
web del desenvolupador és l'arrel, `https://rauxagames.github.io`). Si algun dia es compra un domini, GitHub Pages
redirigeix les adreces de `rauxagames.github.io` al domini nou.

## SEO: pàgines per idioma (generades)

- **Fonts de veritat: `src/*.html`** (estructura, CSS, JS i el diccionari `I18N` de cada pàgina, inclosos `title`,
  `metaDesc` i `bannerAlt`). A les fonts, les rutes són des de l'arrel (`img/...`); l'script les corregeix.
- `py tools/build_i18n.py` regenera, sense dependències, per a cada pàgina: la de sense idioma (x-default, en anglès;
  el JS hi detecta l'idioma: `#hash` → idioma desat → navegador → anglès), la de cada idioma (text ja traduït a
  l'HTML, el que indexa Google) i `sitemap.xml` (amb `hreflang`).
- El bloc entre `<!-- SEO:BEGIN -->` i `<!-- SEO:END -->` (title, description, canonical, hreflang, Open Graph, Twitter,
  JSON-LD) i el de `<!-- LANGLINKS -->` del peu els escriu l'script: no s'editen a mà.
- **Sempre que toquis una font de `src/`, torna a executar l'script abans del commit** (és idempotent). Canvia
  `LASTMOD` a l'script quan hi hagi canvis de contingut.
- Enllaços que l'script i el JS omplen: `data-home-link` (portada), `data-game-link="joc"`, `data-play-link[="joc"]`
  (Google Play amb `utm_campaign=landing_<idioma>` o `<pàgina>_<idioma>`, es veu a Play Console → Adquisició
  d'usuaris) i `data-privacy-link[="joc"]`.
- Imatges per compartir a xarxes (1024×500): `img/og-image.jpg` (AntDefender), `img/cattower/og-image.jpg`,
  `img/og-estudi.jpg` (portada).

## Joc nou

1. `GAMES` i `PAGES` a `tools/build_i18n.py` (i `GAMES` al JS de les fonts).
2. `src/<joc>.html` (es pot copiar `src/cattower.html`), imatges a `img/<joc>/`, i la fitxa a `src/estudi.html`.
3. La política a `<joc>/privacy/index.html` (es pot copiar la de Cat Tower) i afegir-la al `sitemap()` de l'script.
4. Quan el joc surti a Play: `package` a `GAMES` (i `play` al JS), i canviar «aviat» pel botó de Google Play.

Les imatges de Cat Tower les fa `tools/imatges_web.py` del repo `cat_tower` (captures d'Unity → `img/cattower/`).
