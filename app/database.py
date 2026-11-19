from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine, event
from app.config import DATABASE_URL

is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread" : False} if is_sqlite else {}
engine = create_engine(DATABASE_URL,connect_args=connect_args )

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if is_sqlite:
    def sqlite_lower(value):
        return value.lower() if isinstance(value, str) else value

    @event.listens_for(engine, "connect")
    def reg_lower(dbapi_connection, connection_record):
        dbapi_connection.create_function(
            "lower",
            1,
            sqlite_lower
        )