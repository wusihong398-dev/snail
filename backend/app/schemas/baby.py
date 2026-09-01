from datetime import datetime

from pydantic import BaseModel


class BabyRequestCreate(BaseModel):

    sender_user_id: int
    receiver_user_id: int

    baby_name: str | None = None
    baby_gender: str = "unknown"

    message: str | None = None


class BabyRequestHandle(BaseModel):

    user_id: int


class BabyRequestResponse(BaseModel):

    id: int

    sender_user_id: int
    receiver_user_id: int

    status: str

    baby_name: str | None = None
    baby_gender: str

    message: str | None = None

    created_at: datetime | None = None
    handled_at: datetime | None = None

    class Config:
        from_attributes = True


class BabyResponse(BaseModel):

    id: int

    name: str

    parent_user_id_a: int
    parent_user_id_b: int

    gender: str

    level: int
    experience: int

    happiness: int
    hunger: int
    health: int

    born_at: datetime | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True
