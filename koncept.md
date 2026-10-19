# BoomBrand – koncept návrhu (upsell, 17. 10. 2026)

## Tři koncepty (jedna věta, metafora z oboru)
1. **Střižna** – web jako jejich střihový program: metoda BrandFormance™ je časová osa s 11 klipy
   a playheadem, který jede se scrollem; klientské výsledky jsou „exporty“ a svislá videa referencí
   běží jako hotové reels.
2. **Svislý formát 9 : 16** – celý web skládaný z rámečků telefonu, jako feed, který návštěvník
   scrolluje; každý příběh je jeden reel.
3. **Natáčecí den / klapka** – „2–3 hodiny měsíčně“ = jeden natáčecí den; web jako natáčecí plán
   (call sheet) se scénami, klapkou v hero a rozpisem dne.

## Výběr: 1 – Střižna (s prvkem 9 : 16 jen u skutečných videí)
- BoomBrand prodává **systém** (11 kroků, každý měsíc znovu), ne jednotlivé příspěvky. Časová osa
  s playheadem ten systém ukáže lépe než 11 stejných karet na jejich webu.
- Máme reálný materiál z produkce: 4 svislá videa referencí (mp4 z jejich webu), 7 YouTube náhledů
  (CNN Prima News + 6 epizod TalkToWin), fotky ze studia a z natáčení. Koncept 2 by z telefonových
  rámečků udělal klišé a 3 by potřeboval rekvizity (klapka) = kýč.
- Tón klienta: sebevědomý, přímý, „neměříme lajky, měříme poptávky“. Střižna = řemeslo a kontrola.

## Skladba sekcí (úvod)
1. Hero – obří titulek „Vaše jméno prodává.“ (Syne), pod ním monitor náhledu s fotkou z CNN Prima
   News (rámeček hledáčku, REC, popisek) – se scrollem se roztáhne na celou šířku.
2. Důvěřují nám – klidný typografický řádek jmen (bez marquee, bez falešných log).
3. Proč to řešit – světlá editorial sekce: velký citát + text ve dvou sloupcích, dvě doložená čísla
   v kontextu (60 mil. Kč, 2–3 hodiny).
4. **BrandFormance™ – časová osa** (signature 1): sticky „timeline“ se 4 stopami (Strategie,
   Produkce, Distribuce, Měření), 11 klipů, playhead řízený scrollem (CSS view timeline + fallback),
   aktivní klip se zvýrazní; vpravo kroky s popisem. Na konci smyčka „Opakování a růst“.
5. Jak se odlišujeme – plná oranžová plocha, 7 tvrzení velkou Syne (žádné karty).
6. Případové studie – 3 „exporty“, každý jiný layout: Mirka (fotka + 60 mil. Kč), Zlatka (čistě
   typografická, chybí fotka), Petr (fotka + citace + 20M+).
7. **Reels referencí** (signature 2): 4 svislá videa klientů, přehrání kliknutím se zvukem.
8. Zakladatel – Vojtěch Bartoň, portrét, bio, 3 čísla; CNN Prima News + podcast TalkToWin jako
   playlist (YouTube facade, nic se nenačte bez kliknutí).
9. Spolupráce – 4 kroky + cena „od 35 000 Kč měsíčně“, min. 6 měsíců, 2–3 hodiny.
10. FAQ (9 otázek z jejich webu, FAQPage JSON-LD).
11. Kontakt – formulář (ukázkový režim) + telefon, e-mail, Instagram.
Podstránky se stejnými URL: /osobni-znacka/, /firemni-znacka/, /sprava-socialnich-siti/ (jedna
šablona z _data/sluzby.json), /pripadove-studie/, /o-nas/.

## Písmo, paleta, fotky
- **Syne** (jejich logo písmo) 600–800 na nadpisy – široká, výrazná; **Inter** 400–500 na text (jejich
  písmo, ale už ne „všude“); **IBM Plex Mono** jen pro popisky časové osy a timecody (koncept střižny).
  Test háčků 17. 10. OK (Syne regular + 800, Inter, Plex Mono vč. kurzívy). Syne nemá kurzívu → nepoužívat.
- Paleta 1:1 z jejich CSS: #0a0a0a / #0f0c0c / #191514, oranžová #F46527, hover #FF8346, tmavší
  #B74B21, bílá. Navíc světlý „papír“ #EFECE7 pro 2 editorial sekce (rytmus tmavá × světlá × oranžová).
- Fotky jen jejich (web, videa, YouTube náhledy), bez stocku. Svislé fotky se neořezávají na šířku.

## Zakázané vzory – použité a proč
- **Číslování 01–11** u BrandFormance: je to skutečné pořadí kroků metody (jejich obsah).
- **Čísla ve velkém** (60 mil. Kč, 20M+): doložená z jejich webu a vždy u konkrétního příběhu,
  ne samostatná tmavá sekce s countery. Žádné počítadlo.
- Tmavý web: brand je černo-oranžový (theme-color #0a0a0a), ne „tmavý luxus se zlatou“.
- Nic dalšího: bez marquee, zrna, pilulkové navigace, kurzívových slov, polaroidů, indikátoru scrollu.

## Porovnání
- Schválené: Zábranský v2 (video se scrollem roztáhne – stejný princip u hero monitoru), Kling
  (prvek řízený --p), náborový web (obří písmo, celé z barvy loga).
- Odmítnuté: Mailito (chaos, sekce na každou výtku) → jeden příběh „střižna“; Auren/Kalkul (tmavý
  korporát) → tady tma z brandu + oranžová plocha + světlé sekce; Engadin v1 (pás statistik, 4 stejné
  karty) → žádné karty.
- Posledních 5 v registru: display Playfair, Bricolage, Young Serif, Playfair → Syne je nové písmo.
  Skladba (timeline + reels + oranžová plocha) se s nimi neshoduje. Bite Marks Media (také agentura):
  WebGL stuha, Playfair, mega menu – jiný směr.

---

## v2 (17. 10. 2026, podle Rafaela: „výrazně lepší“)
- **Úvod = vrstvená scéna jako hledáček kamery:** rozhovor z CNN Prima News v rámu hledáčku (REC, běžící timecode, rohy), přes něj svislý reels (krátká smyčka z jejich videa s Petrem Vojnarem, bez zvuku, spouští se jen když je vidět), fotka ze studia a plovoucí karty s doloženými čísly (60 mil. Kč, 20M+, 100M+). Vrstvy mají při scrollu různou paralaxu (CSS scroll-driven). Pás „Důvěřují nám“ je součástí úvodu.
- **Signature momenty:** (1) střihová osa BrandFormance (z v1, statická, playhead projede měsíc), (2) Mirka „před a po“: číslo portfolia roste 0 → 60 mil. Kč a osa M0–M3 se plní (CSS @property + view timeline), (3) pás reels + záběry ze zákulisí, který se při scrollu posouvá do strany (na mobilu swipe), (4) Vojta jako editorial s obřím jménem přes velkou fotku, CNN kartou a podcastem, (5) závěr jako celá oranžová plocha „Pojďme točit.“ s formulářem.
- **Řemeslo:** filmové zrno jen na tmavých sekcích úvodu, metody a reels (koncept filmu a natáčení, ne celá stránka, ne fixed), jemné oranžové světlo za scénou a ve výsledcích, hover na kartách studií a reels, průběh scrollu v hlavičce.
- Počty zhlédnutí u jednotlivých reels na webu klienta nejsou, proto u videí jen jméno, role a délka (nic nevymýšlíme).
- Zrno: zakázaný vzor ve výchozím stavu, tady odůvodněný konceptem filmu (lokálně, opacity .07, bez position: fixed).

---

## v3 (19. 10. 2026, po souhlasu klienta: konverze + obsah celého webu + GDPR)
- Koncept Střižna beze změny. Přibyla obsahová signature: **ceník tří balíčků** (prostřední oranžový „Doporučujeme“) se „Za co ručíme“ a **recenze z Googlu** jako papírová sekce (doslovně, se zdrojem).
- Skladba úvodu: hero (+ hvězdy 5,0) → loga klientů → proč → metoda (10 kroků) → výsledky → odlišujeme → reels → recenze → proces + ceník → Vojta → služby (rejstřík) + blog → FAQ → kontakt s „Co si z hovoru odnesete“.
- Nové šablony: `_sluzba.html` pro 9 landingů z `_data/sluzby.json`, `_clanek.html` + `blog.html` (filtr témat), `formular.html` (VSL, minimální hlavička), `tipy.html`, `sluzby.html`, `ochrana-osobnich-udaju.html`.
- Karty článků: typografická obálka jako „klip“ (téma, délka čtení, pás průběhu) – fotky z jeho blogu jsou zčásti AI s nesmyslným textem.
- Písmo: Syne + Inter (Plex Mono pryč, `.tc` = Inter s tabulkovými číslicemi).
- Review 19. 10.: 7/10 po 3 kolech; zbylá výtka „zjednodušit hero na jednu fotku“ vědomě neprovedena – klient odsouhlasil tenhle úvod. Případně nabídnout jako variantu.

---

## v4 (19. 10. 2026 večer, Rafael: „mnohem lepší“)
- Úvod zjednodušen: titulek vlevo, vpravo dvě skutečná reels klientů (smyčka bez zvuku, klik = celé video) s jejich citací. Pryč hledáček, plovoucí čísla a vedlejší fotky (výtka review 3 kola po sobě).
- Důkaz dřív: případové studie hned pod úvodem. Výzva ke konzultaci za metodou.
- Úvodní stránka kratší (pás reels, 4 kroky a 3 díly podcastu pryč). Rytmus pozadí: tma · tma · papír · tma · papír · tma · papír · tma · papír · tma · oranžová.
