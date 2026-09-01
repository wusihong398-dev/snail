from sqlalchemy import (
    Column,
    Integer,
    String,
    Text
)

from app.database import Base


class GameQuestion(Base):

    __tablename__ = "game_questions"


    id = Column(
        Integer,
        primary_key=True
    )


    # 游戏类型
    # image/music/movie/number
    game_type = Column(
        String(32)
    )


    标题 = Column(
        Text
    )


    answer = Column(
        String(255)
    )


    hint = Column(
        String(255)
    )


    media_url = Column(
        String(255)
    )


    reward = Column(
        Integer,
        default=50
    )
