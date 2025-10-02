from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from sqlalchemy import ARRAY, Integer, Date
from datetime import date

class Profile(Base):
    __tablename__ = "ggstore_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    nickname: Mapped[str]
    telegram_tag: Mapped[str] = mapped_column(nullable=True)
    gender: Mapped[str] = mapped_column(nullable=True)
    game: Mapped[str]
    rank: Mapped[str] = mapped_column(nullable=True)
    about: Mapped[str]
    goal: Mapped[str]
    photo: Mapped[str] = mapped_column(nullable=True)
    
    is_active: Mapped[bool] = mapped_column(default=False)
    
    teammate_ids = mapped_column(ARRAY(Integer), default=[])
    polite: Mapped[float] = mapped_column(nullable=True)
    skill: Mapped[float] = mapped_column(nullable=True)
    team_game: Mapped[float] = mapped_column(nullable=True)

    experience: Mapped[int] = mapped_column(default=0)
    send_first_message: Mapped[bool] = mapped_column(default=False)
    five_consecutive_days: Mapped[bool] = mapped_column(default=False)
    last_activity_day: Mapped[date]
    days_series: Mapped[int] = mapped_column(default=1)




