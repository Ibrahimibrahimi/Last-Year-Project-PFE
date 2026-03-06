from flask import Flask
from routes import init_routes
from functions import *


app = Flask(__name__)
init_routes(app)


app.run(debug=True,host="127.0.0.1",port=8080)