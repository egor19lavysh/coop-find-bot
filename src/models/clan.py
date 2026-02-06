from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from sqlalchemy import ARRAY, Integer, DateTime, func, BigInteger
from datetime import datetime

class Clan(Base):
    __tablename__ = "ggstore_clans"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id = mapped_column(BigInteger)
    name: Mapped[str]
    game: Mapped[str]
    add_info: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str]
    demands: Mapped[str]
    photo: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=True)
