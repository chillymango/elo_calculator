import sqlalchemy as sa
from sqlalchemy.orm import relationship

from server.models.orm.base import BaseModel


class Player(BaseModel):
    __tablename__ = "players"
    name = sa.Column(sa.String, nullable=False, index=True)

    won_matches = relationship("Match", back_populates="winner", foreign_keys="Match.winner_id")
    lost_matches = relationship("Match", back_populates="loser", foreign_keys="Match.loser_id")
