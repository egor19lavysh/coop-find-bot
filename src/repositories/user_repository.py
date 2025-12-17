from dataclasses import dataclass
from src.models.user import User
from src.database import async_sessionmaker, AsyncSessionFactory
from sqlalchemy import insert, select, func, desc
from typing import Optional



@dataclass
class UserRepository:
    session_factory: async_sessionmaker

    async def add_user(self,
                       user_id: int,
                       username: str,
                       first_name: str,
                       last_name: str,
                       utm_label: Optional[str]) -> None:
        query = insert(User).values(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            utm_label=utm_label)
        async with self.session_factory() as session:
            await session.execute(query)
            await session.commit()

    async def get_last_utm(self, user_id: int) -> dict:
        async with self.session_factory() as session:
            query = (
                select(
                    func.coalesce(User.utm_label, 'None').label('utm_label'),
                    func.coalesce(User.username, 'None').label('username'),
                    func.coalesce(User.created_at, func.now()).label('created_at')
                )
                .where(User.user_id == user_id)
                .order_by(desc(User.row_id))
                .limit(1)
            )
            data = await session.execute(query)
            result = data.one_or_none()
            if not result:
                result = {'utm_label': 'None', 'username': 'None', 'created_at': 'None'}
            else:
                result = dict(result._mapping)
            return result


user_repository = UserRepository(session_factory=AsyncSessionFactory)