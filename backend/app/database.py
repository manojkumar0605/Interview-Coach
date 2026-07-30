from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine_kwargs = {}
if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def run_migrations():
    """Ensures database schema migration for new columns."""
    try:
        with engine.connect() as conn:
            # Check if grammar_rolling_avg exists in topic_scores
            if settings.DATABASE_URL.startswith("sqlite"):
                result = conn.execute(text("PRAGMA table_info(topic_scores)")).fetchall()
                col_names = [r[1] for r in result]
                if "grammar_rolling_avg" not in col_names:
                    conn.execute(text("ALTER TABLE topic_scores ADD COLUMN grammar_rolling_avg FLOAT DEFAULT 0.0"))
                    conn.commit()
    except Exception as e:
        print(f"Migration notice: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
