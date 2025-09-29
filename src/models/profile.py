from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base
from sqlalchemy import ARRAY, Integer


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
    rating: Mapped[float] = mapped_column(default=0.0)
    is_active: Mapped[bool] = mapped_column(default=False)
    photo: Mapped[str] = mapped_column(nullable=True)
    teammate_ids = mapped_column(ARRAY(Integer))


