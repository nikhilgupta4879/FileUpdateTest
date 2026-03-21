from pydantic import BaseModel
from datetime import datetime


class GroupCreate(BaseModel):
    name: str
    is_public: bool = True


class GroupPublic(BaseModel):
    id: str
    name: str
    owner_id: str
    is_public: bool
    member_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class GroupSearch(BaseModel):
    query: str


class JoinGroupRequest(BaseModel):
    group_id: str
