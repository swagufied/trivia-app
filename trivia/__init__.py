from apscheduler.schedulers.background import BackgroundScheduler
from .router.RouterManager import RouterManager

scheduler = BackgroundScheduler()
scheduler.start()


# initialize a game object for every room that is currently in a game. this is meant as a way to continue games even after a server disconnect
running_games = {}




# delete all tickets


