import time
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

from license_plates_stat.get_data_module import GetData


update_data = GetData()

def init_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_data.update, 'cron', hour=22, minute=30)
    scheduler.start()


def run_gunicorn():
    subprocess.run(["poetry", "run", "gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "license_plates_stat:app"])

if __name__ == "__main__":
    init_scheduler()
    run_gunicorn()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
