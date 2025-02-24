from pydantic import BaseModel


class LikeResponse(BaseModel):
    result: bool
    message: str


class LikeRemovedResponse(BaseModel):
    result: bool
    message: str
