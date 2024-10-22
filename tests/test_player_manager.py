import pytest

from americano.models.enums import Gender
from americano.player_manager import PlayerManager
from americano.players import Player, PlayerList


@pytest.fixture
def player_list():
    players = [
        Player(id=1, name="Alice", gender=Gender.FEMALE, games_played=2, score=100),  # noqa E501
        Player(id=2, name="Bob", gender=Gender.MALE, games_played=1, score=90),
        Player(id=3, name="Charlie", gender=Gender.MALE, games_played=3, score=110),  # noqa E501
        Player(id=4, name="Diana", gender=Gender.FEMALE, games_played=0, score=80),  # noqa E501
        Player(id=5, name="Eve", gender=Gender.FEMALE, games_played=2, score=95),  # noqa E501
        Player(id=6, name="Frank", gender=Gender.MALE, games_played=1, score=85),  # noqa E501
    ]
    return PlayerList(players=players)

@pytest.fixture
def player_manager(player_list):
    return PlayerManager(player_list)

def test_draw_players_basic(player_manager):
    drawn_players = player_manager.draw_players(4)
    assert len(drawn_players) == 4
    assert [p.name for p in drawn_players] == ["Alice", "Bob", "Frank", "Diana"]  # noqa E501

def test_draw_players_all(player_manager):
    drawn_players = player_manager.draw_players(6)
    assert len(drawn_players) == 6
    assert [p.name for p in drawn_players] == ["Charlie", "Alice", "Eve", "Bob", "Frank", "Diana"]  # noqa E501

def test_draw_players_more_than_available(player_manager):
    with pytest.raises(ValueError, match="Cannot draw more players than available"):  # noqa E501
        player_manager.draw_players(10)

def test_draw_players_mix_tournament(player_manager):
    drawn_players = player_manager.draw_players(4, mix_tournament=True)
    assert len(drawn_players) == 4
    assert [p.name for p in drawn_players] == ["Bob", "Alice", "Frank", "Diana"]  # noqa E501

def test_draw_players_mix_tournament_all(player_manager):
    drawn_players = player_manager.draw_players(6, mix_tournament=True)
    assert len(drawn_players) == 6
    assert [p.name for p in drawn_players] == ["Charlie", "Alice", "Bob", "Eve", "Frank", "Diana"]  # noqa E501

def test_draw_players_sorted_by_score(player_manager):
    drawn_players = player_manager.draw_players(4)
    assert [p.score for p in drawn_players] == [100, 90, 85, 80]

def test_draw_players_mix_tournament_sorted_by_score(player_manager):
    drawn_players = player_manager.draw_players(4, mix_tournament=True)
    assert [p.score for p in drawn_players] == [90, 100, 85, 80]

def test_draw_players_zero(player_manager):
    drawn_players = player_manager.draw_players(0)
    assert len(drawn_players) == 0

def test_draw_players_negative(player_manager):
    with pytest.raises(ValueError, match="Cannot draw a negative number of players"):  # noqa E501
        player_manager.draw_players(-1)

def test_draw_players_odd_number(player_manager):
    with pytest.raises(ValueError, match=r"Cannot draw an odd number of players \(yet\)"):  # noqa E501
        player_manager.draw_players(5)