from apscheduler.schedulers.background import BackgroundScheduler
import os
import random
from time import sleep


from license_plates_stat.get_data_module import GetData

update_data = GetData()
scheduler_file = 'scheduler.lock'


def init_scheduler():
    sleep(random.random())
    if not os.path.exists(scheduler_file):
        with open(scheduler_file, 'w') as f:
            f.write('scheduler lock file')
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_data.update, 'cron', hour=22, minute=30)
        scheduler.start()
