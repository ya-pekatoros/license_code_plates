import time
import datetime



print('hey')
message = f'last update was {datetime.datetime.now().strftime("%Y-%m-%d %H-%M")} the next will be {(datetime.datetime.now()+datetime.timedelta(days=1)).strftime("%Y-%m-%d %H-%M")}'
print(message)
