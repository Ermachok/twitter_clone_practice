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
    author_id: int


class TweetListResponse(BaseModel):
    result: bool
    tweets: List[TweetDetail]
