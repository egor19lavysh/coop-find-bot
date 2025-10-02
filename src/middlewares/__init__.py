from .middleware import SubscriptionMiddleware
from .apscheduler_middleware import SchedulerMiddleware


middlewares_list = [SubscriptionMiddleware, SchedulerMiddleware]