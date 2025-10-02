from dataclasses import dataclass
from models.clan import Clan
from database import async_sessionmaker, AsyncSessionFactory
from datetime import date
from sqlalchemy import select, update, insert


@dataclass
class ClanRepository:
    session_factory: async_sessionmaker

    async def create_clan(self,
                          user_id: int,
                          name: str,
                          game: str,
                          description: str,
                          demands: str,
                          photo: str = None) -> None:
        query = insert(Clan).values(
            user_id=user_id,
            name=name,
            game=game,
            description=description,
            demands=demands,
            photo=photo
        )
        async with self.session_factory() as session:
            await session.execute(query)
            await session.commit()

    async def get_clan(self, user_id: int) -> Clan | None:
        async with self.session_factory() as session:
            clan = (await session.execute(select(Clan).where(Clan.user_id == user_id))).scalar_one_or_none()
            return clan
        
    async def get_clans_by_game(self, game: str, user_id: int) -> list[Clan]:
        async with self.session_factory() as session:
            clans = (await session.execute(select(Clan).where(Clan.game == game, Clan.user_id != user_id))).scalars().all()
            return clans
        
    async def update_clan_photo(self, user_id: int, new_photo: str) -> None:
        async with self.session_factory() as session:
            if clan := await self.get_clan(user_id=user_id):
                await session.execute(
                    update(Clan).where(Clan.user_id == user_id).values(photo=new_photo)
                )
                await session.commit()
        
    async def delete_clan(self, user_id: int) -> None:
        async with self.session_factory() as session:
            if clan := await self.get_clan(user_id=user_id):
                await session.delete(clan)
                await session.commit()

clan_repository = ClanRepository(session_factory=AsyncSessionFactory)