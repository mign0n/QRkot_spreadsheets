from copy import deepcopy
from datetime import datetime

from aiogoogle import Aiogoogle, GoogleAPI
from fastapi import HTTPException, status

from app.core.config import settings
from app.models import CharityProject

FORMAT = '%Y/%m/%d %H:%M:%S'
TITLE = 'Отчёт от'
SPREADSHEET_PERMISSIONS = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': settings.email,
}
ROW_COUNT = 100
COLUMN_COUNT = 11
TABLE_HEADER = [
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание'],
]
SPREADSHEET_PROPERTIES = {
    'properties': {
        'title': TITLE,
        'locale': 'ru_RU',
    },
    'sheets': [
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
    ],
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
) -> GoogleAPI:
    drive_service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        drive_service.permissions.create(
            fileId=spreadsheet_id,
            json=SPREADSHEET_PERMISSIONS,
            fields='id',
        ),
    )
    return drive_service


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

    table_row_count = len(table_values)
    table_column_count = max(len(row) for row in table_values)
    if table_row_count > ROW_COUNT or table_column_count > COLUMN_COUNT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Передаваемые данные размером {}x{} не поместятся в '
                'созданной таблице размером {}x{}.'
            ).format(
                table_column_count,
                table_row_count,
                COLUMN_COUNT,
                ROW_COUNT,
            ),
        )

    await wrapper_services.as_service_account(
        (
            await wrapper_services.discover('sheets', 'v4')
        ).spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range='R1C1:R{}C{}'.format(table_row_count, table_column_count),
            valueInputOption='USER_ENTERED',
            json={'majorDimension': 'ROWS', 'values': table_values},
        )
    )
