import time, requests, json, atexit, os
from apscheduler.schedulers.background import BackgroundScheduler
from package import db
from package.models import BuffRates

def update():
		res = requests.get(f'http://api.exchangeratesapi.io/v1/latest?access_key={os.environ.get("BUFF_API_KEY")}')
		data = res.json()

		if (data['success']):
				tmpRates = {}
				for rate in data['rates']:
						tmpRates[rate] = data['rates'][rate] / data['rates']['CNY']
				data['rates'] = tmpRates
				data['base'] = 'CNY'
				
				if BuffRates.query.count() == 0:
						db.session.add(BuffRates(rates=json.dumps(data)))
						db.session.commit()
				else:
						BuffRates.query.first().rates = json.dumps(data)
						db.session.commit()
		else:
				raise Exception('Not a succesful API request')

update()
scheduler = BackgroundScheduler()
scheduler.add_job(func=update, trigger="interval", hours=24)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())