from __future__ import annotations

import asyncio
import logging
import signal
import sys

from config import settings
from core.models import RawItem
from core.deduplicator import RedisDeduplicator
from core.margin_filter import MarginFilter
from parsers.network import StealthHttpClient, ProxyPool
from parsers.avito import AvitoWorker
from parsers.youla import YoulaWorker
from bot.bot import create_bot, create_bot_dispatcher
from bot.dispatcher import ItemDispatcher

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("MAIN")


async def main() -> None:
    logger.info("==================================================")
    logger.info("   ⚡️ APPLE RESELL BOT (AVITO & YOULA RADAR) ⚡️   ")
    logger.info("==================================================")

    # 1. Пул прокси и защищенный HTTP клиент
    proxy_pool = ProxyPool()
    logger.info("Загружено прокси: %d шт.", proxy_pool.total)
    http_client = StealthHttpClient(proxy_pool=proxy_pool)

    # 2. Redis конвейер дедупликации
    deduplicator = RedisDeduplicator()
    await deduplicator.connect()

    # 3. Асинхронная очередь сырых лотов
    queue: asyncio.Queue[RawItem] = asyncio.Queue(maxsize=1000)

    # 4. Фильтр маржинальности (матрица пороговых цен)
    margin_filter = MarginFilter()

    # 5. Telegram Bot & Диспетчер мгновенных оповещений
    bot = create_bot()
    bot_dp = create_bot_dispatcher(margin_filter=margin_filter)
    dispatcher = ItemDispatcher(
        bot=bot,
        queue=queue,
        margin_filter=margin_filter,
    )

    # 6. Независимые параллельные воркеры мониторинга
    avito_worker = AvitoWorker(
        queue=queue,
        deduplicator=deduplicator,
        http_client=http_client,
    )
    youla_worker = YoulaWorker(
        queue=queue,
        deduplicator=deduplicator,
        http_client=http_client,
    )

    # Собираем фоновые задачи
    tasks = [
        asyncio.create_task(dispatcher.start(), name="ItemDispatcher"),
        asyncio.create_task(avito_worker.run(), name="AvitoWorker"),
        asyncio.create_task(youla_worker.run(), name="YoulaWorker"),
    ]

    # Если токен настроен, запускаем polling команд бота (/start, /status)
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "YOUR_BOT_TOKEN_HERE":
        tasks.append(
            asyncio.create_task(
                bot_dp.start_polling(bot, handle_signals=False),
                name="BotPolling",
            )
        )
    else:
        logger.warning(
            "ВНИМАНИЕ: BOT_TOKEN не заполнен в .env! Запуск в режиме имитации/тестирования."
        )

    # Graceful Shutdown
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def _shutdown_handler(sig_name: str) -> None:
        logger.info("Получен сигнал %s. Завершение работы...", sig_name)
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _shutdown_handler, sig.name)
        except NotImplementedError:
            # На Windows add_signal_handler не поддерживается
            pass

    try:
        await stop_event.wait()
    finally:
        logger.info("Остановка всех компонентов...")
        avito_worker.stop()
        youla_worker.stop()
        dispatcher.stop()

        for t in tasks:
            t.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)
        await http_client.close()
        await deduplicator.close()
        await bot.session.close()
        logger.info("Все соединения закрыты. Сервис остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
