import os
import time
from sqlalchemy import (
    Column,
    Integer,
    String,
    JSON,
    DateTime,
    create_engine,
    func,
    select,
    UniqueConstraint,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@db_file_analysis:5432/file_analysis"
)

# Настройка SQLAlchemy
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def wait_for_db(max_retries: int = 10, delay: float = 1.0):
    """Ждём, пока PostgreSQL примет соединение."""
    for attempt in range(1, max_retries + 1):
        try:
            engine.connect().close()
            print(f"Database is up (after {attempt} attempt).")
            return
        except OperationalError:
            print(f"DB not ready, retry {attempt}/{max_retries}…")
            time.sleep(delay)
    raise RuntimeError("Database did not become available in time")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = (
        UniqueConstraint("text_hash", name="uq_analysis_results_text_hash"),
    )

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, nullable=False, index=True, unique=True)
    text_hash = Column(String, nullable=False, index=True)
    paragraphs = Column(Integer, nullable=False)
    words = Column(Integer, nullable=False)
    characters = Column(Integer, nullable=False)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


def init_db():
    """
    Ждём готовности БД и создаём таблицу analysis_results,
    если её ещё нет.
    """
    wait_for_db()
    Base.metadata.create_all(bind=engine)


def insert_result(
    file_id: int,
    text_hash: str,
    paragraphs: int,
    words: int,
    characters: int,
    extra: dict | None = None
) -> AnalysisResult:
    db = SessionLocal()
    try:
        result = AnalysisResult(
            file_id=file_id,
            text_hash=text_hash,
            paragraphs=paragraphs,
            words=words,
            characters=characters,
            extra=extra or {}
        )
        db.add(result)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # Вытаскиваем уже существующий результат по текстовому хэшу
            existing = db.query(AnalysisResult).filter_by(text_hash=text_hash).one()
            return existing
        db.refresh(result)
        return result
    finally:
        db.close()



def get_result_by_file_id(file_id: int) -> AnalysisResult | None:
    db = SessionLocal()
    try:
        stmt = select(AnalysisResult).where(AnalysisResult.file_id == file_id)
        return db.execute(stmt).scalar_one_or_none()
    finally:
        db.close()


def get_result_by_text_hash(text_hash: str) -> AnalysisResult | None:
    db = SessionLocal()
    try:
        stmt = select(AnalysisResult).where(AnalysisResult.text_hash == text_hash)
        return db.execute(stmt).scalar_one_or_none()
    finally:
        db.close()
