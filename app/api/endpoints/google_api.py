from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.report import (
    set_user_permissions,
    spreadsheets_create,
    spreadsheets_update_value,
)

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
):
    """Только для суперюзеров."""
    spreadsheet_id, spreadsheet_url = await spreadsheets_create(
        wrapper_services
    )
    drive_service = await set_user_permissions(
        spreadsheet_id,
        wrapper_services,
    )
    try:
        await spreadsheets_update_value(
            spreadsheet_id,
            await charity_project_crud.get_projects_by_completion_rate(
                session,
            ),
            wrapper_services,
        )
    except HTTPException as error:
        await wrapper_services.as_service_account(
            drive_service.files.delete(fileId=spreadsheet_id),
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.detail,
        )
    return spreadsheet_url
