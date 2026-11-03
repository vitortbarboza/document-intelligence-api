from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = {"sqlite_autoincrement": True}

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
    )

    filename: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    page_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    extracted_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
