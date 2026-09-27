import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

database_url = os.environ["DATABASE_URL"]

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


# Actually retrieve session to be able to export to other modules
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()