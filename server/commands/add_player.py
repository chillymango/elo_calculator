import argparse
import requests

from server.models.dto.player import AddPlayer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="+")
    parser.add_argument("--host", default="http://localhost:8000")
    args = parser.parse_args()

    name = ' '.join(word.capitalize() for word in args.name)

    add_player = AddPlayer(name=name)
    resp = requests.post(f"{args.host}/add_player", json=add_player.dict())
    resp.raise_for_status()
    print(f"Successfully added player {name}")


if __name__ == "__main__":
    main()
