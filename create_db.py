# create_db.py
from sqlalchemy import create_engine
from database.models import Base
from config import settings

url = settings.DATABASE_URL
# For sqlite, create synchronous engine for initial schema creation
if url.startswith("sqlite:///"):
    engine = create_engine(url, echo=True)
else:
    engine = create_engine(url, echo=True)

Base.metadata.create_all(engine)
print("DB tables created")
