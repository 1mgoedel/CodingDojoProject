# from flask import FLask
from flask_app.controllers import users
from flask_app.controllers import events
from flask_app import app

if __name__ == "__main__":
    app.run(debug=True, host='localhost', port=8000)

