from pydantic import BaseModel


class FollowResponse(BaseModel):
    result: bool


class UnfollowResponse(BaseModel):
    result: bool


class GetFollowersResponse(BaseModel):
    result: bool
    followers: list


class GetFollowingResponse(BaseModel):
    result: bool
    following: list
