# Бестиарий и карта руд

`bestiary_data.py` в корне сайта собирается отсюда: `python gen_site.py`, затем скопировать `bestiary_data.py` в корень и запустить `python build.py`.

Входные файлы — выгрузка с сервера на 23.11.2026:
- `rules.json` — правила RandomSpawns MythicMobs (кроме морских);
- `Waterlogged-RandomSpawns-Biomes.yml` — морские правила;
- `wildlife_biomes.txt` — биомы диких животных;
- `ores_raw.txt` — рудные жилы датапака momg_ores (из tools/momg/report.md на сервере);
- `drops.json`, `artifacts.json` — артефакты с мобов (plugins/MiddleLandsRPG/drops.yml).

После изменения спавнов или руд на сервере обновите эти файлы и пересоберите.
