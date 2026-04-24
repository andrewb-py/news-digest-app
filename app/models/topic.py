from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from app.models.news import news_topics

class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)

    users = relationship("UserTopic", back_populates="topic", cascade="all, delete-orphan")
    news_items = relationship("NewsItem", secondary=news_topics, back_populates="topics")

class UserTopic(Base):
    __tablename__ = "user_topics"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="user_topics")
    topic = relationship("Topic", back_populates="users")