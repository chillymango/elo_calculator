from collections import defaultdict
from typing import Any

from sqlalchemy.orm.session import Session

from server.core import env
from server.models.dto.summary import Summary
from server.models.orm.match import Match
from server.models.orm.player import Player
from server.utils import elo_util


def update_cache(cache: dict[Any, Any], db: Session) -> None:
    # TODO: this currently updates the cache from scratch each time.
    # This is not necessary though as we should be able to perform an incremental update
    # to the elo scores at each point.
    # compute new win-loss and elo scores
    players = {p.name: p for p in db.query(Player).all()}
    matches = db.query(Match).order_by(Match.created_at.asc()).all()
    elo = {p: env.STARTING_ELO for p in players}
    wins = defaultdict(lambda: 0)
    loss = defaultdict(lambda: 0)
    for match in matches:
        winner: Player = match.winner
        loser: Player = match.loser
        wins[winner.name] += 1
        loss[loser.name] += 1
        # no farming noobs
        decay_factor = (wins[winner.name] + wins[loser.name] + loss[winner.name] + loss[loser.name]) // 2
        k_elo = max(16, env.ELO_K_VALUE_CEILING // decay_factor)
        print(k_elo)
        new_winner_elo, new_loser_elo = elo_util.calculate_elo(elo[winner.name], elo[loser.name], k_elo)
        elo[winner.name] = new_winner_elo
        elo[loser.name] = new_loser_elo
        print(elo)

    summary = Summary.create_from_cache(elo, wins, loss, matches)
    cache["summary_json_str"] = summary.json()
