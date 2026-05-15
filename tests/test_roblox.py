import pytest
from roblox import build_games_data


def test_build_games_data_merges_and_sorts_descending():
    games = [
        {"universeId": 1, "name": "Game A", "playerCount": 5000, "creatorName": "Dev1"},
        {"universeId": 2, "name": "Game B", "playerCount": 12000, "creatorName": "Dev2"},
    ]
    thumbs = [
        {"targetId": 1, "imageUrl": "https://img/1.png"},
        {"targetId": 2, "imageUrl": "https://img/2.png"},
    ]
    result = build_games_data(games, thumbs)
    assert len(result) == 2
    assert result[0]["playerCount"] == 12000
    assert result[0]["thumbnailUrl"] == "https://img/2.png"
    assert result[1]["playerCount"] == 5000
    assert result[1]["thumbnailUrl"] == "https://img/1.png"


def test_build_games_data_sets_none_when_no_thumbnail():
    games = [{"universeId": 1, "name": "Game A", "playerCount": 100, "creatorName": "Dev1"}]
    result = build_games_data(games, [])
    assert result[0]["thumbnailUrl"] is None
