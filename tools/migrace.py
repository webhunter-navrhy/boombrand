#!/usr/bin/env python3
"""Převod obsahu ze starého webu boom-brand.cz (stažené HTML) do _data/*.json.
   python3 tools/migrace.py <složka se staženými stránkami> <složka s txt výtahy>
Stahuje i obrázky článků a loga klientů do img/. Spouští se jednorázově při migraci; ruční úpravy dělej v _data."""
import html, json, os, re, sys, urllib.request
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES, TXT = sys.argv[1], sys.argv[2]
OLD = "https://boom-brand.cz"
POVOLENE = {"h2", "h3", "h4", "p", "ul", "ol", "li", "table", "thead", "tbody", "tr", "th", "td", "blockquote", "strong", "em", "b", "i", "a", "br"}


def stahni(url, cil):
    cesta = os.path.join(ROOT, "img", cil)
    os.makedirs(os.path.dirname(cesta), exist_ok=True)
    if not os.path.exists(cesta):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        open(cesta, "wb").write(urllib.request.urlopen(req, timeout=30).read())
    return cil


class Telo(HTMLParser):
    """Vytáhne obsah článku (div za úvodní fotkou) a nechá jen povolené značky bez tříd."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.hloubka, self.uvnitr, self.konec, self.za_foto = [], 0, False, False, False

    def handle_starttag(self, t, a):
        a = dict(a)
        if self.konec:
            return
        if not self.uvnitr:
            if t == "figure":
                self.za_foto = True
            if t == "div" and self.za_foto and "space-y-6" in (a.get("class") or ""):
                self.uvnitr, self.hloubka = True, 1
            return
        if t == "div":
            self.hloubka += 1
            return
        if t in POVOLENE:
            if t == "a":
                h = a.get("href", "")
                if h.startswith(OLD):
                    h = h[len(OLD):]
                self.out.append(f'<a href="{html.escape(h, quote=True)}">')
            elif t in ("th", "td") and a.get("scope"):
                self.out.append(f'<{t} scope="{a["scope"]}">')
            else:
                self.out.append(f"<{t}>")

    def handle_endtag(self, t):
        if not self.uvnitr or self.konec:
            return
        if t == "div":
            self.hloubka -= 1
            if self.hloubka == 0:
                self.konec = True
            return
        if t in POVOLENE and t != "br":
            self.out.append(f"</{t}>")

    def handle_data(self, d):
        if self.uvnitr and not self.konec:
            self.out.append(html.escape(d, quote=False))


def meta(h, jmeno):
    m = re.search(r'<meta[^>]+(?:name|property)="%s"[^>]*content="([^"]*)"' % re.escape(jmeno), h)
    return html.unescape(m.group(1)) if m else ""


def titulek(h):
    return html.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1)).strip()


def kategorie(slug):
    """Stejné pravidlo jako filtr na starém /blog (odvozeno ze slugu, článek může být ve víc kategoriích)."""
    k = []
    if re.search(r"znack|personal", slug): k.append("znacka")
    if re.search(r"kolik-stoji", slug): k.append("ceny")
    if re.search(r"instagram|linkedin|socialni|reels|obsahovy|zacit", slug): k.append("site")
    if re.search(r"makler|navratnost|agentur|reklama", slug): k.append("obory")
    return k


def blog():
    clanky = []
    for f in sorted(os.listdir(PAGES)):
        if not f.startswith("blog__"):
            continue
        slug = f[6:-5]
        h = open(os.path.join(PAGES, f), encoding="utf-8").read()
        p = Telo(); p.feed(h)
        telo = re.sub(r"\s+", " ", "".join(p.out)).replace("> <", "><").strip()
        h1 = html.unescape(re.search(r"<h1[^>]*>(.*?)</h1>", h, re.S).group(1))
        h1 = re.sub(r"<[^>]+>", "", h1)
        datum = re.search(r'<time dateTime="([0-9-]+)"', h).group(1)
        cteni = re.search(r"(\d+) min<!-- --> čtení", h)
        fig = re.search(r'<figure[^>]*><img src="([^"]+)" alt="([^"]*)"', h)
        foto = foto_alt = ""
        if fig:
            src = fig.group(1)
            jm = re.sub(r"-[A-Za-z0-9_-]{8}(\.\w+)$", r"\1", os.path.basename(src))
            foto = stahni(OLD + src if src.startswith("/") else src, "blog/" + jm)
            foto_alt = html.unescape(fig.group(2))
        zv = re.search(r'<div class="mt-12[^"]*p-6[^"]*"[^>]*><p[^>]*>(.*?)</p>', h, re.S) or re.search(r'<p class="[^"]*">([^<]{20,400})</p><a[^>]*href="/#kontakt">Domluvit konzultaci', h)
        sl = re.search(r'aria-label="Související služba"><p[^>]*>Související služba</p><a href="([^"]+)"[^>]*>(.*?)</a><p[^>]*>([^<]+)</p>', h)
        clanky.append({
            "slug": slug, "titulek": titulek(h), "popis": meta(h, "description"), "h1": h1,
            "datum": datum, "cteni": int(cteni.group(1)) if cteni else 5, "kategorie": kategorie(slug),
            "foto": foto, "foto_alt": foto_alt, "telo": telo,
            "zaver": html.unescape(re.sub(r"<[^>]+>", "", zv.group(1))).strip() if zv else "",
            "sluzba": {"href": sl.group(1).strip("/"), "text": html.unescape(re.sub(r"<[^>]+>", "", sl.group(2))).replace("→", "").strip(),
                       "popis": html.unescape(sl.group(3))} if sl else None,
        })
    clanky.sort(key=lambda c: (c["datum"], c["slug"]), reverse=True)
    return clanky


def sluzba_z_txt(jmeno, h):
    L = [l for l in open(os.path.join(TXT, jmeno + ".md"), encoding="utf-8").read().split("\n")[2:]]
    i = next(n for n, l in enumerate(L) if l.startswith("# "))
    s = {"stitek": L[i - 1], "h1": L[i][2:].strip(), "titulek": titulek(h), "popis": meta(h, "description"),
         "perex": L[i + 1], "fakta": [], "pilire": [], "postup": [], "faq": [], "cta": {}}
    n = i + 3
    while not re.fullmatch(r"0\d", L[n]):
        if L[n].startswith("## "):
            s["pilire_nadpis"] = L[n][3:].strip(); n += 1; continue
        s["fakta"].append({"k": L[n], "v": L[n + 1]}); n += 2
    while re.fullmatch(r"0\d", L[n]):
        s["pilire"].append({"nazev": L[n + 1].lstrip("# ").strip(), "text": L[n + 2]}); n += 3
    if L[n].startswith("## Jak spolupráce"):
        n += 1
        while re.fullmatch(r"\d", L[n]):
            s["postup"].append({"nazev": L[n + 1].lstrip("# ").strip(), "text": L[n + 2]}); n += 3
    n = next(k for k in range(n, len(L)) if L[k].startswith("## Časté otázky")) + 1
    while L[n].endswith("+"):
        s["faq"].append({"q": L[n][:-1].strip(), "a": L[n + 1]}); n += 2
    s["cta"] = {"nadpis": L[n].lstrip("# ").strip(), "text": L[n + 1]}
    return s


def main():
    clanky = blog()
    json.dump(clanky, open(os.path.join(ROOT, "_data", "blog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"blog: {len(clanky)} článků")
    sl = json.load(open(os.path.join(ROOT, "_data", "sluzby.json"), encoding="utf-8"))
    nove = {"marketingova-agentura-brno": "Marketingová agentura Brno", "sprava-instagramu": "Správa Instagramu",
            "reklama-brno": "Reklama Brno", "osobni-znacka-pro-realitni-maklere": "Pro realitní makléře",
            "osobni-znacka-pro-financni-poradce": "Pro finanční poradce", "linkedin-pro-majitele-firem": "LinkedIn pro majitele firem"}
    for k, menu in nove.items():
        h = open(os.path.join(PAGES, k + ".html"), encoding="utf-8").read()
        d = sluzba_z_txt(k, h)
        d["menu"] = menu
        d.setdefault("foto", sl.get(k, {}).get("foto", ""))
        sl[k] = {**d, **{x: sl[k][x] for x in ("foto", "foto_alt") if k in sl and x in sl[k]}}
        print(k, len(d["fakta"]), len(d["pilire"]), len(d["postup"]), len(d["faq"]))
    json.dump(sl, open(os.path.join(ROOT, "_data", "sluzby.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for src, jm in [("f6697483-eea8-4d86-821a-7ad1bff857ca/logo-tmobile.webp", "tmobile"), ("014186a7-ed75-436b-a417-a793ca0daa3d/logo-sirius.webp", "sirius"),
                    ("005b1d27-a7a9-402b-a62f-1e9d98911178/logo-4fin.webp", "4fin"), ("77c12ba6-a87c-40ab-a7a3-71d72ff73e2f/logo-remax.webp", "remax"),
                    ("304aae25-9097-48ce-8b2a-a33be522dcc2/logo-cnn-prima.webp", "cnn-prima")]:
        stahni(f"{OLD}/__l5e/assets-v1/{src}", f"loga/{jm}.webp")


if __name__ == "__main__":
    main()
