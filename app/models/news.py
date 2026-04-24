from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.sql import func
from sqlalchemy import JSON
from sqlalchemy.orm import relationship
from app.models.base import Base

# Ассоциативная таблица
news_topics = Table(
    "news_topics", Base.metadata,
    Column("news_id", ForeignKey("news_items.id", ondelete="CASCADE"), primary_key=True),
    Column("topic_id", ForeignKey("topics.id", ondelete="CASCADE"), primary_key=True)
)

class NewsItem(Base):
    __tablename__ = "news_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    original_url = Column(String(2048), nullable=False)
    source_type = Column(String(20))
    status = Column(String(20), nullable=False, default="published")
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submission_id = Column(Integer, ForeignKey("news_submissions.id", ondelete="SET NULL"), nullable=True)

    submission = relationship("NewsSubmission", back_populates="news_item", uselist=False)
    favorites = relationship("Favorite", back_populates="news_item", cascade="all, delete-orphan")
    topics = relationship("Topic", secondary=news_topics, back_populates="news_items")

class NewsSubmission(Base):
    __tablename__ = "news_submissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    url = Column(String(2048), nullable=True)
    comment = Column(Text, nullable=True)
    pdf_path = Column(String(255), nullable=True)
    llm_data = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="submissions", foreign_keys=[user_id])
    news_item = relationship("NewsItem", back_populates="submission", uselist=False)

class Favorite(Base):
    __tablename__ = "favorites"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    news_id = Column(Integer, ForeignKey("news_items.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="favorites")
    news_item = relationship("NewsItem", back_populates="favorites")