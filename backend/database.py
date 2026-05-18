import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:dhruva1212@localhost/govai"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,        # reconnect on stale connections
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

try:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ DATABASE CONNECTED SUCCESSFULLY")
except Exception as e:
    print(f"❌ DATABASE CONNECTION ERROR: {e}")
