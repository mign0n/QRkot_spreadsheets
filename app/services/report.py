from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.models import CharityProject

FORMAT = '%Y/%m/%d %H:%M:%S'
LOCALE = 'ru_RU'
SPREADSHEET_TITLE = 'Отчёт от {date}'
SPREADSHEET_PERMISSIONS = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email,
}
SHEETS = [
    {
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': 100,
                'columnCount': 11,
            },
        },
    },
]
DATA_RANGE = 'A1:C{rows_number}'
TABLE_HEADER = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]


async def spreadsheets_create(wrapper_services: Aiogoogle) -> str:
    return (
        await wrapper_services.as_service_account(
            (
                await wrapper_services.discover('sheets', 'v4')
            ).spreadsheets.create(
                json={
                    'properties': {
                        'title': SPREADSHEET_TITLE.format(
                            date=datetime.now().strftime(FORMAT)
                        ),
                        'locale': LOCALE,
                    },
                    'sheets': SHEETS,
                },
            ),
        )
    )['spreadsheetId']


async def set_user_permissions(
    spreadsheetid: str,
    wrapper_services: Aiogoogle,
) -> None:
    await wrapper_services.as_service_account(
        (await wrapper_services.discover('drive', 'v3')).permissions.create(
            fileId=spreadsheetid,
            json=SPREADSHEET_PERMISSIONS,
            fields='id',
        ),
    )


async def spreadsheets_update_value(
    spreadsheetid: str,
    projects: list[CharityProject],
    wrapper_services: Aiogoogle,
) -> None:
    table_values = TABLE_HEADER
    for project in projects:
        table_values.append(
            [
                project.name,
                str(project.close_date - project.create_date),
                project.description,
            ]
        )
    await wrapper_services.as_service_account(
        (
            await wrapper_services.discover('sheets', 'v4')
        ).spreadsheets.values.update(
            spreadsheetId=spreadsheetid,
            range=DATA_RANGE.format(rows_number=len(table_values)),
            valueInputOption='USER_ENTERED',
            json={'majorDimension': 'ROWS', 'values': table_values},
        )
    )
