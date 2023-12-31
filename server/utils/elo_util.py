

def calculate_elo(winner_elo: float, loser_elo: float, k: int = 128):
    """Calculate the new Elo ratings for the winner and loser."""
    prob_winner = 1 / (1 + 10 ** ((loser_elo - winner_elo) / 400))
    prob_loser = 1 - prob_winner

    new_winner_elo = winner_elo + k * (1 - prob_winner)
    new_loser_elo = loser_elo + k * (0 - prob_loser)

    return round(new_winner_elo), round(new_loser_elo)
