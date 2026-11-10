"""Наполнение базы демонстрационными данными.

Запуск из корня проекта, после `alembic upgrade head`:
    python -m app.seed
В Docker:
    docker compose exec app python -m app.seed
"""
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select

from app.auth.utils import hash_password
from app.database import SessionLocal
from app.users.models import User
from app.categories.models import Category
from app.listings.models import Listing
from app.deal_requests.models import DealRequest
from app.messages.models import Message
from app.favorites.models import Favorite
from app.reports.models import Report

DEMO_PASSWORD = "DemoPass123"  # одинаковый для всех демо-аккаунтов

USERS = [("admin", "admin"), ("moderator", "moderator"),
         ("alice", "user"), ("bobby", "user"), ("carol", "user")]
CATEGORIES = ["Учебники", "Техника", "Мебель", "Одежда", "Спорт"]

# владелец, индекс категории, название, описание, состояние, режим, цена, статус
LISTINGS = [
    ("alice", 0, "Математический анализ, Фихтенгольц", "Том 1, состояние хорошее", "used", "sale", "450", "published"),
    ("alice", 0, "Конспекты по физике, 1 курс", "Рукописные, аккуратные", "used", "free", "0", "published"),
    ("alice", 1, "Калькулятор Casio fx-991", "Работает без нареканий", "used", "sale", "1200", "published"),
    ("alice", 2, "Настольная лампа", "Новая, в упаковке", "new", "exchange", None, "published"),
    ("alice", 3, "Куртка зимняя, размер M", "Носила один сезон", "used", "sale", "2500", "reserved"),
    ("alice", 4, "Скакалка", "Новая", "new", "free", "0", "completed"),
    ("alice", 1, "Наушники проводные", "Рабочие", "used", "sale", "300", "unpublished"),
    ("bobby", 0, "Python для начинающих", "Новая книга", "new", "sale", "700", "published"),
    ("bobby", 1, "Монитор 24 дюйма", "Без битых пикселей", "used", "sale", "6500", "published"),
    ("bobby", 2, "Офисный стул", "Регулируется по высоте", "used", "exchange", None, "published"),
    ("bobby", 3, "Толстовка университета", "Новая, размер L", "new", "sale", "1500", "published"),
    ("bobby", 4, "Гантели 2x5 кг", "Пара", "used", "sale", "800", "reserved"),
    ("bobby", 0, "Учебник по химии", "Отдам бесплатно", "used", "free", "0", "published"),
    ("bobby", 1, "Флешка 64 ГБ", "Новая", "new", "exchange", None, "hidden"),
    ("carol", 0, "Английский язык B1", "С ответами", "used", "sale", "350", "published"),
    ("carol", 1, "Клавиатура механическая", "Подсветка работает", "used", "sale", "2200", "published"),
    ("carol", 2, "Книжная полка", "Отдам бесплатно", "used", "free", "0", "published"),
    ("carol", 3, "Шарф вязаный", "Ручная работа", "new", "exchange", None, "published"),
    ("carol", 4, "Йога-коврик", "Почти не использовался", "used", "sale", "600", "completed"),
    ("carol", 1, "Роутер Wi-Fi", "Рабочий", "used", "sale", "900", "published"),
]

# покупатель, номер объявления (с 1), статус заявки, текст
REQUESTS = [
    ("bobby", 5, "accepted", "Здравствуйте, куртка ещё актуальна?"),
    ("carol", 5, "pending", "Готова забрать сегодня"),
    ("carol", 12, "accepted", "Беру гантели, когда удобно встретиться?"),
    ("carol", 6, "completed", "Скакалка нужна для тренировок"),
    ("bobby", 6, "cancelled", "Передумал"),
    ("alice", 19, "completed", "Коврик пригодится, спасибо"),
    ("alice", 8, "pending", "Интересует книга"),
    ("carol", 8, "pending", "Можно посмотреть?"),
    ("bobby", 1, "pending", "Нужна для экзамена"),
    ("alice", 16, "cancelled", "Нашла другую клавиатуру"),
]

# индекс заявки (с 0), отправитель, текст
MESSAGES = [
    (0, "bobby", "Подскажите, где можно встретиться?"),
    (0, "alice", "Могу у главного корпуса в 15:00"),
    (0, "bobby", "Отлично, договорились"),
    (2, "carol", "Когда вам удобно?"),
    (2, "bobby", "Завтра после пар"),
    (3, "alice", "Передала, спасибо!"),
    (5, "carol", "Забрала, всё отлично"),
]

FAVORITES = [("bobby", 1), ("bobby", 3), ("carol", 8), ("alice", 9), ("carol", 2)]

# автор, номер объявления, причина, статус, решение
REPORTS = [
    ("carol", 14, "Подозрение на мошенничество", "resolved", "Объявление скрыто: нарушение правил"),
    ("alice", 11, "Описание не соответствует товару", "pending", None),
]


def seed() -> None:
    db = SessionLocal()
    try:
        if db.execute(select(User)).first():
            print("База уже содержит данные, наполнение пропущено.")
            return

        users = {name: User(username=name, hashed_password=hash_password(DEMO_PASSWORD), role=role)
                 for name, role in USERS}
        categories = [Category(name=name) for name in CATEGORIES]
        db.add_all(list(users.values()) + categories)
        db.flush()  # после flush у объектов появляются id

        now = datetime.now(timezone.utc)
        listings = {}
        for number, (owner, cat, name, desc, cond, mode, price, status) in enumerate(LISTINGS, start=1):
            listings[number] = Listing(
                name=name, description=desc, condition=cond, mode=mode,
                price=None if price is None else Decimal(price),
                status=status,
                user_id=users[owner].id,
                category_id=categories[cat].id,
                created_at=now - timedelta(days=len(LISTINGS) - number),
            )
        db.add_all(listings.values())
        db.flush()

        requests = [DealRequest(buyer_id=users[buyer].id, listing_id=listings[number].id,
                                status=status, text=text)
                    for buyer, number, status, text in REQUESTS]
        db.add_all(requests)
        db.flush()

        for i, (idx, sender, text) in enumerate(MESSAGES):
            db.add(Message(request_id=requests[idx].id, sender_id=users[sender].id, text=text,
                           created_at=now - timedelta(minutes=len(MESSAGES) - i)))
        for user, number in FAVORITES:
            db.add(Favorite(user_id=users[user].id, listing_id=listings[number].id))
        for author, number, reason, status, resolution in REPORTS:
            db.add(Report(user_id=users[author].id, listing_id=listings[number].id,
                          reason=reason, status=status, resolution=resolution))

        db.commit()
        print(f"Готово. Пользователи: {', '.join(users)}. Пароль у всех: {DEMO_PASSWORD}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()