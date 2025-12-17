from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database import Base
from sqlalchemy import Integer, Date, ForeignKey, BigInteger, String
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import date

class Profile(Base):
    __tablename__ = "ggstore_profiles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    nickname: Mapped[str]
    telegram_tag: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    games: Mapped[list["Game"]] = relationship("Game", back_populates="profile")
    about: Mapped[str]
    goal: Mapped[str] = mapped_column(nullable=True)
    goals = mapped_column(ARRAY(String), default=[])
    convenient_time = mapped_column(ARRAY(String), default=[])
    photo: Mapped[str] = mapped_column(nullable=True)
    
    is_active: Mapped[bool] = mapped_column(default=False)
    
    teammate_ids = mapped_column(ARRAY(Integer), default=[])
    polite: Mapped[float] = mapped_column(nullable=True)
    skill: Mapped[float] = mapped_column(nullable=True)
    team_game: Mapped[float] = mapped_column(nullable=True)

    experience: Mapped[int] = mapped_column(default=0)
    send_first_message: Mapped[bool] = mapped_column(default=False)
    last_activity_day: Mapped[date]
    days_series: Mapped[int] = mapped_column(default=1)

    @property
    def games_str(self) -> str:
        return ", ".join([game.name for game in self.games])



class Game(Base):
    __tablename__ = "ggstore_games"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    rank: Mapped[str] = mapped_column(nullable=True)
    gallery: Mapped[list[str]] = mapped_column(ARRAY(String), default=[], nullable=True)

    profile_id: Mapped[int] = mapped_column(ForeignKey("ggstore_profiles.id"))
    profile: Mapped["Profile"] = relationship("Profile", back_populates="games")
