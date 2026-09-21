# Com publicar aquesta web a GitHub Pages

Aquest repo local (`C:\GIT\rauxagames-web`) ja té un commit inicial a la branca `main`
i **cap remot**. Només cal triar on viurà a GitHub, afegir el remot i fer push.

> **Per què no serveix `marcriu80/rauxagames.github.io`:** un repo anomenat
> `<usuari>.github.io` només es publica a l'arrel del domini si `<usuari>` coincideix
> amb el compte (o organització) propietari. Sota el compte `marcriu80`, un repo dit
> `rauxagames.github.io` es publicaria a `https://marcriu80.github.io/rauxagames.github.io/`
> — una URL lletja i confusa. Per això hi ha dues opcions netes:

## Opció A — Repo de projecte al teu compte (`marcriu80/rauxagames-web`)

Funciona avui mateix, sense crear res més. La URL porta el nom del repo al camí.

- URL de la web: `https://marcriu80.github.io/rauxagames-web/`
- URL de la política: `https://marcriu80.github.io/rauxagames-web/privacy`
  (també `…/rauxagames-web/privacy.html`)

Passos:

1. A GitHub: **New repository** → nom `rauxagames-web` → **Public** → *sense* README,
   `.gitignore` ni llicència (el repo local ja té contingut) → **Create repository**.
2. Al terminal (PowerShell o Git Bash):
   ```bash
   cd C:\GIT\rauxagames-web
   git remote add origin https://github.com/marcriu80/rauxagames-web.git
   git push -u origin main
   ```
3. Al repo a GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a
   branch → Branch: `main` / `(root)` → Save**.
4. Espera 1-2 minuts i obre `https://marcriu80.github.io/rauxagames-web/privacy`.

Més endavant, si compres un domini (p. ex. `rauxagames.com`), a **Settings → Pages →
Custom domain** el pots apuntar i la URL passa a ser `https://rauxagames.com/privacy`.

## Opció B — Organització `rauxagames` + repo `rauxagames.github.io` (RECOMANADA)

URL neta a l'arrel, coincideix amb el nom de l'estudi i és la que ja s'ha previst a la
fitxa de Play. Crear una organització a GitHub és gratuït i triga dos minuts.

- URL de la web: `https://rauxagames.github.io/`
- URL de la política: `https://rauxagames.github.io/privacy`
  (també `https://rauxagames.github.io/privacy.html`)

Passos:

1. A GitHub, amb el compte `marcriu80` iniciat: menú **+** (dalt a la dreta) → **New
   organization** → pla **Free** → *Organization name*: `rauxagames` → correu de
   contacte → *This organization belongs to*: **My personal account** → **Next** →
   salta l'afegir membres → **Complete setup**.
   > Si el nom `rauxagames` ja estigués agafat, GitHub t'ho dirà en aquest pas: aleshores
   > prova `rauxa-games` o `rauxagames-studio` (la URL seria `https://<nom>.github.io/`).
2. Dins de l'organització: **New repository** → nom EXACTE `rauxagames.github.io`
   (ha de coincidir lletra per lletra amb el nom de l'organització + `.github.io`) →
   **Public** → sense README/.gitignore/llicència → **Create repository**.
3. Al terminal:
   ```bash
   cd C:\GIT\rauxagames-web
   git remote add origin https://github.com/rauxagames/rauxagames.github.io.git
   git push -u origin main
   ```
   Si ja havies afegit un `origin` per a l'opció A i canvies d'idea:
   `git remote set-url origin https://github.com/rauxagames/rauxagames.github.io.git`
4. **Settings → Pages**: per a un repo `<org>.github.io` la publicació des de `main`
   sol quedar activada sola. Comprova que digui *Source: Deploy from a branch → `main` /
   `(root)`*; si no, selecciona-ho i **Save**.
5. Espera 1-2 minuts i obre `https://rauxagames.github.io/privacy`.

## Abans de fer push: el correu de contacte

A `index.html`, `privacy.html` i `privacy/index.html` hi ha el text
**`rauxa.antdefender@gmail.com`** (marcat en groc a la web) en tots els llocs on ha d'anar
l'adreça real. Substitueix-lo amb un cerca-i-reemplaça a tots tres fitxers.
El correu que hi posis és el que sortirà a la fitxa de Play com a contacte del
desenvolupador, així que millor una adreça que llegeixis de debò.

Després dels canvis:

```bash
cd C:\GIT\rauxagames-web
git add -A
git commit -m "Correu de contacte real"
git push
```

## Mantenir `privacy/index.html` sincronitzat

`/privacy` (sense extensió) funciona perquè hi ha la carpeta `privacy/` amb un
`index.html` que és **una còpia** de `privacy.html` amb els enllaços relatius ajustats
(`../`). Sempre que editis `privacy.html`, regenera la còpia (Git Bash):

```bash
cd /c/GIT/rauxagames-web
sed -e 's|href="\./"|href="../"|g' -e 's|href="privacy\.html"|href="../privacy.html"|g' privacy.html > privacy/index.html
```

## Què posar a Google Play Console

- **Política de privadesa** (Fitxa de Play → *App content* → *Privacy policy*): la URL
  de l'opció triada (`…/privacy`). Google la comprova: ha de ser pública i obrir-se
  sense iniciar sessió — les dues opcions ho compleixen.
- **Data safety**: el formulari s'ha d'omplir a mà, però tot el que cal declarar és
  exactament el que descriu la política (§3): identificador anònim, progrés de joc,
  sobrenom, país, estadístiques de partida, i l'identificador publicitari via AdMob.

## Comprovacions ràpides després del primer deploy

- La política s'obre en català per defecte, i els botons **English / Español** canvien
  l'idioma sense recarregar. L'idioma triat es recorda al mateix navegador.
- Enllaços directes per idioma: `…/privacy#en` i `…/privacy#es`.
- `https://<domini>/` mostra la landing amb l'enllaç a la política.
- Si Pages mostra un 404 just després del push, espera un minut i recarrega: el primer
  desplegament tarda una mica.
