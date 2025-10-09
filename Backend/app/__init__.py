import os
from flask import Flask
# from flask_socketio import SocketIO
from app.extensions import db, migrate, jwt, socketio
from flask_cors import CORS
from flasgger import Swagger
from app.controllers.user_controller import UserController
from app.controllers.conversation_controller import ConversationController
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


from app import models

def create_app():
    app = Flask(__name__)

    # Add static html files here

    # Allow origins
    # CORS(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Swagger
    swagger_template = {
            "swagger": "2.0",
            "info": {
                "title": "My API",
                "version": "1.0.0",
                "description": "API documentation with JWT support"
            },
            "securityDefinitions": {
                "jwt": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer <token>'"
                }
            }
        }

    swagger = Swagger(app, template=swagger_template)

    # DB connection 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")

    # JWT
    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app)

    # message_controller = ConversationController(socketio)
    # app.register_blueprint(message_controller.blueprint, url_prefix="/conversations")

    user_controller = UserController(socketio)
    app.register_blueprint(user_controller.blueprint, url_prefix="/users")

    return app
