Web estàtica de Rauxa Games (AntDefender): landing + política de privadesa en català/anglès/castellà (`/privacy`).
La landing és en 11 idiomes (ca, en, es, fr, de, pt, ru, ja, zh, hi, ar — àrab en RTL) amb diccionari JS a `index.html`; detecta l'idioma per `#hash` → idioma desat → navegador → anglès, i té una galeria de mons amb imatges a `img/themes/tNN_game.webp` i `tNN_map.webp` (NN = 01..10; si falten, s'amaguen).
Es publica amb GitHub Pages: Settings → Pages → Deploy from a branch → `main` / `(root)`. Passos detallats a [PUBLICAR.md](PUBLICAR.md).
