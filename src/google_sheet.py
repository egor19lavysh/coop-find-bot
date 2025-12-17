from gspread import service_account
from gspread.exceptions import WorksheetNotFound
from pathlib import Path
from logging import getLogger

logger = getLogger('GoogleSheetService')


class GoogleSheetService:
    def __init__(self, credentials_path: Path, sheet_id: str, worksheet: str):
        """Инициализая объекта для работы с Google Sheet"""
        self.google_service = service_account(filename=credentials_path)
        self.sheet = self.google_service.open_by_key(key=sheet_id)
        try:
            self.worksheet = self.sheet.worksheet(title=worksheet)
        except WorksheetNotFound:
            self.worksheet = self.sheet.add_worksheet(title=worksheet, rows=100, cols=10)

    def insert_row(self, row: list) -> int:
        """Вставка строки в конец таблицы. Возвращает индекс вставленной строки."""
        self.worksheet.append_row(row)
        return len(self.worksheet.get_all_values())

    def get_row_index(self, value: str, column: int = 1) -> int | None:
        """Поиск строки по значению в указанном столбце. Возвращает индекс строки (1-based) или None"""
        all_values = self.worksheet.get_all_values()
        for i, row in enumerate(all_values):
            if len(row) >= column and row[column - 1] == value:
                return i + 1
        return None

    def get_row_index_multi(self, criteria: dict) -> int | None:
        """
        Находит индекс строки по нескольким критериям.
        Критерии: {индекс_столбца: значение}
        """
        try:
            # Получаем все данные с листа
            data = self.sheet.get_all_values()
            
            for row_index, row in enumerate(data):
                try:
                    # Проверяем все критерии с безопасным доступом к элементам
                    matches_all = True
                    for col_index, expected_value in criteria.items():
                        # Получаем значение из строки с проверкой границ
                        cell_value = row[col_index] if col_index < len(row) else ""
                        if str(cell_value) != str(expected_value):
                            matches_all = False
                            break
                    
                    if matches_all:
                        return row_index + 1  # +1 потому что в Google Sheets нумерация с 1
                        
                except IndexError:
                    # Пропускаем строки, которые короче чем нужно
                    continue
                    
            return None
        
        except Exception as e:
            print(f"Ошибка при поиске строки: {e}")
            return None

    def update_row(self, index: int, data: dict):
        """
        Обновляет только указанные ячейки в строке.
        data = {номер_колонки: новое_значение}
        """
        logger.debug("index = %d, data = %s", index, data)
        for col_index, value in data.items():
            self.worksheet.update_cell(index, col_index + 1, value)