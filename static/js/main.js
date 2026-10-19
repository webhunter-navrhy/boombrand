/* BoomBrand – návrh webu. Bez knihoven: menu, reveal, časová osa BrandFormance, reels, YouTube facade, formulář (demo). */
(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* --- mobilní menu --- */
  var burger = document.querySelector('[data-burger]');
  var menu = document.querySelector('[data-menu]');
  if (burger && menu) {
    var zavri = function () { menu.hidden = true; burger.setAttribute('aria-expanded', 'false'); document.body.style.overflow = ''; };
    burger.addEventListener('click', function () {
      var otevrit = menu.hidden;
      menu.hidden = !otevrit;
      burger.setAttribute('aria-expanded', String(otevrit));
      document.body.style.overflow = otevrit ? 'hidden' : '';
    });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) zavri(); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { zavri(); burger.focus(); } });
    window.matchMedia('(min-width: 64.01rem)').addEventListener('change', function (m) { if (m.matches) zavri(); });
  }

  /* --- reveal --- */
  var rev = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rev.forEach(function (el) { io.observe(el); });
  } else {
    rev.forEach(function (el) { el.classList.add('is-in'); });
  }

  /* --- časová osa BrandFormance: playhead projede měsíc, když osa projíždí obrazovkou (jen při scrollu, v klidu nic neběží) --- */
  var tl = document.querySelector('[data-tl]');
  var editor = tl && tl.querySelector('.tl-editor');
  if (editor && !reduce) {
    var klipy = Array.prototype.slice.call(editor.querySelectorAll('[data-tl-klip]'));
    var n = klipy.length, ceka = false, posledni = -1;
    var spocitej = function () {
      ceka = false;
      var r = editor.getBoundingClientRect(), vh = window.innerHeight;
      if (r.bottom < 0 || r.top > vh) return;
      var p = (vh * 0.92 - r.top) / (vh * 0.55);
      p = Math.max(0, Math.min(1, p));
      editor.style.setProperty('--p', p.toFixed(4));
      var hotovo = Math.floor(p * n + 0.0001);
      if (hotovo === posledni) return;
      posledni = hotovo;
      klipy.forEach(function (k) { k.classList.toggle('is-hotovo', +k.getAttribute('data-tl-klip') < hotovo); });
    };
    var naScroll = function () { if (!ceka) { ceka = true; requestAnimationFrame(spocitej); } };
    window.addEventListener('scroll', naScroll, { passive: true });
    window.addEventListener('resize', naScroll, { passive: true });
    spocitej();
  } else if (editor) {
    editor.querySelectorAll('[data-tl-klip]').forEach(function (k) { k.classList.add('is-hotovo'); });
  }


  /* --- hero: smyčky reels hrají jen když jsou vidět --- */
  var scena = document.querySelector('[data-scena]');
  if (scena && !reduce) {
    var zapni = function (ano) {
      scena.querySelectorAll('video[data-autoplay]').forEach(function (v) {
        if (ano) { var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); } else v.pause();
      });
    };
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) { zapni(en[0].isIntersecting); }, { threshold: 0.05 }).observe(scena);
    } else { zapni(true); }
  }

  /* --- pás reels: o kolik se má posunout do strany (spočítá se jen při načtení a změně velikosti) --- */
  var pasObal = document.querySelector('[data-pas]');
  if (pasObal) {
    var pas = pasObal.querySelector('.pas');
    var spocitejPas = function () { pas.style.setProperty('--posun', Math.max(0, pas.scrollWidth - pasObal.clientWidth) + 'px'); };
    spocitejPas();
    window.addEventListener('resize', spocitejPas, { passive: true });
    window.addEventListener('load', spocitejPas);
  }

  /* --- reels: přehrání po kliknutí, vždy jen jedno video --- */
  var hraje = null;
  document.querySelectorAll('[data-reel]').forEach(function (ram) {
    var btn = ram.querySelector('.reel-play');
    btn.addEventListener('click', function () {
      if (hraje && hraje !== ram) { var v0 = hraje.querySelector('video.reel-plne'); if (v0) v0.pause(); }
      var smycka = ram.querySelector('video[data-autoplay]');
      if (smycka) { smycka.pause(); smycka.removeAttribute('data-autoplay'); smycka.hidden = true; }
      var v = ram.querySelector('video.reel-plne');
      if (!v) {
        v = document.createElement('video');
        v.className = 'reel-plne';
        v.src = ram.getAttribute('data-src');
        v.controls = true; v.playsInline = true; v.setAttribute('playsinline', '');
        var po = ram.querySelector('img'); v.poster = po ? (po.currentSrc || po.src) : (smycka ? smycka.poster : '');
        v.setAttribute('aria-label', btn.getAttribute('aria-label').replace(/^Přehrát video( se zvukem)?: /, 'Video: '));
        ram.appendChild(v);
      }
      btn.hidden = true;
      hraje = ram;
      var pr = v.play(); if (pr && pr.catch) pr.catch(function () {});
      v.focus();
    });
  });

  /* --- YouTube facade: nic se nenačte bez kliknutí --- */
  document.querySelectorAll('[data-yt]').forEach(function (box) {
    var btn = box.querySelector('.yt-play, .monitor-play');
    if (!btn) return;
    btn.addEventListener('click', function () {
      var f = document.createElement('iframe');
      f.src = 'https://www.youtube-nocookie.com/embed/' + box.getAttribute('data-yt') + '?autoplay=1&rel=0&modestbranding=1';
      f.title = btn.getAttribute('aria-label').replace('Přehrát ', '');
      f.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
      f.allowFullscreen = true;
      f.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;border:0;z-index:4';
      box.appendChild(f);
      btn.hidden = true;
      box.querySelectorAll('.monitor-rec,.monitor-roh,.hledacek-rec,.hledacek-info,.roh').forEach(function (x) { x.hidden = true; });
      if (hraje) { var v = hraje.querySelector('video.reel-plne'); if (v) v.pause(); }
    });
  });

  /* --- souhlas s cookies: GA4 a Meta Pixel se načtou až po souhlasu (bez souhlasu se nic neměří) --- */
  var CFG = window.BB || {}, M = CFG.mereni || {};
  var KLIC = 'bb-souhlas', VERZE = 1, PLATNOST = 365 * 864e5;
  var lista = document.querySelector('[data-souhlas]');
  var cti = function () {
    try { var x = JSON.parse(localStorage.getItem(KLIC) || 'null'); if (x && x.v === VERZE && Date.now() - x.t < PLATNOST) return x; } catch (e) {}
    return null;
  };
  var nacteno = { a: false, m: false };
  var skript = function (src) { var el = document.createElement('script'); el.async = true; el.src = src; document.head.appendChild(el); };
  var spustMereni = function (s) {
    if (!M.aktivni || !s) return;
    if (s.a && M.ga4 && !nacteno.a) {
      nacteno.a = true;
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
      window.gtag('config', M.ga4, { anonymize_ip: true });
      skript('https://www.googletagmanager.com/gtag/js?id=' + M.ga4);
    }
    if (s.m && M.pixel && !nacteno.m) {
      nacteno.m = true;
      /* oficiální zavaděč Meta Pixelu */
      !function (f, b, e, v, n, t, s2) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
        if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v;
        s2 = b.getElementsByTagName(e)[0]; s2.parentNode.insertBefore(t, s2); }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
      window.fbq('init', M.pixel);
      window.fbq('track', 'PageView');
    }
  };
  /* konverze: poptávka odeslána (jen když návštěvník souhlasil) */
  var konverze = function (ucel) {
    if (window.gtag && nacteno.a) window.gtag('event', 'generate_lead', { form_name: ucel });
    if (window.fbq && nacteno.m) window.fbq('track', 'Lead', { content_name: ucel });
  };
  if (lista) {
    var volby = lista.querySelector('[data-souhlas-volby]');
    var chA = lista.querySelector('[data-souhlas-a]'), chM = lista.querySelector('[data-souhlas-m]');
    var ulozitBtn = lista.querySelector('[data-souhlas-ulozit]'), nastavitBtn = lista.querySelector('[data-souhlas-nastavit]');
    var uloz = function (a, m) {
      var x = { v: VERZE, t: Date.now(), a: !!a, m: !!m };
      try { localStorage.setItem(KLIC, JSON.stringify(x)); } catch (e) {}
      lista.hidden = true;
      document.documentElement.classList.remove('ma-listu');
      /* odvolání souhlasu: už načtené skripty zastaví až nové načtení stránky */
      if ((nacteno.a && !a) || (nacteno.m && !m)) location.reload(); else spustMereni(x);
    };
    var ukaz = function (sNastavenim) {
      var x = cti();
      chA.checked = !!(x && x.a); chM.checked = !!(x && x.m);
      volby.hidden = !sNastavenim; ulozitBtn.hidden = !sNastavenim; nastavitBtn.hidden = !!sNastavenim;
      lista.hidden = false;
      document.documentElement.classList.add('ma-listu');
    };
    lista.querySelector('[data-souhlas-vse]').addEventListener('click', function () { uloz(true, true); });
    lista.querySelector('[data-souhlas-nic]').addEventListener('click', function () { uloz(false, false); });
    nastavitBtn.addEventListener('click', function () { ukaz(true); chA.focus(); });
    ulozitBtn.addEventListener('click', function () { uloz(chA.checked, chM.checked); });
    document.querySelectorAll('[data-cookies-nastaveni]').forEach(function (b) { b.addEventListener('click', function () { ukaz(true); }); });
    var ulozeno = cti();
    if (ulozeno) spustMereni(ulozeno); else ukaz(false);
  }

  /* --- plovoucí tlačítko na mobilu: po úvodní obrazovce, schová se u formuláře a při liště cookies --- */
  var lepici = document.querySelector('[data-lepici]');
  var kontaktSekce = document.getElementById('kontakt');
  if (lepici && kontaktSekce && 'IntersectionObserver' in window) {
    var zaHero = false, uKontaktu = false;
    var prepni = function () { lepici.hidden = !(zaHero && !uKontaktu); };
    var hero = document.querySelector('.hero, .sub-hero, .clanek-hlava');
    if (hero) new IntersectionObserver(function (en) { zaHero = !en[0].isIntersecting; prepni(); }).observe(hero);
    new IntersectionObserver(function (en) { uKontaktu = en[0].isIntersecting; prepni(); }, { rootMargin: '0px 0px 10% 0px' }).observe(kontaktSekce);
  }

  /* --- recenze: rozbalit dlouhý text --- */
  document.querySelectorAll('[data-recenze-vic]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = b.previousElementSibling, otevreno = b.getAttribute('aria-expanded') === 'true';
      t.classList.toggle('is-cela', !otevreno);
      b.setAttribute('aria-expanded', String(!otevreno));
      b.textContent = otevreno ? 'Číst celou recenzi' : 'Sbalit';
    });
  });

  /* --- blog: filtr podle tématu (bez JS se ukáže všechno) --- */
  var filtr = document.querySelector('[data-blog-filtr]');
  if (filtr) {
    filtr.hidden = false;
    var karty = document.querySelectorAll('.blog-karty-vse .blog-karta');
    var prazdno = document.querySelector('[data-blog-prazdno]');
    filtr.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      var k = b.getAttribute('data-kat'), n = 0;
      filtr.querySelectorAll('button').forEach(function (x) { x.setAttribute('aria-pressed', String(x === b)); });
      karty.forEach(function (c) { var ok = k === 'vse' || (' ' + c.getAttribute('data-kat') + ' ').indexOf(' ' + k + ' ') > -1; c.hidden = !ok; if (ok) n++; });
      prazdno.hidden = n > 0;
    });
  }

  /* --- ceník: výběr balíčku se propíše do poptávky --- */
  document.querySelectorAll('[data-balicek]').forEach(function (a) {
    a.addEventListener('click', function () {
      var z = document.querySelector('#kontakt textarea[name="Zpráva"]');
      if (z && !z.value) z.value = 'Mám zájem o balíček ' + a.getAttribute('data-balicek') + ' měsíčně.';
    });
  });

  /* --- formuláře → webhunter-admin (uloží se a přijdou e-mailem na barton@boom-brand.cz) --- */
  var chyba = function (pole, text) {
    var lab = pole.closest('.pole, .volby, .souhlas-pole') || pole.parentNode;
    var p = lab.querySelector('.pole-chyba');
    if (!text) { if (p) p.remove(); pole.removeAttribute('aria-invalid'); return; }
    if (!p) { p = document.createElement('span'); p.className = 'pole-chyba'; lab.appendChild(p); }
    p.textContent = text; pole.setAttribute('aria-invalid', 'true');
  };
  var zkontroluj = function (koren) {
    var prvni = null;
    koren.querySelectorAll('input, select, textarea').forEach(function (el) {
      if (el.type === 'hidden' || el.closest('.past') || el.disabled) return;
      var t = '';
      if (el.type === 'radio') {
        if (!el.required) return;
        var skup = koren.querySelectorAll('input[name="' + el.name + '"]');
        if (el !== skup[0]) return;
        if (!Array.prototype.some.call(skup, function (r) { return r.checked; })) t = 'Vyberte prosím jednu možnost.';
        chyba(el, t); if (t && !prvni) prvni = el; return;
      }
      var v = (el.value || '').trim();
      if (el.required && !v) t = el.tagName === 'SELECT' ? 'Vyberte prosím možnost.' : 'Tohle pole prosím vyplňte.';
      else if (v && el.type === 'email' && !/^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v)) t = 'E-mail nevypadá správně.';
      else if (v && el.type === 'tel' && !/^[+\d][\d\s/().-]{7,23}$/.test(v)) t = 'Telefon nevypadá správně.';
      chyba(el, t); if (t && !prvni) prvni = el;
    });
    if (prvni) prvni.focus();
    return !prvni;
  };
  document.querySelectorAll('form[data-form]').forEach(function (f) {
    var stav = f.querySelector('.formular-stav');
    var start = Date.now();
    f.addEventListener('input', function (e) { if (e.target.getAttribute('aria-invalid')) chyba(e.target, ''); });
    f.addEventListener('change', function (e) { if (e.target.type === 'radio') chyba(f.querySelector('input[name="' + e.target.name + '"]'), ''); });

    /* vícekrokový formulář */
    var kroky = f.hasAttribute('data-kroky') ? Array.prototype.slice.call(f.querySelectorAll('[data-krok]')) : null, ktery = 0;
    if (kroky) {
      var zpet = f.querySelector('[data-zpet]'), dal = f.querySelector('[data-dal]'), odeslat = f.querySelector('[data-odeslat]'), pas = f.querySelector('[data-kroky-pas]');
      var ukazKrok = function (i) {
        ktery = i;
        kroky.forEach(function (k, n) { k.hidden = n !== i; });
        zpet.hidden = i === 0; dal.hidden = i === kroky.length - 1; odeslat.hidden = i !== kroky.length - 1;
        pas.style.width = ((i + 1) / kroky.length * 100) + '%';
        var leg = kroky[i].querySelector('legend'); if (leg) { leg.setAttribute('tabindex', '-1'); leg.focus({ preventScroll: true }); }
        var r = f.getBoundingClientRect(); if (r.top < 0) f.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      };
      dal.addEventListener('click', function () { if (zkontroluj(kroky[ktery])) ukazKrok(ktery + 1); });
      zpet.addEventListener('click', function () { ukazKrok(ktery - 1); });
      ukazKrok(0);
    }

    f.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!zkontroluj(f)) return;
      var hp = f.querySelector('.past input');
      var pole = {};
      f.querySelectorAll('input, select, textarea').forEach(function (el) {
        if (!el.name || el.closest('.past')) return;
        if ((el.type === 'radio' || el.type === 'checkbox') && !el.checked) return;
        var v = (el.value || '').trim(); if (v) pole[el.name] = v;
      });
      if (pole['Příjmení']) { pole['Jméno'] = (pole['Jméno'] + ' ' + pole['Příjmení']).trim(); delete pole['Příjmení']; }
      if (f.querySelector('input[type="checkbox"][name]') && !pole[f.querySelector('input[type="checkbox"][name]').name]) pole[f.querySelector('input[type="checkbox"][name]').name] = 'ne';
      pole['Formulář'] = f.getAttribute('data-ucel');
      var ucel = f.getAttribute('data-ucel');
      var tlacitko = f.querySelector('[type="submit"]');
      if (CFG.demo || !CFG.endpoint) { stav.textContent = 'Ukázka: v návrhu se nic neodesílá.'; return; }
      tlacitko.disabled = true; stav.className = 'formular-stav'; stav.textContent = 'Odesílám…';
      fetch(CFG.endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: f.getAttribute('data-form'), fields: pole, page: location.href.split('#')[0], hp: hp ? hp.value : '', ms: Date.now() - start })
      }).then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok || !j.ok) throw new Error(j.error || j.message || r.status); }); })
        .then(function () {
          konverze(ucel);
          var pdf = f.getAttribute('data-pdf');
          f.classList.add('is-odeslano');
          f.querySelectorAll('.pole, .pole-2, .formular-spod, .souhlas-pole, .krok, .kroky-tlacitka, .kroky-prubeh, [type="submit"], .formular-gdpr').forEach(function (x) { x.hidden = true; });
          stav.className = 'formular-stav is-ok';
          stav.textContent = f.getAttribute('data-dekujeme');
          if (pdf) { var o = f.querySelector('[data-pdf-odkaz]'); o.href = pdf; o.hidden = false; window.open(pdf, '_blank', 'noopener'); }
          stav.setAttribute('tabindex', '-1'); stav.focus();
        })
        .catch(function (err) {
          tlacitko.disabled = false;
          stav.className = 'formular-stav is-chyba';
          stav.textContent = (err && err.message && !/^\d+$/.test(err.message) ? err.message + ' ' : 'Odeslání se nepodařilo. ') + 'Případně napište na barton@boom-brand.cz nebo volejte +420 775 133 711.';
        });
    });
  });
})();
