from dataclasses import dataclass
from models.profile import Profile
from database import get_db_session, AsyncSession
from datetime import date


@dataclass
class ProfileRepository:
    db_session: AsyncSession

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
        
        async with self.db_session as session:
            new_profile = Profile(
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

            await session.add(new_profile)
            await session.commit()

    from dataclasses import dataclass
from models.profile import Profile
from database import get_db_session, AsyncSession
from datetime import date
from sqlalchemy import select, update


@dataclass
class ProfileRepository:
    db_session: AsyncSession

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
        
        async with self.db_session as session:
            new_profile = Profile(
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

            session.add(new_profile)
            await session.commit()

    async def get_profile(self, user_id: int) -> Profile | None:
        async with self.db_session as session:
            result = await session.execute(
                select(Profile).where(Profile.user_id == user_id)
            )
            return result.scalar_one_or_none()

    async def get_profiles_by_game(self, game: str) -> list[Profile]:
        async with self.db_session as session:
            result = await session.execute(
                select(Profile).where(Profile.game == game)
            )
            return result.scalars().all()

    async def update_profile(self, 
                       user_id: int,
                       nickname: str = None,
                       game: str = None,
                       about: str = None,
                       goal: str = None,
                       is_active: bool = None,
                       telegram_tag: str = None,
                       gender: str = None,
                       rank: str = None,
                       photo: str = None) -> None:
        
        update_data = {}
        fields = {
            'nickname': nickname,
            'game': game,
            'about': about,
            'goal': goal,
            'is_active': is_active,
            'telegram_tag': telegram_tag,
            'gender': gender,
            'rank': rank,
            'photo': photo
        }
        
        for field, value in fields.items():
            if value is not None:
                update_data[field] = value

        if update_data:
            async with self.db_session as session:
                await session.execute(
                    update(Profile)
                    .where(Profile.user_id == user_id)
                    .values(**update_data)
                )
                await session.commit()

    async def delete_profile(self, user_id: int) -> None:
        async with self.db_session as session:
            profile = await session.get(Profile, user_id)
            if profile:
                await session.delete(profile)
                await session.commit()

