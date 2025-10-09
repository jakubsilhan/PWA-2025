from flask import Blueprint
from flask_jwt_extended import jwt_required
from app.services.conversation_service import ConversationService
from flask_socketio import emit, join_room, leave_room

class ConversationController:
    def __init__(self, socketio):
        self.service = ConversationService()
        self.socketio = socketio
        self.blueprint = Blueprint("conversation", __name__)
        self._register_routes()
        self._register_events()

    def _register_routes(self):
        """Endpoints for conversation data retrieval / management"""

        @self.blueprint.route("/conversations", methods=["GET"])
        @jwt_required()
        def get_conversations():
            """Return a list of conversations for the logged-in user"""
            pass

        @self.blueprint.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
        @jwt_required()
        def get_messages(conversation_id):
            """Return messages for a specific conversation"""
            # The ranged stuff
            pass

        @self.blueprint.route("/conversations/<int:conversation_id>/add_user", methods=["POST"])
        @jwt_required()
        def add_user(conversation_id):
            """Add a user to the conversation (body contains user_id)"""
            # emits a notification to join a room
            pass

        # Optional: create conversation
        @self.blueprint.route("/conversations", methods=["POST"])
        @jwt_required()
        def create_conversation():
            """Create a new conversation (body contains participants / name)"""
            pass

    def _register_events(self):
        """Events for real-time updates"""

        @self.socketio.on("join_conversation")
        def join_conversation(data):
            """Client joins all their conversation rooms"""
            conversation_id = data["conversation_id"]
            join_room(conversation_id)

        @self.socketio.on("join_conversation")
        def join_conversation(data):
            """Client joins a conversation room"""
            conversation_id = data["conversation_id"]
            join_room(conversation_id)

        @self.socketio.on("leave_conversation")
        def leave_conversation(data):
            """Client leaves a conversation room"""
            conversation_id = data["conversation_id"]
            leave_room(conversation_id)

        @self.socketio.on("send_message")
        def send_message(data):
            """Client sends a message to a conversation"""
            conversation_id = data["conversation_id"]
            message = data["message"]
            # Save message via service, then emit to room
            # emit("new_message", ..., room=conversation_id)
            pass

        @self.socketio.on("typing")
        def typing(data):
            """Optional: typing indicator"""
            conversation_id = data["conversation_id"]
            # emit("typing", ..., room=conversation_id, include_self=False)
            pass

