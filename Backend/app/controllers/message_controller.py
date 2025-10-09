from flask import Blueprint
from app.services.message_service import MessageService

class MessageController:
  def __init__(self, socketio):
    self.service = MessageService()
    self.socketio = socketio
    self.blueprint = Blueprint("messages", __name__)
    self._register_routes()
    self._register_events()

  def _register_routes(self):
    """Will contain endpoints for manual message retrieval"""
    pass

  def _register_events(self):
    """Will contain websocket endpoints for messages"""
    pass
