# -*- coding: utf-8 -*-
"""Русские названия биомов: ваниль, Terralith (t:), Incendium (incendium:), Nullscape."""
B = {
# --- ваниль, верхний мир
"plains": "Равнины", "sunflower_plains": "Подсолнуховые равнины", "meadow": "Луг",
"forest": "Лес", "flower_forest": "Цветочный лес", "birch_forest": "Березняк",
"old_growth_birch_forest": "Древний березняк", "dark_forest": "Тёмный лес", "pale_garden": "Бледный сад",
"taiga": "Тайга", "old_growth_pine_taiga": "Древняя сосновая тайга", "old_growth_spruce_taiga": "Древняя еловая тайга",
"snowy_taiga": "Заснеженная тайга", "snowy_plains": "Заснеженные равнины", "ice_spikes": "Ледяные шипы",
"grove": "Роща", "snowy_slopes": "Заснеженные склоны", "frozen_peaks": "Заледенелые пики",
"jagged_peaks": "Зубчатые пики", "stony_peaks": "Каменистые пики", "cherry_grove": "Вишнёвая роща",
"windswept_hills": "Ветреные холмы", "windswept_gravelly_hills": "Ветреные гравийные холмы",
"windswept_forest": "Ветреный лес", "savanna": "Саванна", "savanna_plateau": "Плато саванны",
"windswept_savanna": "Ветреная саванна", "desert": "Пустыня", "badlands": "Пустошь",
"eroded_badlands": "Выветренная пустошь", "wooded_badlands": "Лесистая пустошь",
"jungle": "Джунгли", "sparse_jungle": "Редкие джунгли", "bamboo_jungle": "Бамбуковые джунгли",
"swamp": "Болото", "mangrove_swamp": "Мангровое болото", "river": "Река", "frozen_river": "Замёрзшая река",
"beach": "Пляж", "snowy_beach": "Заснеженный пляж", "stony_shore": "Каменистый берег",
"mushroom_fields": "Грибные поля", "ocean": "Океан", "deep_ocean": "Глубокий океан",
"warm_ocean": "Тёплый океан", "lukewarm_ocean": "Умеренно-тёплый океан", "deep_lukewarm_ocean": "Глубокий умеренно-тёплый океан",
"cold_ocean": "Холодный океан", "deep_cold_ocean": "Глубокий холодный океан",
"frozen_ocean": "Замёрзший океан", "deep_frozen_ocean": "Глубокий замёрзший океан",
"lush_caves": "Пышные пещеры", "dripstone_caves": "Карстовые пещеры", "deep_dark": "Глубокая тьма",
# --- Незер
"nether_wastes": "Пустоши Незера", "crimson_forest": "Багровый лес", "warped_forest": "Искажённый лес",
"soul_sand_valley": "Долина песка душ", "basalt_deltas": "Базальтовые дельты",
"incendium:ash_barrens": "Пепельные пустоши", "incendium:quartz_flats": "Кварцевые равнины",
"incendium:inverted_forest": "Перевёрнутый лес", "incendium:weeping_valley": "Плачущая долина",
"incendium:withered_forest": "Иссохший лес", "incendium:volcanic_deltas": "Вулканические дельты",
"incendium:infernal_dunes": "Адские дюны", "incendium:toxic_heap": "Токсичная свалка",
# --- Terralith
"t:alpha_islands": "Альфа-острова", "t:alpha_islands_winter": "Зимние альфа-острова",
"t:alpine_grove": "Альпийская роща", "t:alpine_highlands": "Альпийское нагорье",
"t:amethyst_canyon": "Аметистовый каньон", "t:amethyst_rainforest": "Аметистовый тропический лес",
"t:ancient_sands": "Древние пески", "t:arid_highlands": "Засушливое нагорье", "t:ashen_savanna": "Пепельная саванна",
"t:basalt_cliffs": "Базальтовые утёсы", "t:birch_taiga": "Берёзовая тайга", "t:blooming_plateau": "Цветущее плато",
"t:blooming_valley": "Цветущая долина", "t:brushland": "Кустарниковая степь", "t:bryce_canyon": "Каньон Брайс",
"t:caldera": "Кальдера", "t:cloud_forest": "Облачный лес", "t:cold_shrubland": "Холодный кустарник",
"t:deep_warm_ocean": "Глубокий тёплый океан", "t:desert_canyon": "Пустынный каньон", "t:desert_oasis": "Оазис",
"t:desert_spires": "Пустынные шпили", "t:emerald_peaks": "Изумрудные пики", "t:forested_highlands": "Лесистое нагорье",
"t:fractured_savanna": "Расколотая саванна", "t:frozen_cliffs": "Ледяные утёсы", "t:glacial_chasm": "Ледниковое ущелье",
"t:granite_cliffs": "Гранитные утёсы", "t:gravel_beach": "Галечный пляж", "t:gravel_desert": "Гравийная пустыня",
"t:haze_mountain": "Туманная гора", "t:highlands": "Нагорье", "t:hot_shrubland": "Жаркий кустарник",
"t:ice_marsh": "Ледяная топь", "t:jungle_mountains": "Горные джунгли", "t:lavender_forest": "Лавандовый лес",
"t:lavender_valley": "Лавандовая долина", "t:lush_desert": "Цветущая пустыня", "t:lush_valley": "Зелёная долина",
"t:mirage_isles": "Острова миражей", "t:moonlight_grove": "Лунная роща", "t:moonlight_valley": "Лунная долина",
"t:orchid_swamp": "Орхидеевое болото", "t:painted_mountains": "Расписные горы", "t:red_oasis": "Красный оазис",
"t:rocky_jungle": "Скалистые джунгли", "t:rocky_mountains": "Скалистые горы", "t:rocky_shrubland": "Скалистый кустарник",
"t:sakura_grove": "Сакуровая роща", "t:sakura_valley": "Сакуровая долина", "t:sandstone_valley": "Песчаниковая долина",
"t:savanna_badlands": "Саванные пустоши", "t:savanna_slopes": "Склоны саванны", "t:scarlet_mountains": "Алые горы",
"t:shield": "Щит", "t:shield_clearing": "Поляна Щита", "t:shrubland": "Кустарник", "t:siberian_grove": "Сибирская роща",
"t:siberian_taiga": "Сибирская тайга", "t:skylands_spring": "Весенние небесные острова",
"t:skylands_summer": "Летние небесные острова", "t:skylands_autumn": "Осенние небесные острова",
"t:skylands_winter": "Зимние небесные острова", "t:snowy_badlands": "Заснеженные пустоши",
"t:snowy_cherry_grove": "Заснеженная вишнёвая роща", "t:snowy_maple_forest": "Заснеженный кленовый лес",
"t:snowy_shield": "Заснеженный Щит", "t:steppe": "Степь", "t:stony_spires": "Каменные шпили",
"t:temperate_highlands": "Умеренное нагорье", "t:tropical_jungle": "Тропические джунгли",
"t:valley_clearing": "Поляна в долине", "t:volcanic_crater": "Вулканический кратер", "t:volcanic_peaks": "Вулканические пики",
"t:warm_river": "Тёплая река", "t:warped_mesa": "Искажённая меса", "t:white_cliffs": "Белые утёсы", "t:white_mesa": "Белая меса",
"t:windswept_spires": "Ветреные шпили", "t:wintry_forest": "Зимний лес", "t:wintry_lowlands": "Зимняя низина",
"t:yellowstone": "Йеллоустоун", "t:yosemite_cliffs": "Утёсы Йосемити", "t:yosemite_lowlands": "Низины Йосемити",
"t:cave/andesite_caves": "Андезитовые пещеры", "t:cave/deep_caves": "Глубокие пещеры", "t:cave/diorite_caves": "Диоритовые пещеры",
"t:cave/frostfire_caves": "Пещеры морозного огня", "t:cave/fungal_caves": "Грибные пещеры", "t:cave/granite_caves": "Гранитные пещеры",
"t:cave/infested_caves": "Заражённые пещеры", "t:cave/mantle_caves": "Мантийные пещеры", "t:cave/thermal_caves": "Термальные пещеры",
"t:cave/tuff_caves": "Туфовые пещеры", "t:cave/underground_jungle": "Подземные джунгли",
}


def name(b):
    k = b.strip().replace("minecraft:", "").replace("terralith:", "t:")
    k2 = k.lower() if not k.startswith("t:") and not k.startswith("incendium:") else k
    return B.get(k2, B.get(k, k))


def names(lst):
    out, seen = [], set()
    for b in lst:
        n = name(b)
        if n not in seen:
            seen.add(n); out.append(n)
    return ", ".join(out)
