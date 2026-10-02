from __future__ import annotations

import logging
import random
from typing import Optional, Any
from curl_cffi.requests import AsyncSession
from config import settings

logger = logging.getLogger(__name__)


class ProxyPool:
    """Пул HTTP/SOCKS5 прокси с ротацией и отслеживанием ошибок."""

    def __init__(self, proxies: Optional[list[str]] = None):
        self._proxies: list[str] = proxies or settings.load_proxies()
        self._index: int = 0
        self._failed_counts: dict[str, int] = {p: 0 for p in self._proxies}

    def get_proxy(self) -> Optional[str]:
        if not self._proxies:
            return None
        proxy = self._proxies[self._index % len(self._proxies)]
        self._index += 1
        return proxy

    def mark_bad(self, proxy: str) -> None:
        if proxy in self._failed_counts:
            self._failed_counts[proxy] += 1
            if self._failed_counts[proxy] >= 3:
                logger.warning("Прокси %s временно удален из пула (превышен лимит ошибок)", proxy)
                if proxy in self._proxies:
                    self._proxies.remove(proxy)

    def mark_good(self, proxy: str) -> None:
        if proxy in self._failed_counts:
            self._failed_counts[proxy] = 0

    @property
    def total(self) -> int:
        return len(self._proxies)


class StealthHttpClient:
    """
    Высокопроизводительный асинхронный HTTP-клиент на базе curl_cffi.
    Обходит TLS/JA3/JA4 отпечатки Cloudflare, Akamai и антифрод Авито/Юлы
    за счет нативной эмуляции браузерных handshake (Chrome, Safari).
    """

    def __init__(self, proxy_pool: Optional[ProxyPool] = None, impersonate: str = "chrome124"):
        self.proxy_pool = proxy_pool or ProxyPool()
        self.impersonate = impersonate
        self._session: Optional[AsyncSession] = None

    async def get_session(self) -> AsyncSession:
        if self._session is None or getattr(self._session, "_closed", False):
            self._session = AsyncSession(
                impersonate=self.impersonate,
                timeout=10.0,
                verify=True,
            )
        return self._session

    async def close(self) -> None:
        if self._session and not getattr(self._session, "_closed", False):
            await self._session.close()
            self._session = None

    async def get(
        self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        retries: int = 2,
    ) -> Optional[dict | str]:
        """
        Выполняет GET-запрос с автоматической ротацией прокси и спуфингом заголовков.
        Возвращает распарсенный JSON словарь либо текст.
        """
        session = await self.get_session()

        for attempt in range(1, retries + 1):
            proxy = self.proxy_pool.get_proxy()
            proxies_dict = {"http": proxy, "https": proxy} if proxy else None

            default_headers = {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                ),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            }
            if headers:
                default_headers.update(headers)

            try:
                response = await session.get(
                    url=url,
                    headers=default_headers,
                    params=params,
                    proxies=proxies_dict,
                    timeout=8.0,
                )

                if response.status_code == 200:
                    if proxy:
                        self.proxy_pool.mark_good(proxy)
                    try:
                        return response.json()
                    except Exception:
                        return response.text

                elif response.status_code in (403, 429):
                    logger.warning(
                        "Rate-limit / Защита на URL %s (HTTP %s, прокси: %s)",
                        url,
                        response.status_code,
                        proxy or "Локальный IP",
                    )
                    if proxy:
                        self.proxy_pool.mark_bad(proxy)
                    else:
                        # При работе без прокси делаем паузу для снятия временного лимита
                        logger.info("Пауза 15 сек для снятия временного лимита IP сервера...")
                        await asyncio.sleep(15.0)
                else:
                    logger.debug("Статус %s при запросе %s", response.status_code, url)

            except Exception as e:
                logger.debug("Ошибка запроса (попытка %d/%d) %s: %s", attempt, retries, url, e)
                if proxy:
                    self.proxy_pool.mark_bad(proxy)

        return None

    async def post(
        self,
        url: str,
        json_data: dict[str, Any],
        headers: Optional[dict[str, str]] = None,
        retries: int = 2,
    ) -> Optional[dict | str]:
        """POST-запрос (для GraphQL запросов Юлы)."""
        session = await self.get_session()

        for attempt in range(1, retries + 1):
            proxy = self.proxy_pool.get_proxy()
            proxies_dict = {"http": proxy, "https": proxy} if proxy else None

            default_headers = {
                "User-Agent": (
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4_1 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1"
                ),
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Accept-Language": "ru-RU,ru;q=0.9",
            }
            if headers:
                default_headers.update(headers)

            try:
                response = await session.post(
                    url=url,
                    json=json_data,
                    headers=default_headers,
                    proxies=proxies_dict,
                    timeout=8.0,
                )

                if response.status_code == 200:
                    if proxy:
                        self.proxy_pool.mark_good(proxy)
                    try:
                        return response.json()
                    except Exception:
                        return response.text
                elif response.status_code in (403, 429):
                    logger.warning("HTTP %s при POST %s (прокси %s)", response.status_code, url, proxy)
                    if proxy:
                        self.proxy_pool.mark_bad(proxy)
            except Exception as e:
                logger.debug("POST сбой: %s", e)
                if proxy:
                    self.proxy_pool.mark_bad(proxy)

        return None
