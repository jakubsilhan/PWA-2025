from app import create_app
from app.extensions import db, socketio
app = create_app()

if __name__ == "__main__":
    # app.run(debug=True)
    socketio.run(app, debug=True)