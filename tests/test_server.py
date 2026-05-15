import pytest
from server import create_app


def make_mock_fetcher(rounds):
    call = [0]
    def fetcher():
        result = rounds[call[0]]
        call[0] += 1
        return result
    return fetcher


def test_api_games_returns_200_with_games_after_refresh():
    mock_games = [
        {"universeId": 1, "name": "Game A", "playerCount": 100,
         "creatorName": "Dev", "thumbnailUrl": None}
    ]
    app = create_app(fetcher=lambda: mock_games)
    with app.test_client() as client:
        app.config["REFRESH"]()
        res = client.get("/api/games")
        assert res.status_code == 200
        data = res.get_json()
        assert len(data["games"]) == 1
        assert data["games"][0]["trend"] == "same"
        assert data["lastUpdated"] is not None


def test_trend_up_when_player_count_increased():
    rounds = [
        [{"universeId": 1, "name": "G", "playerCount": 100, "creatorName": "D", "thumbnailUrl": None}],
        [{"universeId": 1, "name": "G", "playerCount": 200, "creatorName": "D", "thumbnailUrl": None}],
    ]
    app = create_app(fetcher=make_mock_fetcher(rounds))
    with app.test_client() as client:
        app.config["REFRESH"]()
        app.config["REFRESH"]()
        res = client.get("/api/games")
        assert res.get_json()["games"][0]["trend"] == "up"


def test_trend_down_when_player_count_decreased():
    rounds = [
        [{"universeId": 1, "name": "G", "playerCount": 500, "creatorName": "D", "thumbnailUrl": None}],
        [{"universeId": 1, "name": "G", "playerCount": 300, "creatorName": "D", "thumbnailUrl": None}],
    ]
    app = create_app(fetcher=make_mock_fetcher(rounds))
    with app.test_client() as client:
        app.config["REFRESH"]()
        app.config["REFRESH"]()
        res = client.get("/api/games")
        assert res.get_json()["games"][0]["trend"] == "down"
