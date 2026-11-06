"""居所助手数据接口（Supabase REST，httpx 实现）。

站点 https://jusuo.playmmo.cn 是纯前端 SPA，数据放在它自己的 Supabase 后端
（db.playmmo.cn）里，前端内置了一个公开只读的 anon key。本模块直接打 REST 接口，
不渲染网页，因此响应快、无需浏览器。
"""

from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://db.playmmo.cn"
DEFAULT_ANON_KEY = (
    "eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9."
    "eyJyb2xlIjogImFub24iLCJpc3MiOiAic3VwYWJhc2UtZGVtbyIsImlhdCI6IDE3ODcxNjIzNjMsImV4cCI6IDIxMDI1MjIzNjN9."
    "Qe7GD4i5-auaMmvL73gbasJLdjo8-tPUHWQ2KmztXek"
)


class JusuoAPIError(RuntimeError):
    """接口调用失败。"""


class JusuoAPI:
    """居所助手只读数据客户端（带缓存与重试）。"""

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        anon_key: str = DEFAULT_ANON_KEY,
        *,
        timeout: float = 15.0,
        cache_ttl: int = 90,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.anon_key = anon_key or DEFAULT_ANON_KEY
        self.timeout = timeout
        self.cache_ttl = max(0, cache_ttl)
        self._cache: dict[str, tuple[float, Any]] = {}
        self.headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Accept": "application/json",
        }

    # ---------------- 基础设施 ----------------

    async def close(self) -> None:
        """兼容性空实现：本客户端按请求建连，无需常驻会话。"""

    def _new_client(self) -> httpx.AsyncClient:
        """建连客户端。

        默认读取系统代理设置；某些环境（例如 NO_PROXY 里写了 `[::1]`）会让 httpx
        解析代理配置时报 InvalidURL，此时退回不读环境变量的模式，避免整条查询失败。
        """
        kwargs = {
            "timeout": self.timeout,
            "headers": self.headers,
            "follow_redirects": True,
        }
        try:
            return httpx.AsyncClient(trust_env=True, **kwargs)
        except Exception:  # noqa: BLE001
            return httpx.AsyncClient(trust_env=False, **kwargs)

    async def _request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        retries: int = 2,
    ) -> Any:
        url = f"{self.base_url}{path}"
        last_error: Exception | None = None
        for attempt in range(retries + 1):
            try:
                async with self._new_client() as client:
                    resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    raise JusuoAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
                text = resp.text
                if not text.strip():
                    return []
                return resp.json()
            except (httpx.HTTPError, ValueError, JusuoAPIError) as exc:
                last_error = exc
                if attempt < retries:
                    await asyncio.sleep(0.6 * (attempt + 1))
                    continue
        raise JusuoAPIError(f"请求失败: {last_error}")

    async def _table(self, table: str, params: dict[str, Any]) -> list[dict]:
        data = await self._request(f"/rest/v1/{table}", params)
        if isinstance(data, dict):
            return [data]
        return list(data or [])

    def _cached(self, key: str) -> Any | None:
        item = self._cache.get(key)
        if not item or not self.cache_ttl:
            return None
        ts, value = item
        return value if time.time() - ts < self.cache_ttl else None

    def _store(self, key: str, value: Any) -> Any:
        self._cache[key] = (time.time(), value)
        return value

    # ---------------- 基础数据 ----------------

    async def unit_prices(self) -> dict[str, dict[str, float]]:
        """返回 {"crop": {名称: 单价}, "ranch": {名称: 单价}}。"""
        cached = self._cached("unit_prices")
        if cached is not None:
            return cached
        rows = await self._table(
            "unit_prices",
            {"select": "name,category,unit_price", "order": "category.asc,name.asc"},
        )
        result: dict[str, dict[str, float]] = {"crop": {}, "ranch": {}}
        for row in rows:
            category = row.get("category") or "crop"
            result.setdefault(category, {})[row.get("name", "")] = float(
                row.get("unit_price") or 0
            )
        return self._store("unit_prices", result)

    async def ranch_presets(self) -> dict[str, str]:
        """牧场产物预设 id -> 名称。"""
        cached = self._cached("ranch_presets")
        if cached is not None:
            return cached
        rows = await self._table("ranch_product_presets", {"select": "id,name", "limit": 500})
        return self._store("ranch_presets", {r["id"]: r["name"] for r in rows})

    # ---------------- 业务数据 ----------------

    async def residence_entries(self, limit: int = 300) -> list[dict]:
        """菜地作物高倍收购条目（仅在售）。"""
        return await self._table(
            "residence_entries",
            {
                "select": (
                    "id,uid,crop_name,quantity,price_multiplier,merchant_name,"
                    "residence_level,expires_at,created_at,like_count,"
                    "is_limit_reached,guild_maxed,sale_price"
                ),
                "expires_at": "gt.now()",
                "is_reported": "eq.false",
                "order": "price_multiplier.desc,expires_at.desc",
                "limit": limit,
            },
        )

    async def ranch_entries(self, limit: int = 300) -> list[dict]:
        """牧场动物产物高倍收购条目（仅在售）。"""
        return await self._table(
            "ranch_entries",
            {
                "select": (
                    "id,uid,product_preset_id,quantity,price_multiplier,merchant_name,"
                    "animal_stall_level,expires_at,created_at,like_count,"
                    "is_limit_reached,guild_maxed,sale_price"
                ),
                "expires_at": "gt.now()",
                "is_reported": "eq.false",
                "order": "price_multiplier.desc,expires_at.desc",
                "limit": limit,
            },
        )

    async def market_matrix(
        self, source: str = "crop", metric: str = "price", hours: int = 24
    ) -> dict:
        """行情矩阵（站点自带的 edge function）。"""
        return await self._request(
            "/functions/v1/market-matrix",
            {"source": source, "metric": metric, "hours": hours, "_t": int(time.time() * 1000)},
        )

    async def ranch_entries_with_names(self, limit: int = 300) -> list[dict]:
        """牧场条目 + 已解析的产物名称（写进 product_name 字段）。"""
        entries, presets = await asyncio.gather(
            self.ranch_entries(limit=limit), self.ranch_presets()
        )
        for entry in entries:
            entry["product_name"] = presets.get(entry.get("product_preset_id"), "未知产物")
        return entries
