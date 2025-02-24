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
    attachments: list
    author: dict
    likes: List[dict]


class TweetListResponse(BaseModel):
    result: bool
    tweets: List[TweetDetail]


class TweetDeleteResponse(BaseModel):
    result: bool


class TweetLikesList(BaseModel):
    result: int
    likes_count: int
