from pydantic import BaseModel
from typing import List


class TweetCreate(BaseModel):
    content: str


class TweetResponse(BaseModel):
    result: bool
    tweet_id: int


class TweetDetail(BaseModel):
    id: int
    content: str
    author: "UserBase"
    likes: List["UserBase"] = []
