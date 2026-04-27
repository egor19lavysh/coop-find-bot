from repositories.profile_repository import profile_repository as pr
import asyncio


async def update_self_deactivated():
        profiles = await pr.get_profiles()
        for profile in profiles:
            if not profile.is_active:
                await pr.update_self_deactivated(user_id=profile.user_id, value=True)

if __name__ == "__main__":
    asyncio.run(update_self_deactivated())