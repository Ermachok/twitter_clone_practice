from typing import List, Optional

from pydantic import BaseModel


class TweetCreate(BaseModel):
    tweet_data: str
    tweet_media_ids: Optional[List[int]]


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
