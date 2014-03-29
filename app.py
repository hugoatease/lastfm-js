from flask import Flask
from lastapi import api

app = Flask(__name__)
app.config.from_pyfile('config.py')

app.register_blueprint(api)

if __name__ == '__main__':
    app.run()