from repositories.user_repository import user_repository
import asyncio


async def update_users():
    users = await user_repository.get_users()
    for user in users:
        await user_repository.update_clicks(user.user_id, clicks=0)
        
        if not user.last_pop_up:
            await user_repository.update_last_pop_up(user.user_id, pop_up=-1)


asyncio.run(update_users())
