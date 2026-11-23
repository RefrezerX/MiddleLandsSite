// MiddleLands: копирование IP, мобильное меню, угли над героем.
(() => {
  const toast = document.querySelector('.toast');
  let toastTimer;
  const say = (text) => {
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add('is-on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('is-on'), 2200);
  };

  // Копирование адреса сервера
  document.querySelectorAll('[data-copy]').forEach((el) => {
    el.addEventListener('click', async () => {
      const ip = el.dataset.copy;
      try {
        await navigator.clipboard.writeText(ip);
      } catch (e) {
        const t = document.createElement('textarea');
        t.value = ip; document.body.appendChild(t); t.select();
        document.execCommand('copy'); t.remove();
      }
      el.classList.add('is-copied');
      const label = el.querySelector('.plate-label');
      if (label) label.textContent = 'Скопировано';
      say('Адрес ' + ip + ' скопирован');
      setTimeout(() => {
        el.classList.remove('is-copied');
        if (label) label.textContent = 'Скопировать';
      }, 2200);
    });
  });

  // Мобильное меню
  const burger = document.querySelector('.burger');
  const nav = document.getElementById('topnav');
  if (burger && nav) {
    burger.addEventListener('click', () => {
      const open = nav.classList.toggle('is-open');
      burger.setAttribute('aria-expanded', String(open));
    });
  }

  // Угли из кузни — единственная фоновая анимация, только на главном экране
  const canvas = document.querySelector('.embers');
  if (!canvas || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const ctx = canvas.getContext('2d');
  let w, h, dpr, parts = [], visible = true;
  const resize = () => {
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = w * dpr; canvas.height = h * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  };
  const spawn = (fromBottom) => ({
    x: Math.random() * w,
    y: fromBottom ? h + Math.random() * 40 : Math.random() * h,
    r: Math.random() * 1.8 + 0.6,
    vy: -(Math.random() * 0.6 + 0.25),
    vx: (Math.random() - 0.5) * 0.25,
    life: Math.random() * 0.6 + 0.4,
    hue: 20 + Math.random() * 22,
    t: Math.random() * Math.PI * 2,
  });
  const init = () => {
    resize();
    const n = Math.round(Math.min(110, w / 14));
    parts = Array.from({ length: n }, () => spawn(false));
  };
  const tick = () => {
    if (visible) {
      ctx.clearRect(0, 0, w, h);
      ctx.globalCompositeOperation = 'lighter';
      for (const p of parts) {
        p.t += 0.02;
        p.x += p.vx + Math.sin(p.t) * 0.25;
        p.y += p.vy;
        const fade = Math.max(0, Math.min(1, p.y / h)) * p.life;
        if (p.y < -10 || fade <= 0.02) Object.assign(p, spawn(true));
        const g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.r * 5);
        g.addColorStop(0, `hsla(${p.hue},100%,70%,${0.9 * fade})`);
        g.addColorStop(1, `hsla(${p.hue},100%,50%,0)`);
        ctx.fillStyle = g;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r * 5, 0, Math.PI * 2); ctx.fill();
      }
    }
    requestAnimationFrame(tick);
  };
  new IntersectionObserver((e) => { visible = e[0].isIntersecting; }).observe(canvas);
  addEventListener('resize', resize);
  init(); tick();
})();

// Живость: панель, параллакс, появление секций, прогресс чтения, оглавление, «наверх»
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const bar = document.querySelector('.topbar');
  const hero = document.querySelector('.hero-photo img');
  const prog = document.querySelector('.progress');
  const up = document.querySelector('.to-top');
  const onScroll = () => {
    const y = scrollY;
    if (bar) bar.classList.toggle('is-scrolled', y > 40);
    if (hero && !reduce && y < innerHeight) hero.style.setProperty('--par', (y * 0.25) + 'px');
    if (prog) {
      const h = document.documentElement.scrollHeight - innerHeight;
      prog.style.width = (h > 0 ? (y / h) * 100 : 0) + '%';
    }
    if (up) up.classList.toggle('is-on', y > 900);
  };
  addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (up) up.addEventListener('click', () => scrollTo({ top: 0, behavior: reduce ? 'auto' : 'smooth' }));

  const els = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) els.forEach((e) => e.classList.add('is-in'));
  else {
    const io = new IntersectionObserver((list) => list.forEach((e) => {
      if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
    }), { threshold: 0, rootMargin: '0px 0px -8% 0px' });
    els.forEach((e) => io.observe(e));
  }

  const toc = [...document.querySelectorAll('.g-toc a')];
  if (toc.length) {
    const map = new Map(toc.map((a) => [a.getAttribute('href').slice(1), a]));
    const so = new IntersectionObserver((list) => list.forEach((e) => {
      if (e.isIntersecting) { toc.forEach((a) => a.classList.remove('is-active')); map.get(e.target.id)?.classList.add('is-active'); }
    }), { rootMargin: '-30% 0px -60% 0px' });
    document.querySelectorAll('.g-sec').forEach((s) => so.observe(s));
  }
})();

/* Поиск по таблицам гайда: скрывает строки и разделы без совпадений. */
(function () {
  var input = document.getElementById('g-search-input');
  if (!input) return;
  var count = document.querySelector('.g-search-count');
  var secs = Array.prototype.slice.call(document.querySelectorAll('.g-sec'));
  function norm(s) { return (s || '').toLowerCase().replace(/ё/g, 'е'); }
  function run() {
    var q = norm(input.value.trim());
    var found = 0;
    secs.forEach(function (sec) {
      var rows = sec.querySelectorAll('tbody tr');
      if (!q) {
        sec.hidden = false;
        rows.forEach(function (r) { r.hidden = false; });
        return;
      }
      var head = norm(sec.querySelector('h2') ? sec.querySelector('h2').textContent : '');
      var any = false;
      rows.forEach(function (r) {
        var hit = head.indexOf(q) >= 0 || norm(r.textContent).indexOf(q) >= 0;
        r.hidden = !hit;
        if (hit) { any = true; found++; }
      });
      sec.hidden = !any && head.indexOf(q) < 0;
    });
    count.textContent = q ? (found ? 'Найдено строк: ' + found : 'Ничего не нашлось. Попробуй другое слово.') : '';
  }
  input.addEventListener('input', run);
})();

/* Магазин: ник, выбор срока и ссылки на Donatello (сумма, ник и товар подставляются сами). */
(function () {
  var nick = document.getElementById('shop-nick-input');
  if (!nick) return;
  var KEY = 'ml-shop-nick';
  try { nick.value = localStorage.getItem(KEY) || ''; } catch (e) {}
  var DN = 'https://donatello.to/middlelands';
  var RUB_PER_BYN = 27.7;

  function clean(s) { return (s || '').replace(/[^A-Za-z0-9_]/g, '').slice(0, 16); }
  function link(a) {
    var n = clean(nick.value);
    var q = [];
    if (a.dataset.uah) q.push('a=' + encodeURIComponent(a.dataset.uah));
    if (n) q.push('c=' + encodeURIComponent(n));
    var what = a.dataset.name + (a.dataset.variant ? ' (' + a.dataset.variant + ')' : '');
    q.push('m=' + encodeURIComponent('[' + a.dataset.code + '] ' + what + (n ? ' — ник ' + n : '')));
    a.href = DN + '?' + q.join('&');
  }
  function all() { document.querySelectorAll('[data-dn]').forEach(link); }

  nick.addEventListener('input', function () {
    var v = clean(nick.value);
    if (v !== nick.value) nick.value = v;
    nick.classList.remove('is-missing');
    try { localStorage.setItem(KEY, v); } catch (e) {}
    all();
  });

  document.addEventListener('click', function (e) {
    var a = e.target.closest('[data-dn]');
    if (a && !clean(nick.value)) {
      e.preventDefault();
      nick.classList.add('is-missing');
      nick.scrollIntoView({ behavior: 'smooth', block: 'center' });
      setTimeout(function () { nick.focus(); }, 350);
      var t = document.querySelector('.toast');
      if (t) { t.textContent = 'Сначала впиши ник — без него покупку не выдать'; t.classList.add('is-on'); setTimeout(function () { t.classList.remove('is-on'); }, 2600); }
      return;
    }
    var b = e.target.closest('.sp-var');
    if (!b) return;
    var card = b.closest('[data-product]');
    card.querySelectorAll('.sp-var').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
    var rub = +b.dataset.rub;
    card.querySelector('.sp-price [data-rub]').textContent = rub;
    card.querySelector('.sp-price [data-uah]').textContent = b.dataset.uah;
    var byn = rub / RUB_PER_BYN;
    card.querySelector('.sp-price [data-byn]').textContent = (byn < 100 ? byn.toFixed(1) : byn.toFixed(0)).replace('.', ',');
    var dn = card.querySelector('[data-dn]');
    dn.dataset.uah = b.dataset.uah; dn.dataset.code = b.dataset.code; dn.dataset.variant = b.dataset.label;
    link(dn);
  });
  all();
})();
