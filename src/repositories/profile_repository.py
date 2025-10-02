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

    async def get_profiles_by_game(self, game: str, user_id: int) -> list[Profile]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile).where(Profile.game == game, Profile.is_active, Profile.user_id != user_id)
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

    async def add_teammate_id(self, user_id: int, teammate_id: int) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile.teammate_ids).where(Profile.user_id == user_id)
            )
            current_ids = result.scalar_one_or_none()

            if current_ids is None:
                new_ids = [teammate_id]
                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(teammate_ids=new_ids)
                )
                await session.commit()
                
            else:
                current_ids_int = [int(id) for id in current_ids] if current_ids else []
                
                if teammate_id not in current_ids_int:
                    new_ids = current_ids + [teammate_id]
                    await session.execute(
                        update(Profile)
                        .where(Profile.user_id == user_id)
                        .values(teammate_ids=new_ids)
                    )
                    await session.commit()

                
    async def update_polite(self, user_id: int, score: int) -> None:
        async with self.session_factory() as session:
            if profile := await self.get_profile(user_id=user_id):
                count = len(profile.teammate_ids)
                new_polite = (profile.polite * (count - 1) + score) / count

                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(polite=new_polite)
                )
                await session.commit()

    async def update_skill(self, user_id: int, score: int) -> None:
        async with self.session_factory() as session:
            if profile := await self.get_profile(user_id=user_id):
                count = len(profile.teammate_ids)
                new_skill = (profile.skill * (count - 1) + score) / count

                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(skill=new_skill)
                )
                await session.commit()

    async def update_team_game(self, user_id: int, score: int) -> None:
        async with self.session_factory() as session:
            if profile := await self.get_profile(user_id=user_id):
                count = len(profile.teammate_ids)
                new_team_game = (profile.team_game * (count - 1) + score) / count

                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(team_game=new_team_game)
                )
                await session.commit()

    async def add_experience(self, user_id: int, experience: int) -> None:
        async with self.session_factory() as session:
            if profile := await self.get_profile(user_id=user_id):
                await session.execute(update(Profile).where(Profile.user_id == user_id).values(experience=profile.experience + experience))
                await session.commit()

    async def update_last_activity_day(self, user_id: int, day: date) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(update(Profile).where(Profile.user_id == user_id).values(last_activity_day=day))
                await session.commit()
    
    async def update_days_series(self, user_id: int, days: int = 1) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(update(Profile).where(Profile.user_id == user_id).values(days_series=days))
                await session.commit()

    async def update_send_first_message(self, user_id: int, value: bool = True) -> None:
        async with self.session_factory() as session:
            if await self.get_profile(user_id=user_id):
                await session.execute(update(Profile).where(Profile.user_id == user_id).values(send_first_message=value))
                await session.commit()

    async def delete_profile(self, user_id: int) -> None:
        async with self.session_factory() as session:
            profile = await self.get_profile(user_id=user_id)
            if profile:
                await session.delete(profile)
                await session.commit()


profile_repository = ProfileRepository(session_factory=AsyncSessionFactory)