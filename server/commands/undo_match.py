import argparse
import requests

from server.models.dto.match import MatchResult


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="http://localhost:8000")
    args = parser.parse_args()

    resp = requests.post(f"{args.host}/api/undo")
    resp.raise_for_status()
    print(f"Successful undo")


if __name__ == "__main__":
    main()
