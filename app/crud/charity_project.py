from typing import Optional

from sqlalchemy import select, true
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase, ModelType
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
)


class CRUDCharityProject(
    CRUDBase[
        CharityProject,
        CharityProjectCreate,
        CharityProjectUpdate,
    ]
):
    async def get_project_id_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        project_id = project_id.scalars().first()
        return project_id

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        # fmt: off
        return (
            await session.execute(
                select(
                    self.model,
                ).where(
                    self.model.fully_invested == true(),
                ).order_by(
                    self.model.close_date - self.model.create_date,
                ),
            )
        ).scalars().all()
        # fmt: on


charity_project_crud = CRUDCharityProject(CharityProject)
