import asyncio
from dataclasses import dataclass
from models.profile import Profile
from database import async_sessionmaker, AsyncSessionFactory
from datetime import date
from sqlalchemy import select, update, insert


@dataclass
class ProfileRepository:
    session_factory: async_sessionmaker

    async def create_profile(self,
                       user_id: int,
                       nickname: str,
                       game: str,
                       about: str,
                       goal: str,
                       is_active: bool,
                       telegram_tag: str = None,
                       gender: str = None,
                       rank: str = None,
                       photo: str = None,
                       ) -> None:
        
        query = insert(Profile).values(
                        user_id=user_id,
                        nickname=nickname,
                        telegram_tag=telegram_tag,
                        gender=gender,
                        game=game,
                        rank=rank,
                        about=about,
                        goal=goal,
                        photo=photo,
                        is_active=is_active,
                        last_activity_day=date.today()
                    )
        async with self.session_factory() as session:
            await session.execute(query)
            await session.commit()

    async def get_profile(self, user_id: int) -> Profile | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile).where(Profile.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_profiles_by_game(self, game: str) -> list[Profile]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile).where(Profile.game == game and Profile.is_active)
            )
            return result.scalars().all()

    async def update_photo(self, user_id: int, photo: str) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(photo=photo)
                )
                await session.commit()

    async def deactivate_profile(self, user_id: int) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(is_active=False)
                )
                await session.commit()

    async def activate_profile(self, user_id: int) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(is_active=True)
                )
                await session.commit()


    async def delete_profile(self, user_id: int) -> None:
        async with self.session_factory() as session:
            profile = await self.get_profile(user_id=user_id)
            if profile:
                await session.delete(profile)
                await session.commit()


profile_repository = ProfileRepository(session_factory=AsyncSessionFactory)