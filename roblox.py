import requests

GAMES_URL = "https://games.roblox.com/v1/games/list?SortType=2&MaxRows=50"
THUMBS_BASE = "https://thumbnails.roblox.com/v1/games/icons"


def build_games_data(games, thumbs):
    thumb_map = {t["targetId"]: t["imageUrl"] for t in thumbs}
    result = [
        {
            "universeId": g["universeId"],
            "name": g["name"],
            "playerCount": g["playerCount"],
            "creatorName": g["creatorName"],
            "thumbnailUrl": thumb_map.get(g["universeId"]),
        }
        for g in games
    ]
    return sorted(result, key=lambda g: g["playerCount"], reverse=True)


def fetch_top_games():
    resp = requests.get(GAMES_URL, timeout=10)
    resp.raise_for_status()
    games = resp.json().get("games", [])

    if not games:
        return []

    ids = ",".join(str(g["universeId"]) for g in games)
    thumbs_resp = requests.get(
        THUMBS_BASE,
        params={"universeIds": ids, "size": "150x150", "format": "Png", "isCircular": "false"},
        timeout=10,
    )
    thumbs_resp.raise_for_status()
    thumbs = thumbs_resp.json().get("data", [])

    return build_games_data(games, thumbs)
