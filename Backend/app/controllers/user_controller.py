from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, set_access_cookies, decode_token
from app.services.user_service import UserService
from app.dtos.user_dto import UserDTO
from flask_socketio import join_room, leave_room, disconnect, emit
from app.controllers import connected_users, connected_sessions
import jwt


class UserController:
    def __init__(self, socketio):
        self.service = UserService()
        self.socketio = socketio
        self.blueprint = Blueprint("user", __name__)
        self._register_routes()
        self._register_events()

    def _register_routes(self):
        """Contains endpoints for user authentication and profile management using HTTP"""

        @self.blueprint.route("/register", methods=["POST"])
        def register_user():
            """
            Register a new user
            ---
            tags:
                - User
            summary: Create a new user account.
            parameters:
                - in: body
                  name: body
                  required: true
                  schema:
                    type: object
                    properties:
                        username:
                            type: string
                            description: Desired unique username.
                        email:
                            type: string
                            format: email
                            description: User's email address.
                        password:
                            type: string
                            format: password
                            description: Secure password for the account.
                    required:
                        - username
                        - email
                        - password
            responses:
                201:
                    description: User created successfully
                400:
                    description: User creation failed (e.g., email/username taken)
                500:
                    description: Internal server error
            """
            data = request.get_json(silent=True) or {}
            username = data.get("username")
            email = data.get("email")
            password = data.get("password")

            try:
                self.service.register_user(username, email, password)

                return jsonify({"message": "User created successfully"}), 201
            except ValueError as e:
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                return jsonify({"error": "Internal server error"}), 500

        @self.blueprint.route("/login", methods=["POST"])
        def login_user():
            """
            User login
            ---
            tags:
            - User
            summary: Authenticate a user and return a JWT token/cookies.
            parameters:
                - in: body
                  name: body
                  required: true
                  schema:
                    type: object
                    properties:
                        email:
                            type: string
                            format: email
                            description: User's email address.
                        password:
                            type: string
                            format: password
                            description: Secure password for the account.
                    required:
                        - email
                        - password
            responses:
                200:
                    description: Login successful
                    content:
                        application/json:
                            schema:
                                type: object
                                properties:
                                    message: {type: string}
                                    token: {type: string}
                401:
                    description: Invalid email or password
            """
            data = request.get_json(silent=True) or {}
            email = data.get("email")
            password = data.get("password")

            try:
                token = self.service.login_user(email, password)
            except ValueError as e:
                return jsonify({"message": str(e)}), 401

            response = jsonify({"message": "Login successful", "token": token})

            set_access_cookies(response, token)

            return response, 200

        @self.blueprint.route("/search", methods=["POST"])
        @jwt_required()
        def search_profiles():
            """
            Search for users by username
            ---
            tags:
            - User
            summary: Search for users with similar usernames
            security:
            - jwt: []
            parameters:
                - in: body
                  name: body
                  required: true
                  schema:
                    type: object
                    properties:
                        username:
                            type: string
                            description: Desired unique username.
                    required:
                        - username
            responses:
                200:
                    description: List of matching users
                    schema:
                    type: object
                    properties:
                        profiles:
                        type: array
                        items:
                            type: object
                            properties:
                            id:
                                type: integer
                                description: User ID
                            username:
                                type: string
                                description: Username
                            email:
                                type: string
                                description: User email
                400:
                    description: Username is required
                    schema:
                    type: object
                    properties:
                        error:
                        type: string
                        example: "Username is required"
                401:
                    description: Unauthorized (JWT missing or invalid)
            """
            data = request.get_json(silent=True) or {}
            username = data.get("username")

            if not username:
                return jsonify({"error": "Username is required"}), 400
            
            profiles = self.service.get_profiles(username)

            profiles_dto = [UserDTO.from_user(profile).__dict__ for profile in profiles]

            return jsonify({"profiles": profiles_dto}), 200
        

    def _register_events(self):
        """Contains endpoints for user authentication and profile management using Websockets"""
        @self.socketio.on("connect")
        def handle_connect():
            """Client connects via websocket"""
            try:
                token = request.cookies.get("access_token_cookie") or request.args.get("access_token_cookie")
                if not token:
                    emit("auth_error", {"message": "No JWT token provided"})
                    return disconnect()
                
                decoded = decode_token(token)
                user_id = decoded.get("sub")
                if not user_id:
                    emit("auth_error", {"message": "Invalid token: missing user ID"})
                    return disconnect()

                # Store connection
                connected_users[request.sid] = user_id
                connected_sessions[user_id] = request.sid

            except jwt.ExpiredSignatureError:
                emit("auth_error", {"message": "Token expired"})
                return disconnect()
            except Exception as e:
                emit("auth_error", {"message": f"Invalid token: {e}"})
                return disconnect()

        @self.socketio.on("disconnect")
        def handle_disconnect():
            """Client disconnects from websocket"""
            user_id = connected_users.pop(request.sid, None)
            session_id = connected_sessions.pop(user_id, None)