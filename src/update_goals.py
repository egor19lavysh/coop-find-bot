from repositories import profile_repository
import asyncio


async def upddate_goals():
    profiles = await profile_repository.get_profiles()
    for profile in profiles:
        if profile.goal:
            await profile_repository.update_goal(user_id=profile.user_id, goals=[profile.goal])

asyncio.run(upddate_goals())