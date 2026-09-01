from pydantic import BaseModel, Field


class GroupCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=128
    )

    group_id: str | None = Field(
        default=None,
        max_length=128
    )

    robot_id: int | None = None

    ai_enabled: bool = True

    game_enabled: bool = True

    social_enabled: bool = False

    love_enabled: bool = False

    marriage_enabled: bool = False

    baby_enabled: bool = False

    welcome_enabled: bool = False

    welcome_text: str | None = None

    system_prompt: str | None = None


class GroupUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        max_length=128
    )

    group_id: str | None = Field(
        default=None,
        max_length=128
    )

    robot_id: int | None = None

    ai_enabled: bool | None = None

    game_enabled: bool | None = None

    social_enabled: bool | None = None

    love_enabled: bool | None = None

    marriage_enabled: bool | None = None

    baby_enabled: bool | None = None

    welcome_enabled: bool | None = None

    welcome_text: str | None = None

    system_prompt: str | None = None


class GroupResponse(BaseModel):

    id: int

    name: str | None = None

    group_id: str | None = None

    robot_id: int | None = None

    ai_enabled: bool = False

    game_enabled: bool = False

    social_enabled: bool = False

    love_enabled: bool = False

    marriage_enabled: bool = False

    baby_enabled: bool = False

    welcome_enabled: bool = False

    welcome_text: str | None = None

    system_prompt: str | None = None
