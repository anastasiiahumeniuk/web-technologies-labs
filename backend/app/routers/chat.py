from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List

router = APIRouter(prefix="/ws")


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict) -> None:
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except RuntimeError:
                self.disconnect(connection)


manager = ConnectionManager()


def build_assistant_reply(text: str) -> str:
    lower_text = text.lower()

    if "привіт" in lower_text or "hello" in lower_text or "hi" in lower_text:
        return "Привіт! Я тут, щоб допомогти з підбором фільму чи відповідями на питання. Запропонуй тему."

    if "фільм" in lower_text or "кіно" in lower_text or "жанр" in lower_text:
        return "Спробуй уточнити жанр або настрій — я пораджу фільм для перегляду."

    if "що подивитися" in lower_text or "рекомендуєш" in lower_text:
        return "Оберіть, будь ласка, жанр чи настрій, і я одразу підкажу хорошу стрічку."

    return "Цікаве питання! Напиши ще трохи деталей, і я постараюся відповісти чіткіше."


@router.websocket("/chat")
async def websocket_chat(websocket: WebSocket):
    await manager.connect(websocket)
    await manager.broadcast({
        "sender": "system",
        "message": "Новий користувач підключився до живого чату. Напишіть повідомлення, щоб почати обмін."
    })

    try:
        while True:
            text = await websocket.receive_text()
            await manager.broadcast({"sender": "user", "message": text})
            reply = build_assistant_reply(text)
            await manager.broadcast({"sender": "assistant", "message": reply})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({
            "sender": "system",
            "message": "Користувач вийшов із чату."
        })
