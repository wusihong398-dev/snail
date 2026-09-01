from datetime import datetime

from pydantic import BaseModel


class RelationshipResponse(BaseModel):

    id: int

    user_id_a: int
    user_id_b: int

    intimacy: int

    relationship_status: str

    love_started_at: datetime | None = None
    married_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class RelationshipActionRequest(BaseModel):

    user_id_a: int
    user_id_b: int
