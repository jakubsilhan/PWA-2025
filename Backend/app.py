from gevent import monkey
monkey.patch_all()
from app import app
from app.extensions import db, socketio


if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)