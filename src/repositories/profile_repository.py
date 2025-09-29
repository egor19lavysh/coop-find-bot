from dataclasses import dataclass
from models.profile import Profile
from database import get_db_session, AsyncSession


@dataclass
class ProfileRepository:
    db_session: AsyncSession

    def create_profile(self):
        pass

