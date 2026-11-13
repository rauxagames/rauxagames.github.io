Web estàtica de Rauxa Games (AntDefender): landing + política de privadesa en català/anglès/castellà (`/privacy`).
La landing és en 11 idiomes (ca, en, es, fr, de, pt, ru, ja, zh, hi, ar — àrab en RTL) amb diccionari JS a `index.html`; detecta l'idioma per `#hash` → idioma desat → navegador → anglès, i té una galeria de mons amb imatges a `img/themes/tNN_game.webp` i `tNN_map.webp` (NN = 01..10; si falten, s'amaguen).
Es publica amb GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `(root)`. Passos detallats a [PUBLICAR.md](PUBLICAR.md).

## SEO: pàgines per idioma (generades)

- **Font de veritat: `index.html` de l'arrel** (estructura, CSS, JS i el diccionari `I18N`, inclosos `title`, `metaDesc` i `h1Tag` de cada idioma).
- `py tools/build_i18n.py` regenera, sense dependències:
  - `index.html` (arrel = `x-default`, contingut estàtic en anglès; el JS hi continua detectant l'idioma),
  - `ca/ en/ es/ fr/ de/ pt/ ru/ ja/ zh/ hi/ ar/index.html` (text ja traduït a l'HTML, `lang` fix; el selector hi navega a l'altra pàgina),
  - `sitemap.xml` (amb `hreflang`).
- El bloc entre `<!-- SEO:BEGIN -->` i `<!-- SEO:END -->` (title, description, canonical, hreflang, Open Graph, Twitter, JSON-LD) i el de `<!-- LANGLINKS -->` del peu els escriu l'script: no s'editen a mà.
- **Sempre que toquis `index.html`, torna a executar l'script abans del commit** (és idempotent). Canvia `LASTMOD` a l'script quan hi hagi canvis de contingut.
- Botons de Google Play amb `&referrer=utm_source=web&utm_medium=site&utm_campaign=landing_<idioma>` (es veu a Play Console → Adquisició d'usuaris).
- Imatge per compartir a xarxes: `img/og-image.jpg` (còpia JPG de `img/banner.webp`, 1024×500).
