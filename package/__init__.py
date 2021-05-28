from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
#from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
#crsf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'ec7a2afe4677b7e8874acb729f843921'

DB_CREDENTIALS = os.environ.get('DB_CREDENTIALS')
if not DB_CREDENTIALS:
	print('no database credentials found, using default')
	DB_CREDENTIALS = "sqlite:///site.db"
app.config['SQLALCHEMY_DATABASE_URI'] = DB_CREDENTIALS
db = SQLAlchemy(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from package import routes
from package import buffcurrency