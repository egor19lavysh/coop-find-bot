from repositories.user_repository import UserRepository
from google_sheet import GoogleSheetService
from datetime import datetime


class Statistic:
    def __init__(self, google_sheet: GoogleSheetService, user_repository: UserRepository):
        self._google_sheet = google_sheet
        self._user_repository = user_repository

    async def add_row(self, user_id, username: str, utm_label: str, created_at: datetime) -> int:
        index = self._google_sheet.get_row_index_multi({0: user_id, 2: utm_label})
        if index:
            return index
        row = [user_id, username, utm_label, created_at.strftime('%d.%m.%Y %H:%M:%S'), '-', '-', '-', '-']
        return self._google_sheet.insert_row(row)

    async def _update_row(self, user_id: int, col_index: int):
        user_data = await self._user_repository.get_last_utm(user_id)
        utm_label = user_data.get('utm_label')
        index = self._google_sheet.get_row_index_multi({0: user_id, 2: utm_label})
        if not index:
            username = user_data.get('username')
            created_at = user_data.get('created_at')
            index = await self.add_row(user_id=user_id, utm_label=utm_label, username=username, created_at=created_at)
        self._google_sheet.update_row(index, {col_index: "'+"})

    async def set_filled_profile(self, user_id: int):
        await self._update_row(user_id, 4)

    async def set_start_search(self, user_id: int):
        await self._update_row(user_id, 5)

    async def set_open_profile(self, user_id: int):
        await self._update_row(user_id, 6)

    async def set_invite_game(self, user_id: int):
        await self._update_row(user_id, 7)