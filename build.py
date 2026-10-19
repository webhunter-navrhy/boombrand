#!/usr/bin/env python3
"""Build: _data/*.json + src/*.html (Jinja2) + img/ + static/ -> dist/

  python3 build.py            # sestaví dist/
  python3 build.py --serve    # + lokální server na http://localhost:8765/<base>

Co dělá sám: WebP + srcset 640/1280/1920, lazy u všech fotek kromě první na stránce, ?v=<hash obsahu> u CSS/JS,
noindex a robots.txt podle site.navrh, JSON-LD LocalBusiness ze site.json, og:image 1200x630, sitemap.xml, 404.html,
.nojekyll (+ CNAME u ostrého webu s doménou). Design si nedědí: styl a šablony píšeš ty.
"""
import datetime
import hashlib
import html
import json
import os, subprocess
import re
import shutil
import sys

from markupsafe import Markup
from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC, DATA, IMG, STATIC, DIST, CACHE = (os.path.join(ROOT, p) for p in ("src", "_data", "img", "static", "dist", ".cache/img"))
SIRKY = (400, 640, 1280, 1920)
RASTER = (".jpg", ".jpeg", ".png", ".webp")


class BuildError(Exception):
    pass


NB_RE = re.compile(r"(?<![\w\u00C0-\u017F])([kKsSvVzZoOuUaAiI])\s+")
NUM_RE = re.compile(r"(\d) +(Kč|mil\.|M\+|hodin|hodiny|minut|měsíc|měsíců|měsíce|dní|dnů|den|let|lidí|platformy|%|000)")


def nb(text):
    """Česká sazba: nezlomitelná mezera po jednopísmenných předložkách/spojkách a mezi číslem a jednotkou."""
    if not isinstance(text, str) or " " not in text or text.startswith(("http", "mailto:", "tel:", "#", "/")):
        return text
    t = NB_RE.sub(lambda m: m.group(1) + "\u00a0", text)
    t = NUM_RE.sub(lambda m: m.group(1) + "\u00a0" + m.group(2), t)
    t = NUM_RE.sub(lambda m: m.group(1) + "\u00a0" + m.group(2), t)
    t = re.sub(r"(\d)–(\d)", "\\1–\u2060\\2", t)
    return t.replace("mil. Kč", "mil.\u00a0Kč").replace(" – ", "\u00a0– ")


def _nb_vse(x):
    if isinstance(x, dict):
        return {k: (v if k in ("href", "src", "id", "url", "soubor", "foto", "video", "poster", "pole", "slug") else _nb_vse(v)) for k, v in x.items()}
    if isinstance(x, list):
        return [_nb_vse(v) for v in x]
    return nb(x)


def nacti_data():
    d = {}
    for f in sorted(os.listdir(DATA)):
        if f.endswith(".json"):
            with open(os.path.join(DATA, f), encoding="utf-8") as fh:
                d[f[:-5]] = _nb_vse(json.load(fh)) if f != "site.json" else json.load(fh)
    if "site" not in d:
        raise BuildError("chybí _data/site.json")
    return d


class Obrazky:
    """Převod do WebP + generování <img srcset>. Počítá fotky na stránce: první je eager."""

    def __init__(self, base):
        self.base = base
        self.pocet = 0
        self.info = {}
        os.makedirs(CACHE, exist_ok=True)

    def reset(self):
        self.pocet = 0

    def _zpracuj(self, nazev):
        if nazev in self.info:
            return self.info[nazev]
        zdroj = os.path.join(IMG, nazev)
        if not os.path.exists(zdroj):
            raise BuildError(f"obrázek img/{nazev} neexistuje")
        stem, ext = os.path.splitext(nazev)
        stem = re.sub(r"[^A-Za-z0-9._-]+", "-", stem)
        cil_dir = os.path.join(DIST, "img")
        os.makedirs(cil_dir, exist_ok=True)
        if ext.lower() not in RASTER:   # svg a ostatní se kopírují beze změny
            shutil.copy(zdroj, os.path.join(cil_dir, os.path.basename(nazev)))
            self.info[nazev] = {"raster": False, "src": f"img/{os.path.basename(nazev)}"}
            return self.info[nazev]
        h = hashlib.sha1(open(zdroj, "rb").read()).hexdigest()[:12]
        im = ImageOps.exif_transpose(Image.open(zdroj))
        im.load()
        w0, h0 = im.size
        sirky = sorted({w for w in SIRKY if w < w0} | {min(w0, SIRKY[-1])})
        varianty = []
        for w in sirky:
            vyska = round(h0 * w / w0)
            cache = os.path.join(CACHE, f"{h}-{w}.webp")
            if not os.path.exists(cache):
                r = im.resize((w, vyska), Image.LANCZOS) if w != w0 else im
                if r.mode not in ("RGB", "RGBA"):
                    r = r.convert("RGBA" if "A" in r.getbands() else "RGB")
                r.save(cache, "WEBP", quality=80, method=6)
            out = f"{stem}-{w}.webp"
            shutil.copy(cache, os.path.join(cil_dir, out))
            varianty.append((w, vyska, f"img/{out}"))
        self.info[nazev] = {"raster": True, "varianty": varianty}
        return self.info[nazev]

    def img(self, nazev, alt=None, sizes="100vw", cls="", eager=None, styl=""):
        if alt is None:
            raise BuildError(f"img('{nazev}'): chybí alt (pro dekorativní fotku alt='')")
        self.pocet += 1
        prvni = (self.pocet == 1) if eager is None else eager
        i = self._zpracuj(nazev)
        a = f' alt="{html.escape(alt, quote=True)}"'
        c = f' class="{cls}"' if cls else ""
        s = f' style="{styl}"' if styl else ""
        if not i["raster"]:
            return Markup(f'<img src="{self.base}{i["src"]}"{a}{c}{s} loading="{"eager" if prvni else "lazy"}" decoding="async">')
        w, h, nejv = i["varianty"][-1][0], i["varianty"][-1][1], i["varianty"][-1][2]
        srcset = ", ".join(f"{self.base}{p} {w_}w" for w_, _, p in i["varianty"])
        nacitani = 'loading="eager" fetchpriority="high"' if prvni else 'loading="lazy"'
        return Markup(f'<img src="{self.base}{nejv}" srcset="{srcset}" sizes="{sizes}" width="{w}" height="{h}"{a}{c}{s} '
                      f'{nacitani} decoding="async">')

    def img_url(self, nazev, w=1280):
        i = self._zpracuj(nazev)
        if not i["raster"]:
            return self.base + i["src"]
        best = min(i["varianty"], key=lambda v: abs(v[0] - w))
        return self.base + best[2]

    def og(self, nazev):
        zdroj = os.path.join(IMG, nazev)
        if not os.path.exists(zdroj):
            return None
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(zdroj)).convert("RGB"), (1200, 630), Image.LANCZOS)
        im.save(os.path.join(DIST, "og.jpg"), quality=84, optimize=True)
        return "og.jpg"


def hash_souboru(cesta):
    return hashlib.sha1(open(cesta, "rb").read()).hexdigest()[:10]



def zmensi_css_js():
    """Minifikace CSS a JS v dist/ přes esbuild (zdroje ve static/ zůstávají čitelné). Bez esbuildu se jen přeskočí."""
    eb = os.environ.get("ESBUILD") or shutil.which("esbuild") or os.path.expanduser("~/webhunter-admin/node_modules/.bin/esbuild")
    if not os.path.exists(eb):
        print("VAROVÁNÍ: esbuild nenalezen, CSS/JS se neminifikují")
        return
    for kde, _, soubory in os.walk(DIST):
        for f in soubory:
            if f.endswith((".css", ".js")) and not f.endswith(".min.js"):
                cesta = os.path.join(kde, f)
                r = subprocess.run([eb, cesta, "--minify", "--log-level=error", "--allow-overwrite", f"--outfile={cesta}"], capture_output=True, text=True)
                if r.returncode:
                    raise BuildError(f"minifikace {f} selhala: {r.stderr.strip()[:300]}")


def jsonld(site):
    """Organizace pro všechny stránky: ProfessionalService s doloženými údaji (OR, ARES), zakladatel, profily."""
    k = site.get("kontakt", {})
    a = site.get("sidlo", {})
    j = {"@context": "https://schema.org", "@type": site.get("typ") or "LocalBusiness", "@id": site["url"] + "#firma",
         "name": site["nazev"], "legalName": site.get("firma"), "url": site["url"], "description": site.get("popis", "")}
    if k.get("telefon"): j["telephone"] = k["telefon"].replace(" ", "")
    if k.get("email"): j["email"] = k["email"]
    if a:
        j["address"] = {"@type": "PostalAddress", "streetAddress": a.get("ulice"), "postalCode": a.get("psc"),
                        "addressLocality": a.get("mesto"), "addressCountry": "CZ"}
    j["areaServed"] = [{"@type": "City", "name": "Brno"}, {"@type": "Country", "name": "Česká republika"}]
    if site.get("sameas"): j["sameAs"] = site["sameas"]
    if site.get("cenove_rozpeti"): j["priceRange"] = site["cenove_rozpeti"]
    if site.get("ico"): j["identifier"] = {"@type": "PropertyValue", "propertyID": "IČO", "value": site["ico"]}
    if site.get("logo"): j["logo"] = site["url"] + site["logo"]
    if site.get("zakladatel"):
        j["founder"] = {"@type": "Person", "name": site["zakladatel"], "url": site["url"] + "o-nas/"}
    j["image"] = site["url"] + "og.jpg"
    return json.dumps(j, ensure_ascii=False).replace("</", "<\\/")


ROBOTI = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "Perplexity-User", "Google-Extended", "ClaudeBot",
          "Claude-User", "Applebot", "Applebot-Extended", "Bingbot", "CCBot", "meta-externalagent")


def main():
    data = nacti_data()
    site = data["site"]
    base = site.get("base", "/")
    if not base.startswith("/") or not base.endswith("/"):
        raise BuildError("site.base musí začínat a končit lomítkem (např. /slug/ nebo /)")
    if not site["url"].endswith("/"):
        site["url"] += "/"
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    obr = Obrazky(base)

    # statické soubory + hash obsahu pro cache busting
    shutil.copytree(STATIC, DIST, dirs_exist_ok=True)
    zmensi_css_js()
    hashe = {}

    def asset(p):
        cil = os.path.join(DIST, p)
        if not os.path.exists(cil):
            raise BuildError(f"asset {p} neexistuje (static/{p})")
        if p not in hashe:
            hashe[p] = hash_souboru(cil)
        return f"{base}{p}?v={hashe[p]}"

    og = obr.og(site["og_image"]) if site.get("og_image") else None
    if not og:
        print("VAROVÁNÍ: chybí og_image (site.og_image -> soubor v img/)")
    og_url = site["url"] + og if og else None

    def url(cesta):
        cesta = cesta.strip("/")
        return base + (cesta + "/" if cesta else "")

    env = Environment(loader=FileSystemLoader(SRC), autoescape=select_autoescape(["html"]), undefined=StrictUndefined)
    env.filters["nb"] = nb
    def clanky_ke_sluzbe(klic, n=3):
        return [c for c in data.get("blog", []) if c.get("sluzba") and c["sluzba"]["href"] == klic][:n]

    def datum_cz(iso):
        r, m, d = (int(x) for x in iso.split("-"))
        mesice = ("ledna", "února", "března", "dubna", "května", "června", "července", "srpna", "září", "října", "listopadu", "prosince")
        return f"{d}.\u00a0{mesice[m - 1]} {r}"

    def faq_z_tela(telo):
        """Otázky z části „Časté otázky“ článku (h3 + odstavec) pro FAQPage."""
        i = telo.find("<h2>Časté otázky</h2>")
        if i < 0:
            return []
        cast = telo[i:]
        j = cast.find("<h2>", 5)
        cast = cast[:j] if j > 0 else cast
        ven = []
        for q, a in re.findall(r"<h3>(.*?)</h3>(.*?)(?=<h3>|$)", cast, re.S):
            a = re.sub(r"<[^>]+>", " ", a)
            ven.append({"q": html.unescape(re.sub(r"<[^>]+>", "", q)).strip(), "a": html.unescape(re.sub(r"\s+", " ", a)).strip()})
        return [x for x in ven if x["a"]]

    def dalsi_clanky(c, n=2):
        stejne = [x for x in data["blog"] if x["slug"] != c["slug"] and set(x["kategorie"]) & set(c["kategorie"])]
        ostatni = [x for x in data["blog"] if x["slug"] != c["slug"] and x not in stejne]
        return (stejne + ostatni)[:n]

    env.filters["datum_cz"] = datum_cz
    env.globals.update(site=site, data=data, base=base, asset=asset, url=url, img=obr.img, img_url=obr.img_url,
                       og_url=og_url, jsonld=jsonld(site), titulek="", popis="", cesta="", noindex=False,
                       clanky_ke_sluzbe=clanky_ke_sluzbe, faq_z_tela=faq_z_tela, dalsi_clanky=dalsi_clanky, minimal=False)
    stranky = []   # (cesta, lastmod)
    dnes = datetime.date.today().isoformat()

    def zapis(cesta, kod, lastmod=None):
        if cesta == "404":
            vystup = os.path.join(DIST, "404.html")
        else:
            os.makedirs(os.path.join(DIST, cesta), exist_ok=True)
            vystup = os.path.join(DIST, cesta, "index.html")
            stranky.append((cesta + "/" if cesta else "", lastmod or dnes))
        with open(vystup, "w", encoding="utf-8") as fh:
            fh.write(kod)

    for f in sorted(os.listdir(SRC)):
        if not f.endswith(".html") or f.startswith("_"):
            continue
        jmeno = f[:-5]
        obr.reset()
        zapis("" if jmeno == "index" else jmeno, env.get_template(f).render(), (data["blog"][0]["datum"] if jmeno == "blog" and data.get("blog") else None))
    # služby a oborové stránky: jedna šablona, obsah v _data/sluzby.json (URL = klíč, stejné jako na starém webu)
    for klic in data.get("sluzby", {}):
        if not os.path.exists(os.path.join(SRC, klic + ".html")):
            obr.reset()
            zapis(klic, env.get_template("_sluzba.html").render(klic=klic))
    # články blogu: blog/<slug>/
    for c in data.get("blog", []):
        obr.reset()
        zapis("blog/" + c["slug"], env.get_template("_clanek.html").render(c=c), c["datum"])
    # textové soubory pro vyhledávače a AI (šablony src/*.txt)
    for f in sorted(os.listdir(SRC)):
        if f.endswith(".txt"):
            with open(os.path.join(DIST, f), "w", encoding="utf-8") as fh:
                fh.write(env.get_template(f).render())

    # robots, sitemap, CNAME
    navrh = bool(site.get("navrh"))
    with open(os.path.join(DIST, "robots.txt"), "w") as fh:
        if navrh:
            fh.write("User-agent: *\nDisallow: /\n")
        else:
            fh.write("User-agent: *\nAllow: /\n\n# AI vyhledávače a asistenti – povolený přístup k obsahu\n")
            fh.write("".join(f"User-agent: {r}\nAllow: /\n\n" for r in ROBOTI))
            fh.write(f"Sitemap: {site['url']}sitemap.xml\n")
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for cesta, lastmod in stranky:
            fh.write(f"  <url><loc>{site['url']}{cesta}</loc><lastmod>{lastmod}</lastmod></url>\n")
        fh.write("</urlset>\n")
    open(os.path.join(DIST, ".nojekyll"), "w").close()
    if site.get("domena") and not navrh:
        open(os.path.join(DIST, "CNAME"), "w").write(site["domena"] + "\n")

    print(f"OK: {len(stranky)} stránek, {len(obr.info)} obrázků -> dist/ ({'NÁVRH, noindex' if navrh else 'OSTRÝ WEB, indexovatelný'})")


if __name__ == "__main__":
    try:
        main()
    except BuildError as e:
        sys.exit(f"CHYBA buildu: {e}")
    if "--serve" in sys.argv:
        import functools, http.server, socketserver
        os.chdir(DIST)
        print("http://localhost:8765" + json.load(open(os.path.join(DATA, "site.json")))["base"] + "  (Ctrl+C = konec; base řeš prefixem)")
        socketserver.TCPServer.allow_reuse_address = True
        socketserver.TCPServer(("", 8765), http.server.SimpleHTTPRequestHandler).serve_forever()
