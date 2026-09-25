from typing import Generic, TypeVar, Type, Sequence, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class BaseRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, pk: Any) -> ModelT | None:
        return await self.session.get(self.model, pk)

    async def get_or_raise(self, pk: Any) -> ModelT:
        obj = await self.get(pk)
        if obj is None:
            raise ValueError(f"{self.model.__name__} with pk={pk} not found")
        return obj

    async def list(
        self,
        *,
        limit: int = 100,
        offset: int = 0,
        order_by: Any = None,
        **filters: Any,
    ) -> Sequence[ModelT]:
        stmt = select(self.model)
        for field, value in filters.items():
            # noinspection PyTypeChecker
            stmt = stmt.where(getattr(self.model, field) == value)
        if order_by is not None:
            stmt = stmt.order_by(order_by)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count(self, **filters: Any) -> int:
        stmt = select(func.count()).select_from(self.model)
        for field, value in filters.items():
            # noinspection PyTypeChecker
            stmt = stmt.where(getattr(self.model, field) == value)
        return (await self.session.execute(stmt)).scalar_one()

    async def create(self, **values: Any) -> ModelT:
        obj = self.model(**values)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def update(self, obj: ModelT, **values: Any) -> ModelT:
        for field, value in values.items():
            setattr(obj, field, value)
        await self.session.flush()
        return obj

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()

    async def exists(self, **filters: Any) -> bool:
        return await self.count(**filters) > 0
