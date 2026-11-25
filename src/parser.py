"""
Модуль 2: Веб-парсер (Компонент сбора данных).

Класс ForumParser извлекает информацию со страниц форумов / структурированных
веб-ресурсов (на примере https://quotes.toscrape.com/) и сохраняет в БД.
"""

import sqlite3
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


# User-Agent, чтобы не блокировали запросы
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
}


class ForumParser:
    """
    Парсер страниц форума.

    По умолчанию настроен под структуру https://quotes.toscrape.com/:
    каждый пост — <div class="quote" data-...>
        <span class="text">...</span>
        <small class="author">...</small>
        <a href="/author/Name">...</a>
    ID берётся из ссылки на автора / или порядкового номера.
    """

    def __init__(
        self,
        base_url: str = "https://quotes.toscrape.com/",
        headers: Optional[dict] = None,
        timeout: int = 10,
    ) -> None:
        if not isinstance(base_url, str) or not base_url:
            raise ValueError("base_url должен быть непустой строкой")

        self.base_url = base_url
        self.headers = headers or DEFAULT_HEADERS
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    # ------------------------------------------------------------------ #
    #  Загрузка HTML
    # ------------------------------------------------------------------ #

    def fetch_html(self, url: str) -> str:
        """
        Скачивает HTML-код страницы.

        :raises requests.RequestException: при сетевой ошибке / плохом статусе.
        """
        if not isinstance(url, str) or not url:
            raise ValueError("url должен быть непустой строкой")

        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        # У quotes.toscrape.com UTF-8; в общем случае requests угадает
        response.encoding = response.encoding or "utf-8"
        return response.text

    # ------------------------------------------------------------------ #
    #  Разбор HTML
    # ------------------------------------------------------------------ #

    def parse_html(self, html: str, url: Optional[str] = None) -> list[dict]:
        """
        Разбирает HTML-код и возвращает список словарей:
            [{"id": int, "name": str, "message": str}, ...]

        :param html: HTML-код страницы (строка).
        :param url:  базовый URL для разрешения относительных ссылок.
        """
        if not isinstance(html, str):
            raise ValueError("html должен быть строкой")

        soup = BeautifulSoup(html, "lxml")
        results: list[dict] = []

        # Каждый пост на quotes.toscrape.com — <div class="quote">
        # В общем случае можно подстроить селекторы под другой форум.
        posts = soup.select("div.quote")

        for idx, post in enumerate(posts, start=1):
            text_tag = post.select_one("span.text")
            author_tag = post.select_one("small.author")
            link_tag = post.select_one("a[href*='/author/']")

            if not text_tag or not author_tag:
                # Пропускаем «битые» посты
                continue

            name = author_tag.get_text(strip=True)

            # Сохраняем внутреннюю HTML-разметку сообщения
            message = text_tag.decode_contents().strip()

            # ID: пытаемся вытащить из ссылки на автора,
            # иначе — порядковый номер поста на странице.
            comment_id = self._extract_id(link_tag, fallback=idx)

            results.append(
                {
                    "id": comment_id,
                    "name": name,
                    "message": message,
                }
            )

        return results

    @staticmethod
    def _extract_id(link_tag, fallback: int) -> int:
        """
        Извлекает ID из ссылки вида /author/Albert-Einstein,
        либо возвращает fallback.
        """
        if link_tag is None:
            return fallback

        href = link_tag.get("href", "")
        # Берём последний сегмент пути и заменяем нецифровые символы
        slug = href.rstrip("/").split("/")[-1]
        # Простейший детерминированный хеш из slug → int
        # (чтобы ID был стабильным и уникальным для каждого автора)
        if not slug:
            return fallback
        # Сумма ord символов — стабильный, но не идеально распределённый хеш
        return sum(ord(ch) for ch in slug)

    # ------------------------------------------------------------------ #
    #  Парсинг страницы по URL (fetch + parse)
    # ------------------------------------------------------------------ #

    def parse_page(self, url: str) -> list[dict]:
        """
        Скачивает страницу по URL и парсит её.
        """
        html = self.fetch_html(url)
        return self.parse_html(html, url=url)

    # ------------------------------------------------------------------ #
    #  Сохранение в БД
    # ------------------------------------------------------------------ #

    def save_to_db(self, parsed_data: list[dict], repository) -> int:
        """
        Сохраняет распарсенные записи в БД через DatabaseRepository.

        Дубликаты по id пропускаются (не считаются ошибкой).

        :return: количество успешно добавленных записей.
        """
        if not isinstance(parsed_data, list):
            raise ValueError("parsed_data должен быть списком словарей")

        added = 0
        for item in parsed_data:
            try:
                comment_id = int(item["id"])
                name = item["name"]
                message = item["message"]
                repository.add(comment_id, name, message)
                added += 1
            except sqlite3.IntegrityError:
                # Дубликат — пропускаем
                continue
            except (KeyError, ValueError, TypeError) as exc:
                print(f"[save_to_db] Пропущена запись {item!r}: {exc}")
                continue
        return added

    def close(self) -> None:
        """Закрывает сессию requests."""
        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()