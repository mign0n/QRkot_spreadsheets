from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase, ModelType
from app.models import Donation, User


class CRUDDonation(CRUDBase):
    async def get_by_user(
        self,
        user: User,
        session: AsyncSession,
    ) -> list[ModelType]:
        db_obj = await session.execute(
            select(self.model).where(self.model.user_id == user.id)
        )
        return db_obj.scalars().all()


donation_crud = CRUDDonation(Donation)
