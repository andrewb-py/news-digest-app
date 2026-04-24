from pydantic import BaseModel
from typing import List

class TopicSelection(BaseModel):
    topic_slugs: List[str]

class UserSettingsUpdate(BaseModel):
    email_notifications: bool