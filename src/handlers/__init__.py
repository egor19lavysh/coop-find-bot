from handlers.start import router as start_router
from handlers.create_profile import router as create_profile_router
from handlers.menu import router as menu_router
from handlers.profile import router as profile_router
from handlers.search import router as search_profile
from handlers.estimate import router as estimate_router

routers = [start_router, create_profile_router, menu_router, profile_router, search_profile, estimate_router]