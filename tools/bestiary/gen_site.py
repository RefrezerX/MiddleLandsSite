# -*- coding: utf-8 -*-
"""Собирает разделы бестиария и рудной карты для сайта из реальных конфигов сервера.
Вход: rules.json (RandomSpawns MythicMobs), wildlife_biomes.txt, ores_raw.txt,
      Waterlogged-RandomSpawns-Biomes.yml (из /home/claude/water).
Выход: bestiary_data.py с MOBS_SECTIONS и ORE_SECTIONS."""
import json, re, yaml
from biomes_ru import names as bnames, name as bname

R = {r["id"]: r for r in json.load(open("rules.json"))}
WL = {}
for l in open("wildlife_biomes.txt"):
    k, v = l.strip().split("|"); WL[k] = v.split(",")
WATER = yaml.safe_load(open("Waterlogged-RandomSpawns-Biomes.yml"))


def pct(x):
    v = x * 100
    if v >= 10: s = f"{v:.0f}"
    elif v >= 1: s = f"{v:.1f}".rstrip("0").rstrip(".")
    elif v >= 0.1: s = f"{v:.2f}".rstrip("0").rstrip(".")
    else: s = f"{v:.3f}".rstrip("0").rstrip(".")
    return s.replace(".", ",") + "%"


def types(rid):
    out = []
    for t in R[rid]["T"].split(","):
        p = t.strip().split()
        out.append((p[0], float(p[1]) if len(p) > 1 else 1.0))
    return out


def share(rid, mob):
    t = types(rid); tot = sum(w for _, w in t)
    w = sum(w for m, w in t if m == mob)
    return float(R[rid]["c"]) * w / tot


def biomes(rid):
    b = R[rid].get("B", "")
    return [x for x in b.split(",") if x]


def cap(rid):
    m = re.search(r"amount=<(\d+);radius=(\d+)", R[rid].get("C", "")) or re.search(r"a=<(\d+);r=(\d+)", R[rid].get("C", ""))
    return (int(m.group(1)), int(m.group(2))) if m else None


def capt(rid):
    c = cap(rid)
    if not c: return ""
    n, r = c
    return f"не больше {n} в радиусе {r} бл." if n > 1 else f"один на {r} бл. вокруг"


HOSTILE = "ночных монстров (зомби, скелетов, пауков, криперов, ведьм, эндерменов)"

# ------------------------------------------------------------------ мобы
S = []

S.append(("Как читать бестиарий", """Все шансы ниже взяты прямо из настроек сервера. Мобы появляются двумя способами.
- **Замена.** Игра хочет заспавнить обычного моба, а вместо него появляется особый. Шанс показывает, какая доля обычных мобов этого вида превращается в особого. «6% от ночных монстров» значит, что примерно каждый семнадцатый монстр в этом биоме будет эльфом.
- **Свой спавн.** Моб появляется сам в подходящем месте рядом с игроком. Шанс показывает вероятность каждой попытки, а лимит не даёт мобам скапливаться.
Почти у всех мобов есть **лимит**: если рядом уже есть такой же, новый не появится. Поэтому редкого босса можно встретить только одного на большой округе.
> Боссы с шансом 0,1% — настоящая редкость. Их проще встретить на событиях: на «Жизни на кон» красный сектор колеса вызывает одного из них."""))

# --- скелеты
rid = "SKM_All_Skeletons"
rows = ["| Моб | Шанс | Здоровье | Как опасен |"]
desc = {"skeleton_archer": ("Скелет-лучник", 20, "Держит дистанцию, стреляет метко"),
        "skeleton_melee": ("Скелет-воин", 24, "Бежит вплотную, бьёт сериями"),
        "skeleton_mage": ("Скелет-маг", 18, "Бьёт магическими снарядами издалека"),
        "skeleton_elite": ("Элитный скелет", 45, "Сильнее и крепче, ведёт за собой остальных")}
for m, w in types(rid):
    n, hp, d = desc[m]
    rows.append(f"| **{n}** | {pct(share(rid, m))} скелетов | {hp} | {d} |")
S.append(("Скелеты", "**Каждый** обычный скелет, зимогор и болотник в любом биоме заменяется на одного из четырёх видов:\n" + "\n".join(rows) +
          "\nОни же приходят из спавнеров в подземельях. С каждого падают кости и редкие трофеи."))

# --- криперы
cre = [("CR_Plains", "Равнинный крипер"), ("CR_Spruce", "Еловый крипер"), ("CR_Snowy", "Снежный крипер"),
       ("CR_Hills", "Горный крипер"), ("CR_DarkOak", "Тёмно-дубовый крипер"), ("CR_Jungle", "Тропический крипер"),
       ("CR_Bamboo", "Бамбуковый крипер"), ("CR_Desert", "Пустынный крипер"), ("CR_Badlands", "Крипер пустошей"),
       ("CR_Savannah", "Саванный крипер"), ("CR_Swamp", "Болотный крипер"), ("CR_Beach", "Пляжный крипер"),
       ("CR_Mushroom", "Грибной крипер"), ("CR_Cave_Dripstone", "Сталактитовый крипер"),
       ("CR_Cave_Mushroom", "Грибной крипер"), ("CR_Cave_Snowy", "Снежный крипер"), ("CR_Cave_Jungle", "Тропический крипер"),
       ("CR_Cave_Cave", "Пещерный крипер")]
rows = ["| Крипер | Где |"]
merged = {}
for rid, n in cre:
    merged.setdefault(n, []).extend(biomes(rid))
for n, bl in merged.items():
    rows.append(f"| **{n}** | {bnames(bl)} |")
rows.append("| **Пещерный крипер** | Любой биом ниже Y 40 |")
rows.append("| **Рождественский крипер** | Все остальные биомы |")
S.append(("Криперы", "**Каждый** крипер заменяется на крипера своего биома. Выглядят по-разному, взрываются одинаково больно.\n" + "\n".join(rows)))

# --- пауки
P = "BLS_Poison"; ST = "BLS_Strangler"
S.append(("Пауки", f"""**30%** обычных пауков превращаются в особых. Рядом может быть не больше двух особых пауков.
| Паук | Где | Здоровье |
| **Ядовитый паук** | {bnames(biomes(P))} | 34 |
| **Паук-душитель** | {bnames(biomes(ST))}. Также в любом другом биоме ниже Y 40 | 46 |
| **Паук-охотник** | Все остальные биомы выше Y 40 | 40 |"""))

# --- биомные
def wrow(rid, n, mob, hp, extra=""):
    b = biomes(rid)
    where = bnames(b) if b else "любые биомы"
    return f"| **{n}** | {where}{extra} | {pct(share(rid, mob))} от {{SRC}} | {hp} | {capt(rid)} |"


def grow(rid, mobs, extra=""):
    """Одна строка на правило: несколько мобов с их долями."""
    b = biomes(rid)
    where = (bnames(b) if b else "любые биомы") + extra
    if len(mobs) == 1:
        m, n, hp = mobs[0]
        return f"| **{n}** | {where} | {pct(share(rid, m))} от {{SRC}} | {hp} | {capt(rid)} |"
    who = "; ".join(f"**{n}** {pct(share(rid, m))}" for m, n, hp in mobs)
    hps = "–".join(sorted({str(hp) for _, _, hp in mobs}, key=int)[::max(1, len({hp for _,_,hp in mobs})-1)])
    return f"| {who} | {where} | {pct(float(R[rid]['c']))} от {{SRC}} всего | {hps} | {capt(rid)} |"

head = "| Моб | Где | Шанс | Здоровье | Лимит |"
forest = [head,
          grow("W_Elves", [("Elven_Swordsman", "Эльф-мечник", 40), ("Elven_Ranger", "Эльф-следопыт", 30), ("Elven_Mage", "Эльф-маг", 32), ("Elven_Runebear", "Рунический медведь", 70)]),
          wrow("W_Elven_Druid", "Эльф-друид (босс)", "Elven_Druid", 650),
          wrow("W_Nature_Sprite", "Дух природы", "nature_sprite", 8),
          wrow("W_Rooted_Warrior", "Укоренённый воин (босс)", "rooted_warrior", 180),
          wrow("W_Woodland_Assassin", "Лесной убийца (босс)", "woodland_assassin", 160),
          wrow("W_Lady_of_the_Forest", "Владычица леса (босс)", "lady_of_the_forest", 400),
          wrow("W_Glume", "Глюм (босс)", "glume", 350)]
S.append(("Леса и луга", "Появляются на поверхности вместо " + HOSTILE + ".\n" + "\n".join(forest).replace("{SRC}", "монстров") +
          f"\n> Глюм живёт ещё и на Грибных полях: там им становится {pct(share('W_Glume_Mushroom', 'glume'))} появляющихся грибных коров."))

mount = [head,
         grow("W_Goblins", [("gp2_goblin_warrior", "Гоблин-воин", 24), ("gp2_goblin_archer", "Гоблин-лучник", 20), ("gp2_goblin_club", "Гоблин с дубиной", 24), ("gp2_goblin_knife", "Гоблин с ножом", 24), ("gp2_goblin_frying_pan", "Гоблин со сковородой", 24), ("gp2_goblin_wooden_spoon", "Гоблин с ложкой", 24), ("gp2_goblin_broken_pitchfork", "Гоблин с вилами", 24)]),
         wrow("W_Goblin_Shaman", "Гоблин-шаман", "gp2_goblin_shaman", 60),
         wrow("W_Goblin_King", "Король гоблинов (босс)", "gp2_goblin_king", 300),
         wrow("W_Eldric", "Элдрик (босс)", "LRD_eldric", 450, ", только выше Y 62"),
         wrow("W_Tengu", "Тэнгу (босс)", "tengu", 280)]
S.append(("Тайга, нагорья и горы", "Появляются на поверхности вместо " + HOSTILE + ". Гоблины бродят отрядами до шести.\n" + "\n".join(mount).replace("{SRC}", "монстров")))

wet = [head,
       grow("W_Sewer_Gang", [("Nocsy_FPV3-Rat", "Крыса", 18), ("Nocsy_FPV3-Spider", "Болотный паук", 20), ("Nocsy_FPV3-Mosquito", "Комар", 8), ("Nocsy_FPV3-Leech", "Пиявка", 20)]),
       wrow("W_Kingpin", "Король крыс (босс)", "Nocsy_FPV3-Kingpin", 600),
       wrow("W_Kappa", "Каппа", "kappa", 45),
       grow("W_Yurei", [("yurei_wandering", "Юрэй бродячий", 45), ("yurei_weeping", "Юрэй плачущий", 45)]),
       wrow("W_Oni", "Они (босс)", "oni", 700)]
S.append(("Болота, реки и сакуровые рощи", "Появляются вместо " + HOSTILE + ". Болотная банда приходит и под землёй, и днём в тени.\n" + "\n".join(wet).replace("{SRC}", "монстров")))

cold = [head, wrow("W_Yeti", "Йети (босс)", "lr_yeti", 1000), wrow("W_Kriger", "Кригер (босс)", "kriger", 900)]
hot = [head, wrow("W_Ork_Nil", "Нил — орк-берсерк (босс)", "ORK_NIL", 450)]
sol = R["W_Solar"]; st = types("W_Solar"); tot = sum(w for _, w in st)
soln = {"sol_sprite": ("Солнечный дух", 10), "sol_seer": ("Солнечный провидец", 60), "solarmancer": ("Солнечный чародей", 60), "sun_warrior": ("Солнечный воин", 90)}
solrows = "| " + "; ".join(f"**{soln[m][0]}** {pct(w / tot)}" for m, w in st) + f" | {bnames(biomes('W_Solar'))}, только днём | свой спавн, {pct(float(sol['c']))} за попытку; проценты — доля каждого вида | 10–90 | {capt('W_Solar')} |"
S.append(("Снега, саванны и пустыни", "\n".join(cold + hot[1:]).replace("{SRC}", "монстров") + "\n" + solrows +
          "\n> Каждая тысячная корова в мире — не простая. Это приманка **Вендиго**: рядом с такой коровой появляется сам Вендиго (350 здоровья)."))

# --- дикая природа
wl = [("Bear_Brown", "Бурый медведь", 50), ("Bear_Black", "Чёрный медведь", 40), ("Bear_Polar", "Белый медведь", 60),
      ("Bear_Panda", "Панда", 40), ("Rat", "Крысы: чёрная, бурая, серая", 8), ("Squirrel", "Белки: бурая, рыжая, серая", 6),
      ("Duck", "Утки: белая и кряква", 6), ("Crab", "Крабы: красный, илистый, рак-отшельник", 10),
      ("Crocodile", "Крокодилы: гребнистый и кубинский", 45)]
rows = ["| Животное | Где | Здоровье |"]
for k, n, hp in wl:
    rows.append(f"| **{n}** | {bnames(WL[k])} | {hp} |")
rows.append(f"| **Светлячки** | Везде, кроме пустынь и снегов | 2 |")
S.append(("Дикие животные", f"""Живут сами по себе: свой спавн с шансом {pct(float(R['Bear_Brown_Random']['c']))} за попытку, не больше одного зверя на чанк. Крабы появляются и на берегу, и в воде. Медведей и крокодилов лучше обходить стороной.
""" + "\n".join(rows) + "\nПочти любого из них можно приручить и держать как питомца."))

# --- море
WATER_NAME = {}
for line in """Shark|Акула
Shark_2|Акула
Swordfish|Рыба-меч
SeaSlug|Морской слизень
Manta_Ray|Скат-манта
Jellyfish|Медуза
Jellyfish_2|Медуза
Sunfish|Рыба-луна
Starfish|Морская звезда
Catfish|Сом
Dolphin|Дельфин
Lobster|Омар
Lobster_2|Омар
Seabass|Морской окунь
Manatee|Ламантин
SpiderCrab|Краб-паук
MahiMahi|Махи-махи
Oarfish|Сельдяной король
ElectricEel|Электрический угорь
TropicalFish|Тропическая рыба
TropicalFish_2|Тропическая рыба
TropicalFish_3|Тропическая рыба
TropicalFish_4|Тропическая рыба
Clownfish|Рыба-клоун
BlueGlaucus|Голубой дракон
BettaFish|Петушок
BettaFish_2|Петушок
BettaFish_3|Петушок
Doryfish|Рыба-хирург
GardenEel|Садовый угорь
MantisShrimp|Рак-богомол
Narwhal|Нарвал
Crab|Краб
Seahorse|Морской конёк
Lionfish|Крылатка
OceanSnail|Морская улитка
OrcaWhale|Косатка
BoxJellyfish|Морская оса
Anglerfish|Удильщик
Nautilus|Наутилус
Piranha|Пиранья
SeaAngel|Морской ангел
Barracuda|Барракуда
HammerheadShark|Акула-молот
HammerheadShark_2|Акула-молот
Octopus|Осьминог
Octopus_2|Осьминог
Stingray|Хвостокол
Pufferfish|Рыба-фугу
PearlClam|Жемчужный моллюск
PistolShrimp|Рак-щелкун
GiantSquid|Гигантский кальмар""".split("\n"):
    a, b = line.split("|"); WATER_NAME[a] = b
VAN = {"TROPICAL_FISH": "тропических рыб", "COD": "трески", "SALMON": "лосося", "SQUID": "кальмаров",
       "GLOW_SQUID": "светящихся кальмаров", "DOLPHIN": "дельфинов", "PUFFERFISH": "иглобрюхов"}
HP = {"Shark": 30, "Swordfish": 20, "SeaSlug": 10, "Manta_Ray": 15, "Jellyfish": 12, "Sunfish": 20, "Starfish": 5, "Catfish": 10,
      "Dolphin": 22, "Lobster": 8, "Seabass": 8, "Manatee": 40, "SpiderCrab": 10, "MahiMahi": 18, "Oarfish": 14, "ElectricEel": 12,
      "TropicalFish": 4, "Clownfish": 4, "BlueGlaucus": 12, "BettaFish": 4, "Doryfish": 4, "GardenEel": 8, "MantisShrimp": 10,
      "Narwhal": 24, "Crab": 8, "Seahorse": 7, "Lionfish": 14, "OceanSnail": 10, "OrcaWhale": 60, "BoxJellyfish": 20,
      "Anglerfish": 15, "Nautilus": 10, "Piranha": 9, "SeaAngel": 12, "Barracuda": 24, "HammerheadShark": 35, "Octopus": 12,
      "Stingray": 13, "Pufferfish": 8, "PearlClam": 10, "PistolShrimp": 8, "GiantSquid": 60}
agg = {}
for rid, r in WATER.items():
    tl = [(t.split()[0].replace("MSO_", ""), float(t.split()[1])) for t in r["Types"]]
    tot = sum(w for _, w in tl)
    van = re.search(r"entitytype\{t=([A-Z_]+)\}", " ".join(r["Conditions"]))
    for m, w in tl:
        sp = WATER_NAME[m]
        a = agg.setdefault(sp, {"b": [], "rep": {}, "add": False, "id": re.sub(r"_\d$", "", m)})
        a["b"] += r["Biomes"]
        if r["Action"] == "REPLACE":
            v = VAN[van.group(1)]
            a["rep"][v] = a["rep"].get(v, 0) + r["Chance"] * w / tot
        else:
            a["add"] = True
rows = ["| Существо | Где | Шанс | Здоровье |"]
for sp in sorted(agg):
    a = agg[sp]
    best = sorted(a["rep"].items(), key=lambda x: -x[1])
    ch = "; ".join(f"до {pct(v)} {k}" for k, v in best[:2])
    if a["add"]: ch = (ch + "; " if ch else "") + "плюс свой спавн в воде"
    rows.append(f"| **{sp}** | {bnames(a['b'])} | {ch} | {HP.get(a['id'], '')} |")
S.append(("Моря, реки и озёра", """В воде живут 40 видов морских существ. Часть подменяет обычных рыб и кальмаров, часть появляется сама прямо в воде рядом с игроком. В одном месте может собраться не больше 24 существ, а крупные хищники — акулы, рыба-меч, косатки — плавают поодиночке, по одному на 96 блоков.
Где сколько живности:
- **Тёплые моря** — самые живые: рифовые рыбы, раки-щелкуны и раки-богомолы, жемчужницы, осьминоги, наутилусы, акулы-молоты.
- **Обычный и умеренно-тёплый океан** — окуни, скаты, крабы, омары, медузы, дельфины.
- **Холодные и ледяные моря** — омары, крабы-пауки, морские ангелы, нарвалы и косатки.
- **Глубоководье** — удильщики, сельдяные короли и гигантский кальмар.
- **Реки, болота и пруды в джунглях** — сомы, петушки, электрические угри, пираньи, ламантины.
""" + "\n".join(rows) + "\n> Хищники кусаются: акулы, барракуды, пираньи, морские осы и электрические угри нападают на ныряльщиков."))

# --- глубокая тьма
dd = [("random_sculk_crabby", "Скалковый крабик", 20), ("random_sculk_screamer", "Скалковый крикун", 40),
      ("random_sculked_crustacean", "Скалковый ракообразный", 60), ("random_soul_bearer", "Носитель душ", 30),
      ("random_sculk_sentinel", "Скалковый часовой (босс)", 300), ("random_echo_enshrouder", "Эхо-окутыватель (босс)", 180)]
rows = ["| Моб | Как часто | Здоровье | Лимит |"]
for rid, n, hp in dd:
    rows.append(f"| **{n}** | раз в {int(R[rid]['cd']) // 60} мин | {hp} | {capt(rid)} |")
S.append(("Глубокая тьма", "Скалковые твари живут только в биоме Глубокая тьма. Каждый вид появляется сам, если рядом нет такого же.\n" + "\n".join(rows)))

# --- незер
nn = [("N_Lava_Mite", "Лавовый клещ", "Lava_Mite", "магмовых кубов", 12), ("N_Lava_Piranha", "Лавовая пиранья", "Lava_Piranha", "лавомерок", 14),
      ("N_Lost_Soul", "Потерянная душа", "Lost_Soul", "скелетов, гастов, эндерменов, визер-скелетов", 18),
      ("N_Nether_Mushroom", "Адский гриб", "Nether_Mushroom", "зомби-пиглинов, хоглинов, эндерменов, пиглинов", 18),
      ("N_Hellhound", "Адская гончая", "Hellhound", "зомби-пиглинов, хоглинов, магмовых кубов, гастов", 40),
      ("N_Fire_Imp", "Огненный бес", "Fire_Imp", "зомби-пиглинов, гастов, магмовых кубов, ифритов", 22),
      ("N_Dark_Imp", "Тёмный бес", "Dark_Imp", "эндерменов, скелетов, гастов, визер-скелетов", 50),
      ("N_Blaze_King", "Король ифритов (босс)", "Blaze_King", "ифритов", 350),
      ("N_Magma_Wyrm", "Магмовый змей (босс)", "MAGMA_WYRM", "магмовых кубов и гастов", 220)]
rows = ["| Моб | Где | Шанс | Здоровье |"]
for rid, n, m, src, hp in nn:
    b = biomes(rid)
    rows.append(f"| **{n}** | {bnames(b) if b else 'весь Незер'} | {pct(share(rid, m))} {src} | {hp} |")
S.append(("Незер", "Появляются вместо обычных обитателей Незера, включая биомы Incendium. Рядом может быть не больше четырёх одного вида.\n" + "\n".join(rows)))

# --- энд
en = [("random_enderling", "Эндерлинг", 30), ("random_end_wraith", "Призрак Энда", 24), ("random_ender_crawler", "Эндер-ползун", 45),
      ("random_enderbruiser", "Эндер-громила", 70), ("random_ender_watchman", "Эндер-страж", 80), ("random_end_strider", "Эндер-странник", 260),
      ("random_endermauler", "Эндер-терзатель", 300), ("random_empowered_enderling", "Усиленный эндерлинг", 48),
      ("random_empowered_end_wraith", "Усиленный призрак Энда", 38), ("random_empowered_ender_crawler", "Усиленный эндер-ползун", 72),
      ("random_empowered_enderbruiser", "Усиленный эндер-громила", 110), ("random_empowered_ender_watchman", "Усиленный эндер-страж", 128),
      ("random_empowered_end_strider", "Усиленный эндер-странник", 420), ("random_empowered_endermauler", "Усиленный эндер-терзатель", 480)]
rows = ["| Моб | Как часто | Здоровье | Лимит |"]
for rid, n, hp in en:
    cd = int(R[rid]["cd"])
    every = f"раз в {cd // 60} мин" if cd >= 60 else f"раз в {cd} с"
    rows.append(f"| **{n}** | {every}, шанс {pct(float(R[rid]['c']))} | {hp} | {capt(rid)} |")
S.append(("Энд", "Порождения Энда появляются на поверхности островов, включая острова Nullscape. На мелких островах вместо них встречается усиленный эндер-странник.\n" + "\n".join(rows)))

# --- особые
S.append(("Особые встречи", f"""| Моб | Где | Шанс | Здоровье |
| **Рыцарь-скелет** | Где угодно на суше | {pct(float(R['RandomSkeletalKnight']['c']))} от всех появляющихся мобов | 36 |
| **Король скелетов (босс)** | Под открытым небом на суше | {pct(float(R['RandomSkeletonKing']['c']))} от всех появляющихся мобов | 600 |
| **Затонувший корабль** | {bnames(biomes('W_Kraken'))} | {pct(share('W_Kraken', 'shipwreck'))} светящихся кальмаров; один на 512 бл. | — |
| **Вендиго** | Любой биом: появляется рядом с особой коровой | {pct(share('W_Wendigo_Cow', 'WENDIGO_COW'))} коров | 350 |
> Затонувший корабль — логово **Кракена** (800 здоровья). Без отряда к нему не подплывай."""))

# --- боссы
S.append(("Все боссы мира", """| Босс | Здоровье | Где искать |
| Йети | 1000 | Заснеженные пики и ледники |
| Кригер | 900 | Заснеженная тайга и равнины |
| Кракен | 800 | Логово в глубоком океане, событие «Проклятье Дейви Джонса» |
| Крампус | 800 | Рождественское событие |
| Они | 700 | Сакуровые рощи и вулканы |
| Эльф-друид | 650 | Березняки, цветочные леса, лавандовые и лунные земли |
| Король скелетов | 600 | Где угодно под открытым небом |
| Король крыс | 600 | Болота |
| Эндер-терзатель | 300–480 | Энд |
| Нил — орк-берсерк | 450 | Саванны |
| Элдрик | 450 | Горы выше Y 62 |
| Гоблинский мех | 450 | Колесо на «Жизни на кон» |
| Владычица леса | 400 | Лес, тёмный лес, древняя тайга |
| Король ифритов | 350 | Незер, событие «Марш нечисти» |
| Глюм | 350 | Тёмный лес, грибные пещеры и Грибные поля |
| Вендиго | 350 | Рядом с особой коровой в любом биоме |
| Король гоблинов | 300 | Тайга и нагорья, событие «Самогонный слёт» |
| Скалковый часовой | 300 | Глубокая тьма |
| Тэнгу | 280 | Пики гор и сакуровые рощи |
| Магмовый змей | 220 | Базальтовые и вулканические дельты Незера |
| Укоренённый воин | 180 | Лес, тёмный лес, древняя тайга |
| Эхо-окутыватель | 180 | Глубокая тьма |
| Лесной убийца | 160 | Лес, тёмный лес, древняя тайга |
Перед боем:
1. Собери отряд — в одиночку большинство боссов не одолеть.
2. Возьми еду хорошего качества, лекарства и запас патронов или маны.
3. Изучи атаки: у каждого босса есть приём, от которого нужно уклоняться.
Арена боссов — `/warp Boss_Arena`."""))

# --- события
S.append(("Мобы на событиях", """| Событие | Кто приходит | Босс |
| Самогонный слёт | Гоблины всех видов, гоблины-шаманы | Король гоблинов |
| Пир Короля | Эльфы: мечники, следопыты, маги, рунические медведи | — |
| Редстоуновая лихорадка | Пауки трёх видов, скелеты четырёх видов, скелеты-прислужники | Рыцарь-скелет |
| Проклятье Дейви Джонса | Акулы, акулы-молоты, барракуды, рыба-меч, морские осы, гигантские кальмары, косатки, утопленники | Кракен |
| Марш нечисти | Лавовые клещи, адские грибы, огненные и тёмные бесы, потерянные души, адские гончие, прислужники ифрита | Король ифритов |
| Жизнь на кон | Синий сектор — орда: гоблины, эльфы, скелеты, пауки, нечисть, солнечные элементали, порождения Энда, скалковые твари, крысы или разбойники | Красный сектор — один-два босса мира |
| Рождество | — | Крампус |
С мобов события ничего не падает — награда выдаётся в конце."""))

# --- добыча
ART = json.load(open("artifacts.json"))
drops = []
for art, srcs in json.load(open("drops.json")).items():
    for s in srcs:
        for m in s["from"].split("|"):
            m = m.replace("mm:", "")
            if m in ("zombie", "zombieclimber", "witch"):
                continue
            drops.append((m, ART.get(art, art), s["chance"]))
MOBN = {"zombie": "Зомби (особый)", "zombieclimber": "Зомби-верхолаз", "bl_strangler_spider": "Паук-душитель", "bear_brown": "Бурый медведь",
        "bear_black": "Чёрный медведь", "mso_octopus": "Осьминог", "mso_octopus_2": "Осьминог", "gp2_goblin_club": "Гоблин с дубиной",
        "skeleton_elite": "Элитный скелет", "skeleton_melee": "Скелет-воин", "bl_hunter_spider": "Паук-охотник", "fire_imp": "Огненный бес",
        "blaze_king": "Король ифритов", "hellhound": "Адская гончая", "oni": "Они", "wendigo": "Вендиго", "end_strider": "Эндер-странник",
        "empowered_end_strider": "Усиленный эндер-странник", "sculk_sentinel": "Скалковый часовой", "duck_white": "Белая утка",
        "duck_mallard": "Кряква", "bl_poison_spider": "Ядовитый паук", "skeleton_archer": "Скелет-лучник", "nature_sprite": "Дух природы",
        "elven_mage": "Эльф-маг", "witch": "Ведьма (особая)", "lr_yeti": "Йети", "enderling": "Эндерлинг", "magma_wyrm": "Магмовый змей",
        "sol_sprite": "Солнечный дух", "solarmancer": "Солнечный чародей", "kraken": "Кракен", "ender_watchman": "Эндер-страж",
        "empowered_ender_watchman": "Усиленный эндер-страж", "nocsy_fpv3-leech": "Пиявка", "bear_polar": "Белый медведь",
        "nether_mushroom": "Адский гриб", "lady_of_the_forest": "Владычица леса", "elven_druid": "Эльф-друид",
        "gp2_goblin_warrior": "Гоблин-воин", "gp2_goblin_shaman": "Гоблин-шаман", "nocsy_fpv3-mosquito": "Комар"}
by = {}
for m, a, c in drops:
    n = MOBN.get(m.lower(), m)
    cs = (f"{c:g}").replace(".", ",")
    by.setdefault(n, []).append(f"{a} — {cs}%")
rows = ["| Моб | Артефакт и шанс |"]
for n in sorted(by):
    rows.append(f"| **{n}** | {'; '.join(dict.fromkeys(by[n]))} |")
S.append(("Добыча с мобов", "С особых мобов падают **артефакты-аксессуары**. Сет Чёрного рынка даёт шанс на двойную добычу.\n" + "\n".join(rows)))

# ------------------------------------------------------------------ руды
MAT = {"adamantite": "Адамантит", "aetherium": "Этериум", "amethyst": "Аметист", "ametrine": "Аметрин", "antimony": "Сурьма",
       "aquamarine": "Аквамарин", "black_opal": "Чёрный опал", "bromine": "Бром", "carnelian": "Сердолик", "chondrit": "Хондрит",
       "chromium": "Хром", "citrine": "Цитрин", "citrtine": "Цитрин", "thalassium": "Талассий", "cobalt": "Кобальт",
       "crimsonite": "Кримзонит", "dsto": "Титан", "monel": "Монель", "ekanite": "Эканит", "electrum": "Электрум",
       "gray_opal": "Серый опал", "gunpowder": "Порох", "heliodor": "Гелиодор", "indium": "Индий", "jade": "Нефрит",
       "lead": "Свинец", "lemonite": "Лемонит", "leucosapphire": "Лейкосапфир", "magnesium": "Магний", "neptunium": "Нептуний",
       "nickel": "Никель", "opalized_quartz": "Опаловый кварц", "osmium": "Осмий", "padparadscha": "Падпараджа",
       "pink_opal": "Розовый опал", "platinum": "Платина", "radium_dust": "Радиевая пыль", "radium": "Радий-226",
       "rare_sapphire": "Редкий сапфир", "rhodium": "Родий", "rose_gold": "Розовое золото", "sapphire": "Сапфир",
       "shadowite": "Теневит", "shadow": "Теневит", "sliver": "Серебро", "silver": "Серебро", "sunflare_gem": "Солнечный камень",
       "tanzanite": "Танзанит", "thorium": "Торий", "tin": "Олово", "topaz": "Топаз", "tungsten": "Вольфрам", "ussingite": "Уссингит",
       "white_crystal": "Кристалл", "white_opal": "Белый опал", "mysticrain_quartz": "Мистический кварц", "fire_opal": "Огненный опал",
       "fluorite_tier_1": "Флюорит I", "fluorite_tier_2": "Флюорит II", "fluorite_tier_3": "Флюорит III", "frost_opal": "Морозный опал",
       "luminous_gem": "Хлорофан", "peridot": "Перидот", "ruby": "Рубин", "ruby_pack": "Рубин", "titanium": "Титан",
       "titanium_quartz": "Титановый кварц", "volcagmium": "Вулкагмий"}
WHERE = {"over": "весь верхний мир", "ocean": "океаны", "cold": "холодные и снежные биомы", "dry": "пустыни и пустоши",
         "dry+volc": "пустыни, пустоши и вулканы", "volc+deep": "вулканы Terralith и глубинные пещеры",
         "amethyst": "аметистовые биомы, ×3", "end": "весь Энд", "shadowlands": "Теневые земли Энда, ещё ×2",
         "nether": "весь Незер", "crimson": "Пустоши Незера, багровый лес, Плачущая долина, Токсичная свалка",
         "quartz": "Кварцевые равнины, ещё ×2", "volcnether": "вулканические биомы Незера"}
ROCK = {"stone": "камень", "deepslate": "глубинный сланец", "nether": "незерак", "end": "эндерняк", "clay": "глина", "magma": "магма-блок"}
mats = {}
for l in open("ores_raw.txt"):
    oid, rock, y, vein, cnt, wh = l.strip().split("|")
    k = oid.rstrip("+")
    k = re.sub(r"^(deepslate_|deeplslate_|deepslatee_|nether_|end_stone_|clay_|magma_)", "", k)
    k = re.sub(r"(_ore_deepslate|_ore|_ore_bonus)$", "", k)
    if k == "deepslate_opalized_quartz": k = "opalized_quartz"
    m = MAT.get(k, k)
    mats.setdefault(m, []).append((rock, y.replace("…", "…"), int(vein), int(cnt), wh))
rows = ["| Материал | Порода | Высота Y | Жил на чанк × размер | Где |"]
for m in sorted(mats):
    order = {"stone": 0, "clay": 1, "deepslate": 2, "nether": 3, "magma": 4, "end": 5}
    for rock, y, vein, cnt, wh in sorted(mats[m], key=lambda r: (order[r[0]], r[4] != "over")):
        rows.append(f"| **{m}** | {ROCK[rock]} | {y} | {cnt} × {vein} | {WHERE[wh]} |")

O = []
O.append(("Где добывать руду", """Кроме обычных железа, золота и алмазов, в мире есть руды **ещё 75 материалов** — от олова и никеля до адамантита. Почти все они нужны в кузне.
### Как читать таблицу
- **Порода** — во что вкраплена руда. Каменные руды лежат выше Y 0, глубинносланцевые — ниже Y 8.
- **Высота Y** — в каком диапазоне искать. Свою высоту видно по [F3].
- **Жил на чанк × размер** — сколько жил игра пытается поставить в один чанк и сколько блоков в каждой. Чем больше оба числа, тем чаще руда.
- **Где** — биомы. «Весь верхний мир» — любые биомы обычного мира, включая пещерные.
> Новые руды есть только в **новых чанках**. Если вокруг дома всё изрыто, отправляйся в нехоженые земли.
### Опасные руды
- **Радий, радиевая пыль и торий** радиоактивны. Они лежат только в вулканических биомах Terralith (Вулканический кратер и пики, Кальдера, Базальтовые утёсы, Йеллоустоун, Пепельная саванна) и в глубинных пещерах (Глубокая тьма, Глубокие, Мантийные, Термальные и Заражённые пещеры). Перед работой надень свинцовую броню.
- **Пороховая руда** может рвануть. Ищи её в пустынях, пустошах и вулканах.
- **Бром** токсичен, он есть только в Энде.
- **Вулкагмий** — в вулканических биомах Незера: Базальтовые и Вулканические дельты, Пепельные пустоши, Адские дюны, Токсичная свалка. Одна из его руд прячется прямо в магма-блоках."""))
O.append(("Обычные руды", """| Руда | Высота Y | Где больше всего |
| Уголь | 0…320 | Y 95 и в горах |
| Медь | −16…112 | Y 48, особенно в карстовых пещерах |
| Железо | −64…320 | Y 16 и в горах выше Y 80 |
| Золото | −64…32 | Y −16; в пустошах ещё и до Y 256 |
| Редстоун | −64…16 | Y −59 и ниже |
| Лазурит | −64…64 | Y 0 |
| Алмаз | −64…16 | Y −59 и ниже |
| Изумруд | −16…320 | Только в горах |
| Незер-кварц и золото Незера | 10…117 | Весь Незер |
| Древние обломки | 8…119 | Незер, больше всего на Y 15 |
**Сталь** в мире не добывается: её крафтят из двух железных слитков и угля."""))
O.append(("Карта руд по материалам", "Все 138 рудных жил сервера, сгруппированные по материалу.\n" + "\n".join(rows)))

out = "# -*- coding: utf-8 -*-\n# Автоматически собрано gen_site.py из конфигов сервера. Не править руками.\n"
out += "MOBS_SECTIONS = " + repr(S) + "\n\nORE_SECTIONS = " + repr(O) + "\n"
open("bestiary_data.py", "w").write(out)
print(len(S), len(O), sum(len(b) for _, b in S), sum(len(b) for _, b in O))
