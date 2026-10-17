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

  /* --- reels: přehrání po kliknutí, vždy jen jedno video --- */
  var hraje = null;
  document.querySelectorAll('[data-reel]').forEach(function (ram) {
    var btn = ram.querySelector('.reel-play');
    btn.addEventListener('click', function () {
      if (hraje && hraje !== ram) { var v0 = hraje.querySelector('video'); if (v0) v0.pause(); }
      var v = ram.querySelector('video');
      if (!v) {
        v = document.createElement('video');
        v.src = ram.getAttribute('data-src');
        v.controls = true; v.playsInline = true; v.setAttribute('playsinline', '');
        v.poster = ram.querySelector('img').currentSrc || '';
        v.setAttribute('aria-label', btn.getAttribute('aria-label').replace('Přehrát video: ', 'Video: '));
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
      box.querySelectorAll('.monitor-rec,.monitor-roh').forEach(function (x) { x.hidden = true; });
      if (hraje) { var v = hraje.querySelector('video'); if (v) v.pause(); }
    });
  });

  /* --- formulář (v návrhu ukázkový režim) --- */
  document.querySelectorAll('form.formular').forEach(function (f) {
    var stav = f.querySelector('.formular-stav');
    f.addEventListener('submit', function (e) {
      var endpoint = f.getAttribute('data-endpoint');
      var demo = f.getAttribute('data-demo') === '1';
      e.preventDefault();
      if (f.querySelector('.past input').value) return;
      if (demo || !endpoint) { stav.textContent = 'Ukázka formuláře: v návrhu se nic neodesílá. Po spuštění webu přijde poptávka rovnou na barton@boom-brand.cz.'; return; }
      stav.textContent = 'Odesílám…';
      fetch(endpoint, { method: 'POST', body: new FormData(f), headers: { Accept: 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(r.status); f.reset(); stav.textContent = 'Děkujeme, ozveme se do 24 hodin.'; })
        .catch(function () { stav.textContent = 'Odeslání se nepodařilo. Napište nám prosím na barton@boom-brand.cz.'; });
    });
  });
})();
