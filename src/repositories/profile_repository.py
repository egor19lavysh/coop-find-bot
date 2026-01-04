import asyncio
from dataclasses import dataclass
from models.profile import Profile, Game
from database import async_sessionmaker, AsyncSessionFactory
from datetime import date
from sqlalchemy import select, update, insert, delete
from sqlalchemy.orm import selectinload


@dataclass
class ProfileRepository:
    session_factory: async_sessionmaker

    async def create_profile(self,
                       user_id: int,
                       nickname: str,
                       games: dict[str, dict[str, str]],
                       time: list[str],
                       about: str,
                       goals: list[str],
                       is_active: bool,
                       telegram_tag: str = None,
                       gender: str = None,
                       photo: str = None,
                       ) -> None:
        
        query = insert(Profile).values(
                        user_id=user_id,
                        nickname=nickname,
                        telegram_tag=telegram_tag,
                        gender=gender,
                        convenient_time=time,
                        about=about,
                        goals=goals,
                        photo=photo,
                        is_active=is_active,
                        last_activity_day=date.today()
                    ).returning(Profile.id)
        
        async with self.session_factory() as session:
            profile_id = (await session.execute(query)).scalar_one_or_none()
            for name, info in games.items():
                await session.execute(insert(Game).values(
                    name=name,
                    rank=info["rank"],
                    gallery=info["gallery"],
                    profile_id=profile_id
                ))
            await session.commit()

    async def get_profiles(self) -> list[Profile]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile)
            )
            return result.scalars().all()
        
    async def get_profile(self, user_id: int) -> Profile | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile).where(Profile.user_id == user_id).options(selectinload(Profile.games))
            )
            return result.scalar_one_or_none()

    async def get_profiles_by_game(self, game: str, user_id: int) -> list[Profile]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Profile)
                .join(Profile.games)
                .where(
                    Game.name == game,
                    Profile.is_active == True,
                    Profile.user_id != user_id
                )
                .distinct()
            )
        return result.scalars().all()
    
    async def get_profiles_by_filters(self,
                                      user_id: int, 
                                      game: str,
                                      rank: str = None,
                                      goal: str = None) -> list[Profile]:
        print(user_id, game, rank, goal)
        stmt = select(Profile).join(Profile.games).where(Profile.is_active, 
                                                         Game.name == game, 
                                                         Profile.user_id != user_id)
        if rank:
            stmt = stmt.where(Game.rank == rank)
        if goal:
            stmt = stmt.where(Profile.goals.contains([goal]))

        stmt = stmt.distinct()
    
        async with self.session_factory() as session:
            result = await session.execute(stmt)
            return result.scalars().all()
        
    @staticmethod
    async def get_profiles_by_rank(game_name: str, profiles: list[Profile], rank: str) -> list[Profile]: # Говнокод...
        filtered_profiles = []
        need = rank.split("@")

        for profile in profiles:
            flag = False
            for game in profile.games:
                if game.name == game_name:
                    parts = game.rank.split("@")

                    for i in range(len(need)):
                        if need[i] == "skip":
                            continue
                        if parts[i] != need[i]:
                            flag = True
                            break

                    if not flag:
                        filtered_profiles.append(profile)
                        break
                
        return filtered_profiles

    async def get_raven_profiles(self, user_id: int, rank: str = None, goal: str = None, game: str = "Raven 2") -> list[Profile]:
        stmt = select(Profile).options(selectinload(Profile.games)).where(
            Profile.is_active,
            Game.name == game,
            Profile.user_id != user_id
        )
        if goal:
            stmt = stmt.where(Profile.goals.contains([goal]))

        stmt = stmt.distinct()

        async with self.session_factory() as session:
            result = await session.execute(stmt)
            all_profiles = result.scalars().all()
            print(len(all_profiles))

            return await self.get_profiles_by_rank(game, all_profiles, rank) if rank else all_profiles

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
                if count > 1:
                    new_polite = (profile.polite * (count - 1) + score) / count
                else:
                    new_polite = score

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
                if count > 1:
                    new_skill = (profile.skill * (count - 1) + score) / count
                else:
                    new_skill = score

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
                if count > 1:
                    new_team_game = (profile.team_game * (count - 1) + score) / count
                else:
                    new_team_game = score

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

    async def update_nickname(self, user_id: int, nickname: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(nickname=nickname)
            )
            await session.commit()

    async def update_telegram_tag(self, user_id: int, telegram_tag: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(telegram_tag=telegram_tag)
            )
            await session.commit()

    async def update_gender(self, user_id: int, gender: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(gender=gender)
            )
            await session.commit()

    async def update_about(self, user_id: int, about: str) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(about=about)
            )
            await session.commit()

    async def update_goal(self, user_id: int, goals: list[str]) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(goals=goals)
            )
            await session.commit()

    async def update_time(self, user_id: int, time: list[str]) -> None:
        async with self.session_factory() as session:
            await session.execute(
                update(Profile)
                .where(Profile.user_id == user_id)
                .values(convenient_time=time)
            )
            await session.commit()

    async def update_games(self, user_id: int, games: dict[str, str | None]) -> None:
        async with self.session_factory() as session:
            if profile := await self.get_profile(user_id=user_id):

                await self.delete_games(profile_id=profile.id)

                for name, rank in games.items():
                    await session.execute(insert(Game).values(
                        name=name,
                        rank=rank,
                        profile_id=profile.id
                    ))

                await session.commit()

    async def create_game(self, user_id: int,
                          name: str,
                          rank: str,
                          gallery: list[str]) -> None:
        if profile := await self.get_profile(user_id=user_id):
            async with self.session_factory() as session:
                await session.execute(
                    insert(Game)
                    .values(
                        name=name,
                        rank=rank,
                        gallery=gallery,
                        profile_id=profile.id
                    )
                )
                await session.commit()

    async def update_game_rank(self, user_id: int, game: str, rank: str) -> None:
        if profile := await self.get_profile(user_id=user_id):
            async with self.session_factory() as session:
                await session.execute(
                    update(Game)
                    .where(Game.profile_id == profile.id, Game.name == game)
                    .values(rank=rank)
                )
                await session.commit()
    
    async def update_game_gallery(self, user_id: int, game: str, gallery: list[str]) -> None:
        if profile := await self.get_profile(user_id=user_id):
            async with self.session_factory() as session:
                await session.execute(
                    update(Game)
                    .where(Game.profile_id == profile.id, Game.name == game)
                    .values(gallery=gallery)
                )
                await session.commit()

    async def delete_game(self, user_id: int, game: str) -> None:
        if profile := await self.get_profile(user_id=user_id):
            async with self.session_factory() as session:
                await session.execute(
                    delete(Game)
                    .where(Game.profile_id == profile.id, Game.name == game)
                )
                await session.commit()

    async def delete_games(self, profile_id: int) -> None:
        async with self.session_factory() as session:
            await session.execute(delete(Game).where(Game.profile_id == profile_id))
            await session.commit()

    
    async def get_games_by_user_id(self, user_id: int) -> list[Game]:
        if profile := await self.get_profile(user_id=user_id):
            async with self.session_factory() as session:
                return (await session.execute(select(Game).where(Game.profile_id == profile.id))).scalars().all()
            
            
    async def delete_profile(self, user_id: int) -> None:
        async with self.session_factory() as session:
            profile = await self.get_profile(user_id=user_id)
            if profile:
                await session.execute(delete(Game).where(Game.profile_id==profile.id))
                await session.delete(profile)
                await session.commit()


profile_repository = ProfileRepository(session_factory=AsyncSessionFactory)