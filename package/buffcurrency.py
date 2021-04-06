import time, requests, json, atexit
from apscheduler.schedulers.background import BackgroundScheduler
from package import db
from package.models import BuffRates

def update():
		res = requests.get('http://api.exchangeratesapi.io/v1/latest?access_key=602cc04b94aaa7d94ddea3834c97d99f')
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
				print("a")


scheduler = BackgroundScheduler()
scheduler.add_job(func=update, trigger="interval", hours=24)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())