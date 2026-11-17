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
