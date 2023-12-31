from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from server.core.guid import GUID
from server.models.orm.base import BaseModel
from server.models.orm.player import Player


class Match(BaseModel):
    __tablename__ = "matches"

    created_at = sa.Column(sa.DateTime, default=datetime.utcnow, nullable=False)
    winner_id = sa.Column(GUID(), ForeignKey("players.uuid"), nullable=False, index=True)
    loser_id = sa.Column(GUID(), ForeignKey("players.uuid"), nullable=False, index=True)

    winner = relationship(Player, back_populates="won_matches", foreign_keys=[winner_id])
    loser = relationship(Player, back_populates="lost_matches", foreign_keys=[loser_id])
