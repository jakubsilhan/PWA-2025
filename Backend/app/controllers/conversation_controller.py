from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.conversation_service import ConversationService
from app.services.user_service import UserService
from flask_socketio import emit, join_room, leave_room
from app.controllers import connected_users, connected_sessions
from app.dtos.conversation_dto import ConversationDTO
from app.dtos.message_dto import MessageDTO

class ConversationController:
    def __init__(self, socketio):
        self.service = ConversationService()
        self.user_service = UserService()
        self.socketio = socketio
        self.blueprint = Blueprint("conversation", __name__)
        self._register_routes()
        self._register_events()

    def _register_routes(self):
        """Endpoints for conversation data retrieval / management"""

        @self.blueprint.route("/conversations", methods=["GET"])
        @jwt_required()
        def get_conversations():
            """
            Return a list of conversations for the logged-in user
            ---
            tags:
                - Conversation
            summary: Get a list of the user's conversations.
            security:
            - jwt: []
            responses:
                200:
                    description: A list of conversations retrieved successfully.
                401:
                    description: Unauthorized - Missing or invalid JWT token.
            """
            user_id = get_jwt_identity()
            conversations = self.service.get_conversations(user_id)
            conversations_dto = list()
            for conversation in conversations:
                try:
                    last_message = self.service.get_messages(conversation.id, 1, 0)[0]
                    conv_dto = ConversationDTO(conversation.id, conversation.chat_name, last_message.content, last_message.sender.username, last_message.timestamp.isoformat(), True).__dict__
                except IndexError:
                    conv_dto = ConversationDTO(conversation.id, conversation.chat_name, "", "", "", True).__dict__
                conversations_dto.append(conv_dto)
            # conversations_dto = [ConversationDTO.from_conversation(conversation).__dict__ for conversation in conversations]
            return jsonify({"conversations": conversations_dto}), 200
        
        @self.blueprint.route("/all_conversations", methods=["GET"])
        @jwt_required()
        def get_all_conversations():
            """
            Return a list of all conversations
            ---
            tags:
                - Conversation
            summary: Get a list of all conversations.
            security:
            - jwt: []
            responses:
                200:
                    description: A list of conversations retrieved successfully.
                401:
                    description: Unauthorized - Missing or invalid JWT token.
            """
            user_id = get_jwt_identity()
            conversations = self.service.get_all_conversations()
            conversations_dto = list()
            for conversation in conversations:
                can_access = self.service.is_user_in_conversation(user_id, conversation.id)
                conv_dto = ConversationDTO(conversation.id, conversation.chat_name, "", "", "", can_access).__dict__
                conversations_dto.append(conv_dto)
            return jsonify({"conversations": conversations_dto}), 200

        @self.blueprint.route("/conversations/<int:conversation_id>/messages", methods=["GET"])
        @jwt_required()
        def get_messages(conversation_id):
            """
            Return messages for a specific conversation
            ---
            tags:
                - Conversation
            summary: Retrieve messages from a specific conversation.
            security:
            - jwt: []
            parameters:
                - in: path
                  name: conversation_id
                  type: integer
                  required: true
                  description: The ID of the conversation to retrieve messages from.
                - in: query
                  name: limit
                  type: integer
                  required: false
                  default: 30
                  description: Maximum number of messages to return.
                - in: query
                  name: offset
                  type: integer
                  required: false
                  default: 0
                  description: The starting message offset for pagination.
            responses:
                200:
                    description: Messages retrieved successfully.
                401:
                    description: Unauthorized - Missing or invalid JWT token.
                403:
                    description: Access denied - User is not a participant in this conversation.
            """
            user_id = get_jwt_identity()

            if not self.service.is_user_in_conversation(user_id, conversation_id):
                print(user_id)
                return jsonify({"error": "Access denied"}), 403
            
            limit = int(request.args.get("limit", 30))
            offset = int(request.args.get("offset", 0))

            messages = self.service.get_messages(conversation_id, limit, offset)

            messages_dto = [
                MessageDTO.from_message(m).__dict__
                for m in messages
            ]
            return jsonify({"messages": messages_dto}), 200

        @self.blueprint.route("/conversations/<int:conversation_id>/add_user", methods=["POST"])
        @jwt_required()
        def add_user(conversation_id):
            """
            Add a user to the conversation
            ---
            tags:
            - Conversation
            summary: Add a new user to a specific conversation.
            security:
            - jwt: []
            parameters:
            - in: path
              name: conversation_id
              type: integer
              required: true
              description: The ID of the conversation to add a user to.
            - in: body
              name: body
              required: true
              schema:
                type: object
                properties:
                    user_id:
                        type: integer
                        description: ID of the user to be added to the conversation.
                required:
                    - user_id
            responses:
                200:
                    description: User added successfully.
                400:
                    description: Invalid input (e.g., missing user_id or user already in conversation/service error).
                401:
                    description: Unauthorized - Missing or invalid JWT token.
                403:
                    description: Access denied - Current user is not a participant in this conversation.
            """
            user_id = get_jwt_identity()
            data = request.get_json() or {}
            new_user_id = data.get("user_id")

            if not new_user_id:
                return jsonify({"error": "user_id is required"}), 400

            if not self.service.is_user_in_conversation(user_id, conversation_id):
                return jsonify({"error": "Access denied"}), 403

            try:
                conversation = self.service.add_user_to_conversation(conversation_id, new_user_id)
                conversation_dto = ConversationDTO.from_conversation(conversation).__dict__
                sid = connected_sessions.get(new_user_id)
                if sid:
                    self.socketio.emit("new_conversation", conversation_dto, room=sid)
                return jsonify({"message": "User added successfully"}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

        @self.blueprint.route("/conversations", methods=["POST"])
        @jwt_required()
        def create_conversation():
            """
            Create a new conversation
            ---
            tags:
            - Conversation
            summary: Start a new conversation.
            security:
            - jwt: []
            parameters:
            - in: body
              name: body
              required: true
              schema:
                type: object
                properties:
                    chat_name:
                        type: string
                        description: The name for the new conversation (e.g., group chat name).
                    participant_ids:
                        type: array
                        description: List of user IDs (integers) to include in the conversation. The creator's ID will be added automatically.
                        items:
                            type: integer
              required:
                  - chat_name
                  - participant_ids
            responses:
                201:
                    description: Conversation created successfully.
                400:
                    description: Invalid input (e.g., missing chat_name).
                401:
                    description: Unauthorized - Missing or invalid JWT token.
            """
            user_id = get_jwt_identity()
            data = request.get_json() or {}

            chat_name = data.get("chat_name")
            participant_ids = data.get("participant_ids", [])
            if not chat_name:
                return jsonify({"error": "chat_name is required"}), 400

            if user_id not in participant_ids:
                participant_ids.append(int(user_id))


            conversation = self.service.create_conversation(chat_name, participant_ids)
            try:
                last_message = self.service.get_messages(conversation.id, 1, 0)[0]
                conversation_dto = ConversationDTO(conversation.id, conversation.chat_name, last_message.content, last_message.sender.username, last_message.timestamp.isoformat(), True)
            except IndexError:
                conversation_dto = ConversationDTO(conversation.id, conversation.chat_name, "", "", "", True)
            for participant in participant_ids:
                sid = connected_sessions.get(str(participant), None)
                if sid:
                    self.socketio.emit("new_conversation", conversation_dto.__dict__, room=sid)
            return jsonify(conversation_dto), 201
        
        # TODO add these endpoints
        def rename_conversation():
            pass

        @self.blueprint.route("/conversations/<int:conversation_id>/remove_user", methods=["POST"])
        @jwt_required()
        def remove_user(conversation_id):
            """
            Remove a user from the conversation
            ---
            tags:
            - Conversation
            summary: Remove a user from a specific conversation.
            security:
            - jwt: []
            parameters:
            - in: path
              name: conversation_id
              type: integer
              required: true
              description: The ID of the conversation to add a user to.
            - in: body
              name: body
              required: true
              schema:
                type: object
                properties:
                    user_id:
                        type: integer
                        description: ID of the user to be removed from the conversation.
                required:
                    - user_id
            responses:
                200:
                    description: User removed successfully.
                400:
                    description: Invalid input (e.g., missing user_id or user already in conversation/service error).
                401:
                    description: Unauthorized - Missing or invalid JWT token.
                403:
                    description: Access denied - Current user is not a participant in this conversation.
            """
            current_user_id = get_jwt_identity()
            data = request.get_json() or {}
            user_id = data.get("user_id")

            if not user_id:
                return jsonify({"error": "user_id is required"}), 400

            if not self.service.is_user_in_conversation(current_user_id, conversation_id):
                return jsonify({"error": "Access denied"}), 403

            try:
                conversation = self.service.remove_user_from_conversation(conversation_id, user_id)
                sid = connected_sessions.get(user_id)
                if current_user_id == user_id:
                    leave_room(conversation.id)
                return jsonify({"message": "User added successfully"}), 200
            except ValueError as e:
                return jsonify({"error": str(e)}), 400


    def _register_events(self):
        """Events for real-time updates"""

        @self.socketio.on("join_conversation")
        def join_conversation(data):
            """Client joins a conversation room"""
            user_id = connected_users.get(request.sid)
            if not user_id:
                emit("auth_error", {"error": "User not authenticated!"}, room=request.sid)
                return
            
            conversation_id = data.get("conversation_id")
            if not conversation_id:
                emit("error", {"error": "Missing conversation id!"}, room=request.sid)
                return

            if not self.service.is_user_in_conversation(user_id, conversation_id):
                emit("error", {"error": "User is not part of conversation!"}, room=request.sid)
                return
            join_room(conversation_id)

        @self.socketio.on("leave_conversation")
        def leave_conversation(data):
            """Client leaves a conversation room"""
            conversation_id = data.get("conversation_id")
            if not conversation_id:
                emit("error", {"error": "Missing conversation id!"}, room=request.sid)
                return
            leave_room(conversation_id)

        @self.socketio.on("send_message")
        def send_message(data):
            """Client sends a message to a conversation"""
            user_id = connected_users.get(request.sid)
            conversation_id = data.get("conversation_id")
            message = data.get("message")

            if not user_id:
                emit("auth_error", {"error": "User not authenticated!"}, room=request.sid)
                return
            
            if not conversation_id:
                emit("error", {"error": "Missing conversation id!"}, room=request.sid)
                return
            
            if not self.service.is_user_in_conversation(user_id, conversation_id):
                emit("error", {"error": "User is not part of conversation!"}, room=request.sid)
                return

            try:
                message = self.service.add_message(conversation_id, user_id, message)
                message_dto = MessageDTO.from_message(message).__dict__
                emit("new_message", message_dto, room=conversation_id)
            except ValueError as e:
                emit("error", {"error": str(e)}, room=request.sid)
            except Exception as e:
                print(f"[Socket Error] send message: {e}")
                emit("error", {"error": "Internal server error"}, room=request.sid)

        # @self.socketio.on("typing")
        # def typing(data):
        #     """Typing indicator"""
        #     conversation_id = data["conversation_id"]
        #     # emit("typing", ..., room=conversation_id, include_self=False)
        #     pass

