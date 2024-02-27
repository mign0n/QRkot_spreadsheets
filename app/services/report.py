from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.api.validators import check_data_fits_table_grid
from app.core.config import settings
from app.models import CharityProject

FORMAT = '%Y/%m/%d %H:%M:%S'
LOCALE = 'ru_RU'
TITLE = 'Отчёт от'
SPREADSHEET_PERMISSIONS = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email,
}
ROW_COUNT = 100
COLUMN_COUNT = 11
SHEETS = [
    {
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': 'Лист1',
            'gridProperties': {
                'rowCount': ROW_COUNT,
                'columnCount': COLUMN_COUNT,
            },
        },
    },
]

TABLE_HEADER = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
SPREADSHEET_PROPERTIES = {
    'properties': {
        'title': TITLE,
        'locale': LOCALE,
    },
    'sheets': SHEETS,
}


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    properties=deepcopy(SPREADSHEET_PROPERTIES),
) -> tuple[str, str]:
    properties['properties']['title'] += ' {}'.format(
        datetime.now().strftime(FORMAT)
    )
    response = await wrapper_services.as_service_account(
        (await wrapper_services.discover('sheets', 'v4')).spreadsheets.create(
            json=properties
        ),
    )
    return response['spreadsheetId'], response['spreadsheetUrl']


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle,
) -> None:
    await wrapper_services.as_service_account(
        (await wrapper_services.discover('drive', 'v3')).permissions.create(
            fileId=spreadsheet_id,
            json=SPREADSHEET_PERMISSIONS,
            fields='id',
        ),
    )


async def spreadsheets_update_value(
    spreadsheet_id: str,
    projects: list[CharityProject],
    wrapper_services: Aiogoogle,
) -> None:
    table_values = [
        [TITLE, datetime.now().strftime(FORMAT)],
        *TABLE_HEADER,
        *[
            list(
                map(
                    str,
                    [
                        project.name,
                        project.close_date - project.create_date,
                        project.description,
                    ],
                )
            )
            for project in projects
        ],
    ]
    await check_data_fits_table_grid(table_values, ROW_COUNT, COLUMN_COUNT)
    await wrapper_services.as_service_account(
        (
            await wrapper_services.discover('sheets', 'v4')
        ).spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='R1C1:R{}C{}'.format(ROW_COUNT, COLUMN_COUNT),
            valueInputOption='USER_ENTERED',
            json={'majorDimension': 'ROWS', 'values': table_values},
        )
    )
