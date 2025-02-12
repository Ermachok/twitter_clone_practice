from pydantic import BaseModel, Field
from typing import List


class UserBase(BaseModel):
    id: int
    name: str


class UserProfile(UserBase):
    followers: List[UserBase] = Field(default_factory=lambda: [])
    following: List[UserBase] = Field(default_factory=lambda: [])


class UserResponse(BaseModel):
    result: bool
    user: UserProfile
