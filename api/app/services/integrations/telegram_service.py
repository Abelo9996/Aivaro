"""Telegram Integration Service — messaging, photos, webhooks."""
import httpx
from typing import Optional, Any


class TelegramService:
    """Service for Telegram Bot API."""

    def __init__(self, bot_token: str):
        self.bot_token = bot_token
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        self._client = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        client = await self._get_client()
        resp = await client.request(method, f"{self.base_url}/{endpoint}", **kwargs)
        resp.raise_for_status()
        data = resp.json()
        if not data.get("ok"):
            raise Exception(data.get("description", "Telegram API error"))
        return data.get("result")

    async def get_me(self) -> dict:
        return await self._request("GET", "getMe")

    async def send_message(self, chat_id: str, text: str, parse_mode: str = None,
                           disable_notification: bool = False) -> dict:
        payload = {"chat_id": chat_id, "text": text}
        if parse_mode: payload["parse_mode"] = parse_mode
        if disable_notification: payload["disable_notification"] = True
        return await self._request("POST", "sendMessage", json=payload)

    async def send_photo(self, chat_id: str, photo: str, caption: str = "") -> dict:
        payload = {"chat_id": chat_id, "photo": photo}
        if caption: payload["caption"] = caption
        return await self._request("POST", "sendPhoto", json=payload)

    async def send_document(self, chat_id: str, document: str, caption: str = "") -> dict:
        payload = {"chat_id": chat_id, "document": document}
        if caption: payload["caption"] = caption
        return await self._request("POST", "sendDocument", json=payload)

    async def get_updates(self, offset: int = None, limit: int = 100) -> list:
        params = {"limit": limit}
        if offset is not None: params["offset"] = offset
        return await self._request("GET", "getUpdates", params=params)

    async def get_chat(self, chat_id: str) -> dict:
        return await self._request("POST", "getChat", json={"chat_id": chat_id})

    async def set_webhook(self, url: str, secret_token: str = None) -> bool:
        payload = {"url": url}
        if secret_token: payload["secret_token"] = secret_token
        return await self._request("POST", "setWebhook", json=payload)

    async def delete_webhook(self) -> bool:
        return await self._request("POST", "deleteWebhook")
