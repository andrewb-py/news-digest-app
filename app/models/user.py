from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")
    submissions = relationship("NewsSubmission", back_populates="user", cascade="all, delete-orphan", foreign_keys="NewsSubmission.user_id")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    user_topics = relationship("UserTopic", back_populates="user", cascade="all, delete-orphan")

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    email_notifications = Column(Boolean, default=True)
    
    user = relationship("User", back_populates="settings")