import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = \
			'postgresql://{user}:{password}@{host}:{port}/{db_name}'.format(
				user = os.environ.get('POSTGRES_USER', 'nessus'), 
				password = os.environ.get('POSTGRES_PASSWORD', '123'), 
				host = os.environ.get('POSTGRES_HOST', 'localhost'), 
				port = os.environ.get('POSTGRES_PORT', '5432'), 
				db_name = os.environ.get('POSTGRES_DB', 'nessus_driver')
			)

REDIS_URL = "redis://{host}:{port}/".format(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=os.environ.get('REDIS_PORT', '6379')
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

MEDIA_FOLDER = os.path.join(os.getcwd(), 'scanresults')

if not os.path.exists(MEDIA_FOLDER):
    os.mkdir(MEDIA_FOLDER)
