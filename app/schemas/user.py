from typing import List

from pydantic import BaseModel


class UserBase(BaseModel):
    id: int
    name: str


class UserProfile(UserBase):
    followers: List[UserBase]
    following: List[UserBase]


class UserResponse(BaseModel):
    result: bool
    user: UserProfile
