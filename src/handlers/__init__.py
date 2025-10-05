from handlers.start import router as start_router
from handlers.create_profile import router as create_profile_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.search import router as search_profile
from handlers.estimate import router as estimate_router
from handlers.create_clan import router as create_clan_router
from handlers.clan import router as clan_router
from handlers.edit_profile import router as edit_profile_router

routers = [start_router, create_profile_router, menu_router, profile_router, search_profile, estimate_router, create_clan_router, clan_router, edit_profile_router]