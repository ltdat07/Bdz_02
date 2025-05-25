import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    LargeBinary,
    create_engine,
    select,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/file_storage")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    hash = Column(String, nullable=False, unique=True, index=True)
    location = Column(String, nullable=False)


def init_db():
    """Вызвать при старте сервиса, чтобы создать таблицы (если их нет)."""
    Base.metadata.create_all(bind=engine)


def insert_file(name: str, file_hash: str, location: str) -> FileMetadata:
    """
    Вставляет запись о файле и возвращает её.
    Если файл с таким hash уже есть, бросает IntegrityError.
    """
    db = SessionLocal()
    try:
        file = FileMetadata(name=name, hash=file_hash, location=location)
        db.add(file)
        db.commit()
        db.refresh(file)
        return file
    finally:
        db.close()


def get_file_by_hash(file_hash: str) -> FileMetadata | None:
    db = SessionLocal()
    try:
        stmt = select(FileMetadata).where(FileMetadata.hash == file_hash)
        result = db.execute(stmt).scalar_one_or_none()
        return result
    finally:
        db.close()


def get_file_by_id(file_id: int) -> FileMetadata | None:
    db = SessionLocal()
    try:
        stmt = select(FileMetadata).where(FileMetadata.id == file_id)
        result = db.execute(stmt).scalar_one_or_none()
        return result
    finally:
        db.close()
