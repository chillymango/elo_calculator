import argparse
import requests

from server.models.dto.match import MatchResult


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--winner", nargs="+")
    parser.add_argument("--loser", nargs="+")
    parser.add_argument("--host", default="http://localhost:8000")
    args = parser.parse_args()

    winner_name = ' '.join(word.capitalize() for word in args.winner)
    loser_name = ' '.join(word.capitalize() for word in args.loser)

    match_result = MatchResult(winner=winner_name, loser=loser_name)
    resp = requests.post(f"{args.host}/match", json=match_result.dict())
    resp.raise_for_status()
    print(f"Successfully recorded {winner_name} beating {loser_name}")


if __name__ == "__main__":
    main()
