from typing import Dict, List
from fastapi import WebSocket # type: ignore

class InquiryMessagesManager:
  def __init__(self):
    self.active_connections: Dict[int, List[WebSocket]] = {}

  async def connect(self, inquiry_id: int, websocket: WebSocket):
    await websocket.accept()
    self.active_connections.setdefault(inquiry_id, []).append(websocket)

  def disconnect(self, inquiry_id: int, websocket: WebSocket):
    if inquiry_id in self.active_connections:
      self.active_connections[inquiry_id].remove(websocket)

      if not self.active_connections[inquiry_id]:
        del self.active_connections[inquiry_id]

  async def broadcast(self, message: dict):
    try:
      for connection in self.active_connections.get(message["inquiry_id"], []):
        await connection.send_json(message)
    except Exception as e:
      print(e)

inquiry_messages_manager = InquiryMessagesManager()