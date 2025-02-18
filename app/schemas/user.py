from typing import List

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    id: int
    name: str


class UserProfile(UserBase):
    followers: List[UserBase] = Field(default_factory=list)
    following: List[UserBase] = Field(default_factory=list)


class UserResponse(BaseModel):
    result: bool
    user: UserProfile
