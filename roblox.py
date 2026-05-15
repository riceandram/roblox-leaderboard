import requests

EXPLORE_URL = "https://apis.roblox.com/explore-api/v1/get-sorts?sessionId=0"
GAMES_DETAIL_URL = "https://games.roblox.com/v1/games"
GAMES_VOTES_URL = "https://games.roblox.com/v1/games/votes"
THUMBS_BASE = "https://thumbnails.roblox.com/v1/games/icons"
CCU_SORT_ID = "CCU_Based_V1"
MAX_GAMES = 100
BATCH_SIZE = 50


def _batched_get(url, ids, extra_params, timeout=10):
    results = []
    for i in range(0, len(ids), BATCH_SIZE):
        chunk = ids[i:i + BATCH_SIZE]
        resp = requests.get(url, params={"universeIds": ",".join(str(x) for x in chunk), **extra_params}, timeout=timeout)
        resp.raise_for_status()
        results.extend(resp.json().get("data", []))
    return results


def build_games_data(games, thumbs):
    thumb_map = {t["targetId"]: t["imageUrl"] for t in thumbs}
    result = [
        {
            "universeId": g["universeId"],
            "name": g["name"],
            "playerCount": g["playerCount"],
            "creatorName": g["creatorName"],
            "thumbnailUrl": thumb_map.get(g["universeId"]),
            "upVotes": g.get("upVotes", 0),
        }
        for g in games
    ]
    return sorted(result, key=lambda g: g["playerCount"], reverse=True)


def fetch_top_games():
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

    explore_games = sorted(explore_games, key=lambda g: g["playerCount"], reverse=True)[:MAX_GAMES]
    ids = [g["universeId"] for g in explore_games]

    details = _batched_get(GAMES_DETAIL_URL, ids, {})
    creator_map = {g["id"]: g.get("creator", {}).get("name", "Unknown") for g in details}

    votes = _batched_get(GAMES_VOTES_URL, ids, {})
    upvotes_map = {g["id"]: g.get("upVotes", 0) for g in votes}

    games_with_creator = [
        {**g, "creatorName": creator_map.get(g["universeId"], "Unknown"), "upVotes": upvotes_map.get(g["universeId"], 0)}
        for g in explore_games
    ]

    thumbs = _batched_get(THUMBS_BASE, ids, {"size": "150x150", "format": "Png", "isCircular": "false"})

    return build_games_data(games_with_creator, thumbs)
