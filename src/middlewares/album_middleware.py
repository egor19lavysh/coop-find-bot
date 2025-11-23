# Source - https://stackoverflow.com/a
# Posted by say8hi
# Retrieved 2025-11-23, License - CC BY-SA 4.0

import asyncio
from abc import ABC
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import Message

from aiogram import BaseMiddleware
from aiogram import types
from aiogram.dispatcher.event.bases import CancelHandler


class AlbumMiddleware(BaseMiddleware, ABC):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: int | float = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or not event.media_group_id:
            return await handler(event, data)

        try:
            self.album_data[event.media_group_id].append(event)
            return  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)

            event.model_config["is_last"] = True
            data["album"] = self.album_data[event.media_group_id]

            result = await handler(event, data)

            if event.media_group_id and event.model_config.get("is_last"):
                del self.album_data[event.media_group_id]

            return result
