# -*- coding: utf-8 -*-
"""Сборка сайта MiddleLands в папку docs/ (её и публикует GitHub Pages).

    python build.py

Никаких зависимостей — только стандартная библиотека Python 3.8+.
Тексты — в content.py, стили — assets/style.css, скрипт — assets/main.js,
ваши фото — в папке img/ (список и размеры — в PHOTOS.md).
"""
import html
import re
import shutil
from pathlib import Path

import content as C

ROOT = Path(__file__).parent
OUT = ROOT / "docs"


# ------------------------------------------------------------------ helpers
def esc(s):
    return html.escape(str(s), quote=True)


def inline(s):
    p = esc(s)
    p = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", p)
    p = re.sub(r"`(.+?)`", r'<code class="cmd">\1</code>', p)
    p = re.sub(r"\[(ЛКМ|ПКМ|F|Shift|Q|E|ПКМ\+Shift|Esc|Пробел|Tab)\]", r"<kbd>\1</kbd>", p)
    return p


def rich(text):
    """Мини-разметка: абзацы, `- ` список, `1. ` нумерованный список, `| a | b |` таблица,
    `### ` подзаголовок, `> ` врезка, **жирный**, `/команда`, [ЛКМ]."""
    lines = str(text).split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            i += 1; continue
        if ln.startswith("### "):
            out.append(f"<h3>{inline(ln[4:])}</h3>"); i += 1; continue
        if ln.startswith("> "):
            out.append(f'<p class="note">{inline(ln[2:])}</p>'); i += 1; continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>"); i += 1
            out.append("<ul>" + "".join(items) + "</ul>"); continue
        if re.match(r"^\d+\. ", ln):
            items = []
            while i < len(lines) and re.match(r"^\d+\. ", lines[i]):
                items.append(f"<li>{inline(re.sub(r'^\d+\. ', '', lines[i]))}</li>"); i += 1
            out.append('<ol class="steps-list">' + "".join(items) + "</ol>"); continue
        if ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head_, body = rows[0], rows[1:]
            th = "".join(f"<th>{inline(c)}</th>" for c in head_)
            tb = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'); continue
        out.append(f"<p>{inline(ln)}</p>"); i += 1
    return "\n".join(out)


def photo(src, hint, cls="", prefix="", alt=""):
    """Слот под фото: если файла ещё нет, показывается рамка с подписью, что сюда положить."""
    name = Path(src).name
    return (f'<figure class="photo {cls}" data-file="{esc(src)}" data-hint="{esc(hint)}">'
            f'<img src="{prefix}{esc(src)}" alt="{esc(alt or hint)}" loading="lazy" '
            f'onerror="this.closest(\'.photo\').classList.add(\'is-empty\');this.remove()">'
            f'<figcaption class="photo-slot"><span class="photo-file">{esc(name)}</span>'
            f'<span class="photo-hint">{esc(hint)}</span></figcaption></figure>')


ICONS = {
    # простые собственные пиктограммы (не логотипы сервисов)
    "shop": '<path d="M3 4h2l2.2 10.2a2 2 0 0 0 2 1.6h7.6a2 2 0 0 0 2-1.5L21 8H6.2"/><circle cx="10" cy="20" r="1.4"/><circle cx="17" cy="20" r="1.4"/>',
    "telegram": '<path d="M21 4 3 11l6.5 2.2L18 7l-6.8 7.4.4 5.6 3.3-4.3 4.6 3.4z"/>',
    "discord": '<path d="M5 6.5C7 5.4 9 5 12 5s5 .4 7 1.5l1.5 9.5c-1.7 1.4-3.6 2.3-5.5 2.6l-1-2c-1.4.3-2.6.3-4 0l-1 2c-1.9-.3-3.8-1.2-5.5-2.6z"/><circle cx="9" cy="12" r="1.3"/><circle cx="15" cy="12" r="1.3"/>',
    "youtube": '<rect x="2.5" y="5.5" width="19" height="13" rx="3.5"/><path d="m10 9.2 5 2.8-5 2.8z"/>',
    "tiktok": '<path d="M14 3v11.5a3.5 3.5 0 1 1-3.5-3.5"/><path d="M14 3c.6 2.6 2.4 4.2 5 4.5"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"/>',
    "check": '<path d="m4 12 5 5L20 6"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
}


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def socials(prefix="", cls="socials"):
    def href(url):
        return (esc(url) + '" target="_blank" rel="noopener') if url.startswith("http") else prefix + esc(url)
    items = "".join(
        f'<li><a class="sigil" href="{href(url)}">{icon(key)}'
        f'<span class="sigil-text"><span class="sigil-name">{esc(label)}</span>'
        f'<span class="sigil-note">{esc(note)}</span></span></a></li>'
        for key, label, url, note in C.LINKS)
    return f'<ul class="{cls}">{items}</ul>'


def ip_plate(ip, note=""):
    return (f'<button class="plate" type="button" data-copy="{esc(ip)}" aria-label="Скопировать адрес {esc(ip)}">'
            f'<span class="plate-ip">{esc(ip)}</span>'
            f'<span class="plate-act">{icon("copy", "ico ico-copy")}{icon("check", "ico ico-ok")}'
            f'<span class="plate-label">Скопировать</span></span></button>'
            + (f'<p class="plate-note">{esc(note)}</p>' if note else ""))


def head(title, desc, prefix):
    url = C.SITE.get("url") or ""
    og = (f'<meta property="og:image" content="{esc(url)}/img/og.jpg">' if url else "")
    return f"""<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
{og}
<meta name="theme-color" content="#0d1115">
<link rel="icon" href="{prefix}img/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,500;0,600;0,700;1,500&family=Alegreya+Sans:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>"""


def nav(prefix, active=""):
    links = [("index.html", "Сервер", "home"), ("guides/index.html", "Гайды", "guides"),
             ("shop.html", "Магазин", "shop")]
    items = "".join(
        f'<a href="{(href if href.startswith("http") else prefix + href)}"'
        f'{" aria-current=page" if key == active else ""}'
        f'{" target=_blank rel=noopener" if href.startswith("http") else ""}>{label}</a>'
        for href, label, key in links)
    return f"""<header class="topbar">
  <a class="brand" href="{prefix}index.html"><img src="{prefix}img/logo-small.png" alt="" onerror="this.remove()"><span>{esc(C.SITE["name"])}</span></a>
  <nav class="topnav" id="topnav">{items}</nav>
  <button class="topbar-ip" type="button" data-copy="{esc(C.SITE["ip"])}">{esc(C.SITE["ip"])}</button>
  <button class="burger" type="button" aria-controls="topnav" aria-expanded="false" aria-label="Меню">{icon("menu")}</button>
</header>"""


def footer(prefix, with_socials=True):
    return f"""<footer class="footer">
  <div class="footer-in">
    <div class="footer-brand">
      <p class="footer-name">{esc(C.SITE["name"])}</p>
      <p class="footer-text">{esc(C.SITE["season"])}, Minecraft Java {esc(C.SITE["version"])}</p>
      {ip_plate(C.SITE["ip"])}
    </div>
    {socials(prefix, "socials socials-compact") if with_socials else ""}
  </div>
  <p class="footer-legal">MiddleLands не связан с Mojang Studios и Microsoft. Minecraft — товарный знак Mojang Synergies AB.</p>
</footer>
<div class="toast" role="status" aria-live="polite"></div>
<button class="to-top" type="button" aria-label="Наверх">↑</button>
<script src="{prefix}assets/main.js" defer></script>
</body>
</html>"""


# ------------------------------------------------------------------ главная
def page_index():
    p = ""
    S = C.SITE
    facts = "".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in C.FACTS)
    realms = "".join(
        f'<article class="realm">{photo(r["img"], r["hint"], "realm-photo")}'
        f'<h3>{esc(r["name"])}</h3><p>{esc(r["text"])}</p></article>' for r in C.REALMS)

    tiles = []
    for g in C.GUIDES:
        tiles.append(
            f'<a class="tile tile-{g["size"]}" href="guides/{g["slug"]}.html">'
            f'{photo(g["img"], g["hint"], "tile-photo")}'
            f'<span class="tile-body"><span class="tile-group">{esc(g["group"])}</span>'
            f'<span class="tile-title">{esc(g["title"])}</span>'
            f'<span class="tile-lead">{esc(g["lead"])}</span><span class="tile-cta">Читать гайд</span></span></a>')

    classes = "".join(
        f'<li class="cls"><img src="assets/classes/{cid}.png" alt="" width="96" height="96" loading="lazy">'
        f'<span class="cls-tier">{esc(tier)}</span><span class="cls-name">{esc(name)}</span>'
        f'<span class="cls-role">{esc(role)}</span><span class="cls-price">от {price} ₽ навсегда</span></li>'
        for cid, name, tier, price, role in C.CLASSES)

    steps = "".join(f'<li><h3>{esc(t)}</h3>{rich(d)}</li>' for t, d in C.STEPS)
    events = "".join(f"<li>{esc(e)}</li>" for e in C.EVENTS_SHORT)
    intro = "".join(f"<p>{esc(x)}</p>" for x in C.INTRO)

    return head(S["title"], S["description"], p) + f"""
<body class="page-home">
{nav(p, "home")}
<main id="main">
  <section class="hero">
    {photo("img/hero.jpg", "Главный кадр: панорама спавна или замка на закате, без интерфейса. 16:9, от 1920×1080", "hero-photo", p, "Мир MiddleLands")}
    <canvas class="embers" aria-hidden="true"></canvas>
    <div class="hero-in">
      <h1 class="hero-title"><img class="hero-logo" src="img/logo.png" alt="{esc(S["name"])}" onerror="this.replaceWith(document.createTextNode('{esc(S["name"])}'))"></h1>
      <p class="hero-sub">Тёмное средневековое RPG-выживание: живой мир, ремёсла, классы и королевства. {esc(S["season"])} уже идёт.</p>
      {ip_plate(S["ip"], "Minecraft Java " + S["version"] + ". Из России — " + S["ip_ru"])}
      <div class="hero-links">
        <a class="btn btn-gold" href="shop.html">{icon("shop")}Открыть магазин</a>
        <a class="btn btn-ghost" href="{esc(C.LINKS[2][2])}" target="_blank" rel="noopener">{icon("discord")}Войти в Discord</a>
      </div>
    </div>
  </section>

  <section class="chronicle wrap reveal" id="about">
    <h2 class="h2">Что такое MiddleLands</h2>
    <div class="chronicle-grid">
      <div class="chronicle-text">{intro}</div>
      <dl class="facts">{facts}</dl>
    </div>
  </section>

  <section class="realms wrap reveal" id="realms">
    <h2 class="h2">Земли</h2>
    <div class="realms-grid">{realms}</div>
  </section>

  <section class="index wrap reveal" id="guides">
    <div class="index-head">
      <h2 class="h2">Механики сервера</h2>
      <p>Всё, чего нет в обычном Minecraft. Нажми на раздел, чтобы открыть подробный гайд.</p>
    </div>
    <div class="tiles">{"".join(tiles)}</div>
  </section>

  <section class="events-band" id="events">
    <div class="wrap events-in">
      <div>
        <h2 class="h2">События по расписанию</h2>
        <p>Публичные ивенты с волнами врагов, заданиями и наградами для всех участников. Анонсы — в Telegram и Discord.</p>
        <a class="link-more" href="guides/events.html">Как устроены события</a>
      </div>
      <ul class="event-list">{events}</ul>
    </div>
  </section>

  <section class="classes wrap reveal" id="classes">
    <div class="index-head">
      <h2 class="h2">Пути героя</h2>
      <p>Девять привилегий с собственными сетами брони, умениями и командами. Каждую неделю — кейс со своим сетом. При апгрейде доплачиваешь только разницу.</p>
    </div>
    <ul class="cls-row">{classes}</ul>
    <a class="btn btn-gold btn-center" href="shop.html">{icon("shop")}Выбрать привилегию</a>
  </section>

  <section class="join wrap reveal" id="join">
    <h2 class="h2">Как начать играть</h2>
    <ol class="steps">{steps}</ol>
  </section>

  <section class="community wrap reveal" id="community">
    <h2 class="h2">Мы на связи</h2>
    {socials(p)}
  </section>
</main>
""" + footer(p, with_socials=False)


# ------------------------------------------------------------------ гайды
def sidebar(prefix, current=""):
    blocks = []
    for grp in C.GROUPS_ORDER:
        items = "".join(
            f'<li><a href="{prefix}guides/{g["slug"]}.html"{" aria-current=page" if g["slug"] == current else ""}>{esc(g["title"])}</a></li>'
            for g in C.GUIDES if g["group"] == grp)
        blocks.append(f'<p class="side-group">{esc(grp)}</p><ul>{items}</ul>')
    return f'<aside class="side"><nav aria-label="Гайды">{"".join(blocks)}</nav></aside>'


def search_box(g):
    """Поиск по таблицам гайда (бестиарий, карта руд). Работает без перезагрузки."""
    if not g.get("search"):
        return ""
    return (f'<div class="g-search" role="search"><label for="g-search-input">Поиск по странице</label>'
            f'<input id="g-search-input" type="search" autocomplete="off" placeholder="{esc(g["search"])}">'
            f'<p class="g-search-count" aria-live="polite"></p></div>')


def page_guide(g, i):
    p = "../"
    secs = "".join(f'<section class="g-sec" id="s{n}"><h2>{esc(t)}</h2>{rich(body)}</section>'
                   for n, (t, body) in enumerate(g["sections"], 1))
    toc = "".join(f'<li><a href="#s{n}">{esc(t)}</a></li>' for n, (t, _) in enumerate(g["sections"], 1))
    tips = ("<aside class='g-tips'><h2>Советы</h2><ul>" + "".join(f"<li>{inline(t)}</li>" for t in g["tips"]) + "</ul></aside>") if g["tips"] else ""
    cmds = ("<section class='g-cmds'><h2>Команды</h2><table><tbody>" + "".join(
        f"<tr><td><code class='cmd'>{esc(c)}</code></td><td>{esc(d)}</td></tr>" for c, d in g["cmds"]) + "</tbody></table></section>") if g["cmds"] else ""
    prev_g = C.GUIDES[i - 1] if i > 0 else None
    next_g = C.GUIDES[i + 1] if i + 1 < len(C.GUIDES) else None
    pager = '<nav class="pager">' + (
        f'<a class="pager-prev" href="{prev_g["slug"]}.html"><span>Назад</span>{esc(prev_g["title"])}</a>' if prev_g else "<span></span>") + (
        f'<a class="pager-next" href="{next_g["slug"]}.html"><span>Дальше</span>{esc(next_g["title"])}</a>' if next_g else "") + "</nav>"
    return head(f'{g["title"]} — гайд MiddleLands', g["lead"], p) + f"""
<body class="page-guide">
<div class="progress" aria-hidden="true"></div>
{nav(p, "guides")}
<main id="main" class="guide-layout wrap">
  {sidebar(p, g["slug"])}
  <article class="g-article">
    <p class="crumbs"><a href="index.html">Гайды</a> / {esc(g["group"])}</p>
    <h1 class="g-title">{esc(g["title"])}</h1>
    <p class="g-lead">{esc(g["lead"])}</p>
    {photo(g["img"], g["hint"], "g-cover", p)}
    {"<nav class='g-toc' aria-label='На этой странице'><ul>" + toc + "</ul></nav>" if len(g["sections"]) > 2 else ""}
    {search_box(g)}
    {secs}
    {tips}
    {cmds}
    {pager}
  </article>
</main>
""" + footer(p)


def page_guides_index():
    p = "../"
    groups = []
    for grp in C.GROUPS_ORDER:
        items = "".join(
            f'<li><a href="{g["slug"]}.html"><span class="gi-title">{esc(g["title"])}</span>'
            f'<span class="gi-lead">{esc(g["lead"])}</span></a></li>'
            for g in C.GUIDES if g["group"] == grp)
        groups.append(f'<section class="gi-group"><h2>{esc(grp)}</h2><ul>{items}</ul></section>')
    return head("Гайды по механикам — MiddleLands", "Все уникальные механики сервера MiddleLands: от первых шагов до королевств.", p) + f"""
<body class="page-guide">
<div class="progress" aria-hidden="true"></div>
{nav(p, "guides")}
<main id="main" class="guide-layout wrap">
  {sidebar(p)}
  <article class="g-article">
    <h1 class="g-title">Гайды</h1>
    <p class="g-lead">Всё, что отличает MiddleLands от обычного Minecraft. Начни с первых шагов — дальше в любом порядке.</p>
    {"".join(groups)}
  </article>
</main>
""" + footer(p)



# ------------------------------------------------------------------ магазин
import shop_data as SD


def _byn(rub):
    v = rub / SD.RUB_PER_BYN
    return (f"{v:.1f}" if v < 100 else f"{v:.0f}").replace(".", ",")


def _price(rub, uah, old_rub=None, old_uah=None):
    old = f'<s class="sp-old">{old_rub} ₽</s>' if old_rub else ""
    oldu = f'<s class="sp-old">{old_uah} ₴</s>' if old_uah else ""
    return (f'<div class="sp-price">'
            f'<span class="sp-rub">{old}<b data-rub>{rub}</b> ₽ <small>≈ <span data-byn>{_byn(rub)}</span> Br</small></span>'
            f'<span class="sp-uah">{oldu}<b data-uah>{uah}</b> ₴</span></div>')


def _buttons(pid, name, code, uah, variant=""):
    mil = f'{SD.MILLIDA}/product/{pid}?server={SD.MILLIDA_SERVER}'
    return (f'<div class="sp-buy">'
            f'<a class="btn btn-gold sp-btn" href="{esc(mil)}" target="_blank" rel="noopener">'
            f'<span class="sp-btn-cur">₽ / Br</span><span class="sp-btn-sub">Оплатить через Millida</span></a>'
            f'<a class="btn btn-ghost sp-btn sp-btn-uah" href="{esc(SD.DONATELLO)}" target="_blank" rel="noopener" '
            f'data-dn data-name="{esc(name)}" data-code="{esc(code)}" data-uah="{uah}" data-variant="{esc(variant)}">'
            f'<span class="sp-btn-cur">₴ Гривны</span><span class="sp-btn-sub">Оплатить через Donatello</span></a></div>')


def _md(text):
    """Описание в стиле Millida: **заголовки** и строки «• »."""
    out, ul = [], []
    def flush():
        if ul: out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in ul) + "</ul>"); ul.clear()
    for ln in text.split("\n"):
        ln = ln.strip()
        if not ln: flush(); continue
        if ln.startswith("• "): ul.append(ln[2:]); continue
        flush()
        m = re.fullmatch(r"\*\*(.+)\*\*", ln)
        out.append(f"<h4>{esc(m.group(1))}</h4>" if m else f"<p>{inline(ln)}</p>")
    flush()
    return "".join(out)


def _priv(p, prefix):
    v30, vf = p["variants"]
    toggle = "".join(
        f'<button type="button" class="sp-var" aria-pressed="{"true" if i == 0 else "false"}" '
        f'data-rub="{rub}" data-uah="{uah}" data-code="{code}" data-label="{esc(lbl)}">{esc(lbl)}<small>{rub} ₽ · {uah} ₴</small></button>'
        for i, (lbl, rub, uah, code) in enumerate(p["variants"]))
    details = (f"**Что входит**\n• Кейс со своим сетом — открывается раз в 7 дней: {p['set']}\n{SD.INCLUDES}\n\n"
               f"**Бонус полного сета**\n" + "\n".join("• " + x for x in p["bonus"]) + "\n\n"
               + ("**Оружие сета**\n" + "\n".join("• " + x for x in p["weapon"]) + "\n\n" if p["weapon"] else "")
               + p["perks"] + "\n\n" + SD.UPGRADE)
    badge = f'<span class="sp-badge">{esc(p["badge"])}</span>' if p.get("badge") else ""
    return f"""<article class="sp-card sp-priv" id="{p['slug']}" style="--acc:{p['accent']}" data-product>
  {photo(f"img/shop/{p['slug']}.png", f"Превью «{p['name']}». Квадрат, от 800×800, прозрачный или тёмный фон", "sp-photo", prefix, p["name"])}
  <div class="sp-body">
    <p class="sp-meta"><span class="sp-tier">Класс {esc(p['tier'])}</span>{badge}</p>
    <h3 class="sp-name">{esc(p['name'])}</h3>
    <p class="sp-short">{esc(p['short'])}</p>
    <p class="sp-lead">{esc(p['lead'])}</p>
    <div class="sp-vars" role="group" aria-label="Срок">{toggle}</div>
    {_price(v30[1], v30[2])}
    {_buttons(p['id'], p['name'], v30[3], v30[2], v30[0])}
    <details class="sp-more"><summary>Что даёт привилегия</summary><div class="sp-desc">{_md(details)}</div></details>
  </div>
</article>"""


def _small(it, prefix, kind="sp-case"):
    return f"""<article class="sp-card {kind}" id="{it['slug']}" style="--acc:{it.get('accent', '#d9a85b')}" data-product>
  {photo(f"img/shop/{it['slug']}.png", f"Иконка «{it['name']}». Квадрат, от 512×512", "sp-photo", prefix, it["name"])}
  <div class="sp-body">
    {f'<p class="sp-meta"><span class="sp-badge">{esc(it["badge"])}</span></p>' if it.get("badge") else ""}
    <h3 class="sp-name">{esc(it['name'])}</h3>
    <p class="sp-short">{esc(it.get('short') or it['desc'])}</p>
    {f'<p class="sp-lead">{esc(it["desc"])}</p>' if it.get("short") else ""}
    {_price(it['rub'], it['uah'], it.get('old_rub'), it.get('old_uah'))}
    {_buttons(it['id'], it['name'], it['code'], it['uah'])}
  </div>
</article>"""


def page_shop():
    p = ""
    privs = "".join(_priv(x, p) for x in SD.PRIVILEGES)
    extras = "".join(_small(x, p, "sp-extra") for x in SD.EXTRAS)
    cases = "".join(_small(x, p) for x in SD.CASES)
    s = SD.SUPPORT
    support = f"""<article class="sp-card sp-extra sp-support" id="support" style="--acc:#FF4D7A">
  <div class="sp-body">
    <h3 class="sp-name">{esc(s['name'])}</h3>
    <p class="sp-short">{esc(s['desc'])}</p>
    <div class="sp-buy">
      <a class="btn btn-gold sp-btn" href="{esc(SD.MILLIDA)}/product/{s['id']}?server={SD.MILLIDA_SERVER}" target="_blank" rel="noopener"><span class="sp-btn-cur">₽ / Br</span><span class="sp-btn-sub">Любая сумма от 10 ₽</span></a>
      <a class="btn btn-ghost sp-btn sp-btn-uah" href="{esc(SD.DONATELLO)}" target="_blank" rel="noopener" data-dn data-free data-name="Поддержка сервера" data-code="SUPPORT" data-uah=""><span class="sp-btn-cur">₴ Гривны</span><span class="sp-btn-sub">Любая сумма от 10 ₴</span></a>
    </div>
  </div>
</article>"""
    toc = [("privileges", "Привилегии"), ("pass", "Боевой пропуск"), ("cases", "Кейсы"), ("how", "Как оплатить в гривнах"), ("faq", "Вопросы")]
    return head("Официальный магазин — MiddleLands", "Привилегии, боевой пропуск и кейсы сервера MiddleLands. Оплата в рублях, белорусских рублях и гривнах.", p) + f"""
<body class="page-shop">
{nav(p, "shop")}
<main id="main" class="shop wrap">
  <header class="shop-head">
    <h1 class="shop-title">Официальный магазин</h1>
    <p class="shop-lead">Привилегии с собственными сетами, боевой пропуск и кейсы. Каждая покупка продлевает серверу жизнь — спасибо, что поддерживаешь MiddleLands.</p>
    <div class="shop-pay">
      <div class="shop-nick">
        <label for="shop-nick-input">Твой ник в Minecraft</label>
        <input id="shop-nick-input" type="text" inputmode="latin" autocomplete="nickname" maxlength="16" placeholder="Например, Steve" spellcheck="false">
        <p class="shop-nick-note">Нужен для оплаты в гривнах: подставим его в форму Donatello. Для Millida ник вводится на её странице.</p>
      </div>
      <ul class="shop-ways">
        <li><b>₽ / Br</b> — оплата через Millida. Цена в белорусских рублях примерная: банк спишет по своему курсу.</li>
        <li><b>₴</b> — оплата через Donatello для игроков из Украины.</li>
      </ul>
    </div>
    <nav class="shop-toc" aria-label="Разделы магазина">{"".join(f'<a href="#{a}">{t}</a>' for a, t in toc)}</nav>
  </header>

  <section class="shop-sec" id="privileges">
    <h2>Привилегии</h2>
    <p class="shop-sec-lead">Классы выстроены лестницей: от C до S+. Каждая следующая включает всё, что дают привилегии ниже, а при апгрейде доплачиваешь только разницу.</p>
    <div class="sp-list">{privs}</div>
  </section>

  <section class="shop-sec" id="pass">
    <h2>Боевой пропуск и поддержка</h2>
    <div class="sp-grid sp-grid-2">{extras}{support}</div>
  </section>

  <section class="shop-sec" id="cases">
    <h2>Кейсы</h2>
    <div class="sp-grid">{cases}</div>
  </section>

  <section class="shop-sec shop-how" id="how">
    <h2>Как оплатить в гривнах</h2>
    <ol class="shop-steps">
      <li><b>Впиши ник</b> в поле вверху страницы. Он сохранится в этом браузере.</li>
      <li><b>Нажми «₴ Гривны»</b> у нужного товара. Откроется Donatello с уже подставленными суммой, ником и названием товара.</li>
      <li><b>Не меняй сумму и сообщение.</b> По ним мы понимаем, что ты купил. Если сумма будет меньше цены, товар не выдадут.</li>
      <li><b>Оплати картой.</b> Товар придёт на сервер после проверки платежа.</li>
    </ol>
  </section>

  <section class="shop-sec" id="faq">
    <h2>Вопросы</h2>
    <details class="shop-q"><summary>Когда придёт покупка?</summary><p>Через Millida — сразу после оплаты. Через Donatello — после проверки платежа, обычно в течение нескольких часов, максимум за сутки.</p></details>
    <details class="shop-q"><summary>Ошибся в нике или покупка не пришла</summary><p>Напиши в Discord в канал поддержки: ник, товар, время и способ оплаты. Разберёмся и выдадим вручную.</p></details>
    <details class="shop-q"><summary>Как работает апгрейд привилегии?</summary><p>Если у тебя уже есть привилегия ниже, при покупке старшей доплачиваешь только разницу. На Millida это считается автоматически, при оплате в гривнах — напиши в поддержку, посчитаем вручную.</p></details>
    <details class="shop-q"><summary>Что значит «30 дней» и «Навсегда»?</summary><p>«30 дней» — привилегия на месяц, потом её можно продлить. «Навсегда» — без срока, пока существует сервер.</p></details>
  </section>
</main>
""" + footer(p)


# ------------------------------------------------------------------ сборка
def build():
    (OUT / "guides").mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "assets", OUT / "assets", dirs_exist_ok=True)
    if (ROOT / "img").exists():
        shutil.copytree(ROOT / "img", OUT / "img", dirs_exist_ok=True)
    (OUT / "index.html").write_text(page_index(), encoding="utf-8")
    (OUT / "guides" / "index.html").write_text(page_guides_index(), encoding="utf-8")
    for i, g in enumerate(C.GUIDES):
        (OUT / "guides" / f'{g["slug"]}.html').write_text(page_guide(g, i), encoding="utf-8")
    (OUT / "shop.html").write_text(page_shop(), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Готово: {OUT} — {len(C.GUIDES) + 3} страниц")


if __name__ == "__main__":
    build()
