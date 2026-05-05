from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import random

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

    genre_suggestions = {
        ("комедія", "комедію", "комедії", "комедіями"): [
            "Кращий вибір зараз — 'День бабака'. Легко і весело.",
            "Спробуй 'Назад в майбутнє' — це класика комедії з фантастикою.",
        ],
        ("жахи", "жахів", "жахи", "страшне", "страшно"): [
            "Тоді 'Оно' або 'Сяйво' можуть стати гарним варіантом.",
            "Можу порадити 'Кишені' — якщо хочеш трилер з напругою.",
        ],
        ("драма", "драму", "драми"): [
            "'Зелена книга' чудово підійде, якщо хочеш сильну історію.",
            "Рекомендую 'Прислугу' — це глибока й емоційна драма.",
        ],
        ("романтика", "романтику", "романтичне", "романтичний"): [
            "'Перед світанком' — дуже ніжна й атмосферна історія.",
            "Спробуй 'Ла-Ла Ленд' для романтичного вечора.",
        ],
        ("екшн", "бойовик", "бойовика"): [
            "'Місія нездійсненна' — класика швидких трюків.",
            "'Джон Вік' добре підійде, якщо хочеш динаміку й бойовик.",
        ],
        ("фантастика", "фантастичне", "наукову фантастику", "sf"): [
            "'Інтерстеллар' — гарне поєднання науки й емоцій.",
            "'Матриця' — якщо хочеш щось стильне й філософське.",
        ],
    }

    mood_suggestions = {
        ("настрій", "весело", "веселий", "весела"): [
            "Може, тобі підійде легка комедія або пригодницький фільм?",
            "Пиши, який настрій сьогодні: веселий, сумний, напружений...",
        ],
        ("страшно", "жахливо", "моторошно"): [
            "Тоді шукай трилери чи жахи — 'Сяйво' або 'Оно'.",
            "Можу порадити хтивий жах з містикою.",
        ],
        ("сумно", "сумний"): [
            "Надихаюча драма може допомогти — 'Зелена книга'.",
            "Романтична історія теж підійде, якщо хочеш тепло.",
        ],
        ("пригоди", "пригодницький", "пригода"): [
            "Тоді 'Індіана Джонс' або 'Пірати Карибського моря' — саме те.",
            "Можна подивитися 'Марсіанин' — і пригоди, і наукова драма.",
        ],
    }

    if any(word in lower_text for word in ("привіт", "hello", "hi")):
        return random.choice([
            "Привіт! Я тут, щоб допомогти з підбором фільму чи відповідями на питання.",
            "Вітаю! Скажи, який жанр чи настрій тобі цікавий сьогодні.",
        ])

    for keywords, replies in genre_suggestions.items():
        if any(keyword in lower_text for keyword in keywords):
            return random.choice(replies)

    for keywords, replies in mood_suggestions.items():
        if any(keyword in lower_text for keyword in keywords):
            return random.choice(replies)

    if any(phrase in lower_text for phrase in ("що подивитися", "рекомендуєш", "по радь", "що подивитись", "що дивитись")):
        return "Пиши, будь ласка, жанр або настрій — я підлаштую відповідь під твій настрій."

    if any(phrase in lower_text for phrase in ("який фільм", "щось дивитись", "щось подивитись", "хочу дивитись", "хочу подивитись")):
        return "Напиши, який жанр ти любиш, або в якому настрої зараз."

    if any(word in lower_text for word in ("жанр", "кіно", "фільм")):
        return "Можу порадити фільм, якщо ти скажеш, що саме хочеш: смішне, страшне, романтичне чи фантастичне."

    return random.choice([
        "Цікаве питання! Напиши ще трохи деталей, і я постараюся відповісти чіткіше.",
        "Мені потрібно трохи більше інформації — напиши, який жанр чи настрій сьогодні.",
        "Я ще вчуся, але можу підтримати розмову про фільми чи жанри. Напиши тему.",
    ])


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
