from datetime import datetime

from pydantic import BaseModel


class RelationshipRequestCreate(BaseModel):

    sender_user_id: int
    receiver_user_id: int

    message: str | None = None


class RelationshipRequestHandle(BaseModel):

    user_id: int


class RelationshipRequestResponse(BaseModel):

    id: int

    request_type: str

    sender_user_id: int
    receiver_user_id: int

    status: str

    message: str | None = None

    created_at: datetime | None = None
    handled_at: datetime | None = None

    class Config:
        from_attributes = True
