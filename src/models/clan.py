from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from sqlalchemy import ARRAY, Integer, Date
from datetime import date

class Clan(Base):
    __tablename__ = "ggstore_clans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int]
    name: Mapped[str]
    game: Mapped[str]
    description: Mapped[str]
    demands: Mapped[str]
    photo: Mapped[str] = mapped_column(nullable=True)