import requests

EXPLORE_URL = "https://apis.roblox.com/explore-api/v1/get-sorts?sessionId=0"
GAMES_DETAIL_URL = "https://games.roblox.com/v1/games"
THUMBS_BASE = "https://thumbnails.roblox.com/v1/games/icons"
CCU_SORT_ID = "CCU_Based_V1"
MAX_GAMES = 100


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
    # Fetch CCU-sorted game list from explore API (includes playerCount)
    resp = requests.get(EXPLORE_URL, timeout=10)
    resp.raise_for_status()
    sorts = resp.json().get("sorts", [])

    explore_games = []
    for sort in sorts:
        if sort.get("id") == CCU_SORT_ID:
            explore_games = sort.get("games", [])
            break

    if not explore_games:
        return []

    # Take top MAX_GAMES by playerCount
    explore_games = sorted(explore_games, key=lambda g: g["playerCount"], reverse=True)[:MAX_GAMES]
    id_str = ",".join(str(g["universeId"]) for g in explore_games)

    # Fetch creator names from games detail API
    details_resp = requests.get(GAMES_DETAIL_URL, params={"universeIds": id_str}, timeout=10)
    details_resp.raise_for_status()
    creator_map = {
        g["id"]: g.get("creator", {}).get("name", "Unknown")
        for g in details_resp.json().get("data", [])
    }

    games_with_creator = [
        {**g, "creatorName": creator_map.get(g["universeId"], "Unknown")}
        for g in explore_games
    ]

    # Fetch thumbnails
    thumbs_resp = requests.get(
        THUMBS_BASE,
        params={"universeIds": id_str, "size": "150x150", "format": "Png", "isCircular": "false"},
        timeout=10,
    )
    thumbs_resp.raise_for_status()
    thumbs = thumbs_resp.json().get("data", [])

    return build_games_data(games_with_creator, thumbs)
