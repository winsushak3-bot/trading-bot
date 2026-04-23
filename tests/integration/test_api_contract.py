# tests/integration/test_api_contract.py
"""
Контрактные тесты между фронтендом (webapp, admin) и backend'ом (FastAPI).

Задача: на этапе CI отлавливать ситуации, когда TypeScript-клиент вызывает
несуществующий URL (будет 404 в рантайме).

Как работает:
  1. Парсим `webapp/src/api/client.ts` и `admin/src/api/client.ts` регуляркой,
     собираем все `apiClient.<method>('<url>'...)` вызовы.
  2. Нормализуем URL-шаблоны: `/charts/crypto/ohlcv/${symbol}` → `/charts/crypto/ohlcv/{}`.
  3. Берём список всех роутов FastAPI `app` и тоже нормализуем путь-параметры
     (`/charts/crypto/ohlcv/{symbol:path}` → `/charts/crypto/ohlcv/{}`).
  4. Для каждого клиентского URL проверяем, что есть соответствующий роут
     с тем же HTTP-методом.

Если клиент вызывает URL, которого нет в backend — тест краснеет и показывает
точное место в TS-клиенте.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from backend.main import app


# ── Paths ────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
_WEBAPP_CLIENT = _REPO_ROOT / "webapp" / "src" / "api" / "client.ts"
_ADMIN_CLIENT = _REPO_ROOT / "admin" / "src" / "api" / "client.ts"


# ── URL нормализация ──────────────────────────────────────────
#
# FastAPI-путь `/charts/crypto/ohlcv/{symbol:path}` и TS-вызов
# `/charts/crypto/ohlcv/${symbol}` после нормализации оба превращаются в
# `/charts/crypto/ohlcv/{}`. Это позволяет сравнивать их напрямую.

_TS_INTERPOLATION_RE = re.compile(r"\$\{[^}]+\}")
_FASTAPI_PARAM_RE = re.compile(r"\{[^}]+\}")


def _normalize_url(url: str) -> str:
    """Приводит URL к канонической форме для сравнения клиент↔сервер.

    Примеры:
      /charts/crypto/ohlcv/${symbol}          → /charts/crypto/ohlcv/{}
      /charts/crypto/ohlcv/{symbol:path}  → /charts/crypto/ohlcv/{}
      /charts/crypto/ohlcv                      → /charts/crypto/ohlcv
    """
    # Убираем query-string (?limit=50) — роуты FastAPI их игнорируют.
    url = url.split("?", 1)[0]
    # TS `${var}` → {}
    url = _TS_INTERPOLATION_RE.sub("{}", url)
    # FastAPI {name} и {name:type} → {}
    url = _FASTAPI_PARAM_RE.sub("{}", url)
    # `/api/...` префикс у клиентов уже отрезан через baseURL='/api',
    # но в FastAPI роуты регистрируются с `/api/...`. Приводим к одному виду.
    if not url.startswith("/api/"):
        url = "/api" + (url if url.startswith("/") else f"/{url}")
    # Убираем trailing slash для унификации.
    if url != "/" and url.endswith("/"):
        url = url[:-1]
    return url


# ── Парсер TS-клиента ─────────────────────────────────────────

# Ищем вызовы вида:
#   apiClient.get('/some/path'
#   apiClient.post(`/some/${var}`
#   apiClient.put("/path", ...)
# Поддерживаем одинарные, двойные, и обратные кавычки.
_API_CALL_RE = re.compile(
    r"""apiClient\.(?P<method>get|post|put|patch|delete)\s*\(
        \s*
        (?P<quote>['"`])
        (?P<url>[^'"`]+)
        (?P=quote)
    """,
    re.VERBOSE,
)


def _extract_client_calls(ts_file: Path) -> list[tuple[str, str, int]]:
    """Возвращает список (HTTP_METHOD, URL, LINE_NO) из TS-клиента."""
    if not ts_file.exists():
        return []
    text = ts_file.read_text(encoding="utf-8")
    calls: list[tuple[str, str, int]] = []
    for match in _API_CALL_RE.finditer(text):
        line_no = text.count("\n", 0, match.start()) + 1
        calls.append((match.group("method").upper(), match.group("url"), line_no))
    return calls


# ── Сбор FastAPI-роутов ───────────────────────────────────────

def _collect_fastapi_routes() -> set[tuple[str, str]]:
    """Возвращает {(METHOD, NORMALIZED_PATH), ...} для всех роутов backend.main.app."""
    result: set[tuple[str, str]] = set()
    for route in app.routes:
        # Только HTTP-роуты с атрибутами `methods` и `path`.
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", None)
        if not path or not methods:
            continue
        normalized = _normalize_url(path)
        for m in methods:
            if m in {"HEAD", "OPTIONS"}:
                continue
            result.add((m, normalized))
    return result


# ── Тесты ─────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def fastapi_routes() -> set[tuple[str, str]]:
    return _collect_fastapi_routes()


def _assert_calls_match(
    client_file: Path,
    fastapi_routes: set[tuple[str, str]],
    client_label: str,
) -> None:
    """Проверяет, что все вызовы в client_file имеют соответствующий роут в FastAPI."""
    calls = _extract_client_calls(client_file)
    assert calls, f"Не удалось распарсить {client_label}: нет вызовов apiClient.*"

    missing: list[str] = []
    for method, raw_url, line in calls:
        normalized = _normalize_url(raw_url)
        if (method, normalized) not in fastapi_routes:
            # `/api/api_not_found` — это catch-all 404-хендлер в backend.main,
            # он не должен участвовать в проверке (соответствует любому неизвестному /api/*).
            missing.append(
                f"  {client_label}:{line}  {method} {raw_url}  → нормализовано: {normalized}"
            )

    if missing:
        # Формируем информативное сообщение с полным списком несовпадений.
        msg = (
            f"\nКлиент вызывает URL, которого НЕТ в FastAPI (будет 404 в рантайме):\n\n"
            + "\n".join(missing)
            + "\n\nРеально зарегистрированные /api/charts роуты:\n"
            + "\n".join(
                f"  {m} {p}"
                for m, p in sorted(fastapi_routes)
                if "/charts" in p
            )
        )
        pytest.fail(msg)


def test_webapp_api_calls_match_backend_routes(fastapi_routes) -> None:
    """Каждый вызов в webapp/src/api/client.ts должен иметь соответствующий
    endpoint в FastAPI. Ловит ситуации, когда TS добавили, а backend забыли."""
    _assert_calls_match(_WEBAPP_CLIENT, fastapi_routes, "webapp/src/api/client.ts")


def test_admin_api_calls_match_backend_routes(fastapi_routes) -> None:
    """Каждый вызов в admin/src/api/client.ts должен иметь соответствующий
    endpoint в FastAPI."""
    _assert_calls_match(_ADMIN_CLIENT, fastapi_routes, "admin/src/api/client.ts")
