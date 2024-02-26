from datetime import datetime
from typing import Generic, Optional, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.models import User

ModelType = TypeVar('ModelType', bound=Base)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[ModelType]:
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(self, session: AsyncSession) -> list[ModelType]:
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def create(
        self,
        object_in: ModelType,
        session: AsyncSession,
        user: Optional[User] = None,
        allow_commit: bool = True,
    ) -> ModelType:
        data_in = object_in.dict()
        data_in['create_date'] = datetime.now()
        data_in['invested_amount'] = 0
        if user is not None:
            data_in['user_id'] = user.id
        db_object = self.model(**data_in)
        session.add(db_object)
        if allow_commit:
            await session.commit()
            await session.refresh(db_object)
        return db_object

    async def remove(
        self,
        db_obj: ModelType,
        session: AsyncSession,
    ) -> ModelType:
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def update(
        self,
        db_obj: ModelType,
        object_in: UpdateSchemaType,
        session: AsyncSession,
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        update_data = object_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_opened(self, session: AsyncSession) -> list[ModelType]:
        # fmt: off
        return (
            await session.execute(
                select(
                    self.model,
                ).where(
                    self.model.fully_invested == false(),
                ).order_by(
                    self.model.create_date,
                ),
            )
        ).scalars().all()
        # fmt: on
