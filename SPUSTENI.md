# BoomBrand – spuštění na boom-brand.cz

Stav 19. 10. 2026: návrh je obsahově kompletní (všech 30 URL starého webu + nové stránky), formuláře ostré, GDPR připravené.
Na doméně dnes běží jeho starý web (Lovable, A 185.158.133.1). Pošta jede přes Google Workspace a přepnutím webu se nezmění.

## 1. Od klienta před spuštěním
- [ ] PDF „20 AI triků“ → `static/tipy/20-ai-triku.pdf`, do `_data/site.json` → `tipy.pdf: "tipy/20-ai-triku.pdf"`
- [ ] odsouhlasený text `/ochrana-osobnich-udaju/` (doby uložení, případný nástroj na rozesílku tipů → doplnit mezi zpracovatele)
- [ ] DPH u cen (pokud je plátce a ceny jsou bez DPH, doplnit „bez DPH“ v `_cenik.html`)
- [ ] souhlas se sídlem v patičce (§ 435 OZ ho vyžaduje; alternativa = virtuální sídlo)
- [ ] smlouva o zpracování osobních údajů s WebHunter s.r.o. (čl. 28 GDPR)
- [ ] přístup do DNS u WebSupportu (nebo ať záznamy přepne sám, viz 3.)

## 2. Přepnout build na ostrý web (`_data/site.json`)
```json
"url": "https://boom-brand.cz/",
"base": "/",
"navrh": false,
"domena": "boom-brand.cz",
"mereni": { "aktivni": true, ... },
"zasady_od": "<datum spuštění>"
```
Pak `python3 build.py` (zmizí noindex, robots povolí AI boty, vznikne CNAME) a `./deploy.sh`.
GitHub Pages: `gh api -X PUT repos/webhunter-navrhy/boombrand/pages -f cname=boom-brand.cz` a po vydání certifikátu `-F https_enforced=true`.

## 3. DNS u WebSupportu
| Záznam | Hodnota |
|---|---|
| A `@` | 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153 (smazat 185.158.133.1) |
| CNAME `www` | webhunter-navrhy.github.io. |
| MX, TXT (SPF, google-site-verification) | **beze změny** – jinak přestane chodit pošta / ověření Search Console |

Po přepnutí odpojit doménu v Lovable (pozor: neodpojovat dřív, než DNS běží u nás).

## 4. Po spuštění ověřit
- [ ] `https://boom-brand.cz/` i `https://www.boom-brand.cz/` → 200, HTTPS
- [ ] staré URL bez lomítka (`/osobni-znacka`, `/blog/kolik-stoji-osobni-znacka`) → 301 na verzi s lomítkem (GitHub Pages to dělá sám)
- [ ] `qa.py https://boom-brand.cz/ ~/boombrand` zelené, bez varování noindex
- [ ] testovací poptávka z úvodu i z /formular dorazí na barton@boom-brand.cz (pak ji smazat z KV `frm:boombrand:*`)
- [ ] lišta cookies: po „Odmítnout“ se nenačte googletagmanager ani connect.facebook.net; po „Přijmout“ ano
- [ ] GA4: událost `generate_lead` označit jako klíčovou; Meta Events Manager: událost `Lead` z webu
- [ ] Search Console: odeslat `https://boom-brand.cz/sitemap.xml`

## Technika
- Zdroj: `~/boombrand` (repo webhunter-navrhy/boombrand, main = zdroje, gh-pages = dist)
- Obsah: `_data/*.json` (sluzby = 9 landingů, blog = články, recenze, obsah = úvod/ceník/formuláře, site = kontakty a nastavení)
- Formuláře: `https://webhunter-admin.webhunter.workers.dev/api/boombrand/form` (KV `site:boombrand`: formStore, formLang cs, formTo, formOrigins)
- Nový článek: přidat objekt do `_data/blog.json` (slug, titulek, popis, h1, datum, cteni, kategorie, telo v HTML, sluzba)
