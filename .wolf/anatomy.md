# anatomy.md

> Auto-maintained by OpenWolf. Last scanned: 2026-10-14T05:36:17.430Z
> Files: 57 tracked | Anatomy hits: 0 | Misses: 0

> Project structure index. Auto-maintained by OpenWolf hooks and daemon.
> Run `openwolf scan` to generate, or wait for the first Claude Code session.
> Status: Pending initial scan

## ./

- `_headers` (~51 tok)
- `.gitignore` — Git ignore rules (~119 tok)
- `AGENTS.md` — OpenWolf (~611 tok)
- `article.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~559 tok)
- `CLAUDE.md` — OpenWolf (~99 tok)
- `config.py` — Settings: parse_target_chat_id, load_pricing_matrix, load_proxies (~772 tok)
- `docker-compose.yml` — Docker Compose services (~172 tok)
- `Dockerfile` — Docker container definition (~127 tok)
- `GEMINI.md` — OpenWolf (~75 tok)
- `index.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~57453 tok)
- `main.py` — acquire_single_instance_lock, main (~2156 tok)
- `pricing_matrix_default.json` (~2900 tok)
- `pricing_matrix.json` (~1 tok)
- `proxies.txt.example` — Добавьте сюда ваши HTTP / SOCKS5 прокси (по одному на строку): (~49 tok)
- `README.md` — Project documentation (~1470 tok)
- `requirements.txt` — Python dependencies (~55 tok)
- `search_streams.json` (~742 tok)

## .github/workflows/

- `deploy-pages.yml` — CI: Deploy Telegram Mini App to GitHub Pages (~213 tok)

## bot/

- `__init__.py` (~85 tok)
- `bot.py` — register_worker_query_listener, broadcast_worker_query, cleanup_user_message, send_or_replace_functional_message + 1 more (~27866 tok)
- `dispatcher.py` — ItemDispatcher: format_lot_message, start (~4868 tok)
- `keyboards.py` — get_item_keyboard, get_favorites_keyboard, get_main_menu_keyboard, get_reply_keyboard + 6 more (~3524 tok)

## core/

- `__init__.py` (~92 tok)
- `deduplicator.py` — RedisDeduplicator: extract_image_key, normalize_text_fingerprint, normalize_location, connect + 3 more (~4262 tok)
- `excel_manager.py` — ExcelPricingManager: export_matrix_to_bytes, parse_excel_to_matrix, import_matrix_from_bytes (~2261 tok)
- `favorites.py` — URL configuration (~1506 tok)
- `link_stream.py` — SearchStream: to_dict, from_dict, extract_prices_from_query, parse_search_url (~6584 tok)
- `margin_filter.py` — MarginFilter: reload_matrix, save_matrix, is_series_enabled, toggle_series + 2 more (~2132 tok)
- `models.py` — Pydantic: RawItem (51 fields) (~853 tok)
- `parser.py` — Регулярные выражения для фильтрации мусора, копий и брака (Blacklist) (~6922 tok)
- `regions.py` (~7811 tok)
- `user_profile.py` — Pydantic: UserConditionRules (34 fields) (~3527 tok)

## docs/

- `_headers` (~51 tok)
- `article.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~559 tok)
- `index.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~57453 tok)
- `pricing_matrix_default.json` (~2900 tok)

## parsers/

- `__init__.py` (~81 tok)
- `avito.py` — AvitoWorker: add_custom_query, set_location, fetch_fresh_items (~3403 tok)
- `base.py` — BaseWorker: fetch_fresh_items, is_fresh, run, stop (~1273 tok)
- `network.py` — ProxyPool: get_proxy, mark_bad, mark_good, total + 4 more (~1990 tok)
- `youla.py` — YoulaWorker: add_custom_query, set_location (~4880 tok)

## tests/

- `test_custom_categories.py` — Tests: custom_category_profile, broadcast_worker_query, parser_with_custom_category_model (~787 tok)
- `test_deduplicator.py` — Tests: in_memory_deduplication, price_drop_detection, semantic_crossplatform_duplicate, semantic_photo_duplicate + 2 more (~2321 tok)
- `test_excel_manager.py` — Tests: export_and_read_back, import_modified_excel, import_invalid_data_handles_cleanly (~994 tok)
- `test_favorites.py` — Tests: add_and_get_favorite, remove_favorite, clear_favorites, lot_caching (~860 tok)
- `test_formatting.py` — Tests: format_fresh_lot, format_price_drop, format_battery_penalty_notice (~794 tok)
- `test_link_streams.py` — Tests: parse_search_url_avito, parse_search_url_avito_f_param_pricing, parse_search_url_ekb_and_categories, parse_search_url_youla + 4 more (~3343 tok)
- `test_margin_filter.py` — Tests: profitable_item, unprofitable_item, battery_penalty, disabled_model_configuration + 1 more (~1740 tok)
- `test_modern_bot_features.py` — Tests: expandable_blockquote_in_formatting, item_keyboard_with_bargain_and_fav, custom_model_extraction, macbook_multi_spec_parsing + 9 more (~9333 tok)
- `test_regex_parser.py` — Tests: model_extraction, storage_extraction, battery_extraction, blacklist_rejection + 3 more (~1709 tok)
- `test_regions.py` — Tests: default_region, set_region_by_key, set_region_by_alias, set_region_by_russian_name + 8 more (~1549 tok)
- `test_user_profile.py` — Tests: evaluate_item_clean_deal, evaluate_item_worn_battery_applies_discount, evaluate_item_defect_rejected_when_not_allowed, evaluate_item_defect_... (~3293 tok)

## webapp/

- `_headers` (~51 tok)
- `article.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~559 tok)
- `index.html` — ⚡️ БРЕДЛИ ПЕРЕКУПЕР (~57453 tok)
- `pricing_matrix_default.json` (~2900 tok)
- `pricing_matrix.json` (~1 tok)
