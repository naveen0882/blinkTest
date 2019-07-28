import unittest
from unittest import mock

from kayles.models import (
    Game,
    Row,
    Tournament,
)
from kayles import exceptions


class GameTest(unittest.TestCase):
    def setUp(self):
        self.p1 = 'player1'
        self.p2 = 'player2'

    def test_init(self):
        game = Game(self.p1, self.p2)
        self.assertEqual(game.player1, self.p1)
        self.assertEqual(game.player2, self.p2)
        self.assertEqual(len(game.row.pins), game.PINS)

    def test_move_fail(self):
        game = Game(self.p1, self.p2)

        with self.assertRaises(exceptions.InvalidTurnException) as context:
            game.move(self.p2, 0)

    def test_move_success(self):
        tests = [
            {
                'name': 'pin2_none',
                'pin1': 0,
                'pin2': None,
            },
            {
                'name': 'pin2_set',
                'pin1': 0,
                'pin2': 1,
            },
        ]
        game = Game(self.p1, self.p2)

        for test in tests:
            with self.subTest(test['name']):
                with mock.patch.object(Row, 'knockdown') as knockdown, \
                    mock.patch.object(Game, 'update_turn') as update_turn:
                        game.move(self.p1, test['pin1'], test['pin2'])

                        self.assertEqual(knockdown.call_count, 1)
                        knockdown.assert_called_with(test['pin1'], test['pin2'])

                        self.assertEqual(update_turn.call_count, 1)
                        update_turn.assert_called_with()

    def test_update_turn_not_expired(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Game, 'is_ended', return_value=False):
            # see that turn goes to the other player
            self.assertEqual(game.turn, self.p1)
            game.update_turn()
            self.assertEqual(game.turn, self.p2)

            # turn goes back to original player
            game.update_turn()
            self.assertEqual(game.turn, self.p1)

    def test_update_turn_expired(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Game, 'is_ended', return_value=True):
            # see that turn does not rotate players
            self.assertEqual(game.turn, self.p1)
            game.update_turn()
            self.assertEqual(game.turn, self.p1)

    def test_is_ended_true(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Row, 'get_pins_left', return_value=0):
            self.assertTrue(game.is_ended())

    def test_is_ended_false(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Row, 'get_pins_left', return_value=1):
            self.assertFalse(game.is_ended())

    def test_winner_none(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Game, 'is_ended', return_value=False):
            self.assertIsNone(game.winner)

    def test_winner_set(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Game, 'is_ended', return_value=True):
            self.assertEqual(game.winner, game.turn)

    def test_loser_none(self):
        game = Game(self.p1, self.p2)

        with mock.patch.object(Game, 'is_ended', return_value=False):
            self.assertIsNone(game.loser)

    def test_loser_p2(self):
        game = Game(self.p1, self.p2)
        game.turn = self.p1

        with mock.patch.object(Game, 'is_ended', return_value=True):
            self.assertEqual(game.loser, self.p2)

    def test_loser_p1(self):
        game = Game(self.p1, self.p2)
        game.turn = self.p2

        with mock.patch.object(Game, 'is_ended', return_value=True):
            self.assertEqual(game.loser, self.p1)

    def test_str(self):
        game = Game(self.p1, self.p2)
        game.row = [True, False, True]
        self.assertEqual(game.__str__(), game.row.__str__())


class RowTest(unittest.TestCase):
    def test_init(self):
        tests = [
            {
                'name': 'one',
                'length': 1,
                'expected': 1,
            },
            {
                'name': 'ten',
                'length': 10,
                'expected': 10,
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                row = Row(test['length'])
                self.assertEqual(len(row.pins), test['expected'])

    def test_get_pins_left(self):
        tests = [
            {
                'name': 'three',
                'pins': [True, True, True],
                'expected': 3,
            },
            {
                'name': 'two-1',
                'pins': [True, True, False],
                'expected': 2,
            },
            {
                'name': 'two-2',
                'pins': [True, False, True],
                'expected': 2,
            },
            {
                'name': 'two-3',
                'pins': [False, True, True],
                'expected': 2,
            },
            {
                'name': 'one-1',
                'pins': [True, False, False],
                'expected': 1,
            },
            {
                'name': 'one-2',
                'pins': [False, True, False],
                'expected': 1,
            },
            {
                'name': 'one-3',
                'pins': [False, False, True],
                'expected': 1,
            },
            {
                'name': 'zero',
                'pins': [False, False, False],
                'expected': 0,
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                row = Row(len(test['pins']))
                row.pins = test['pins']
                self.assertEqual(row.get_pins_left(), test['expected'])

    def test_knockdown_exception(self):
        tests = [
            {
                'name': 'pin1-out-of-range_pin2-none',
                'pins': [True, True, True],
                'pin1': 4,
                'pin2': None,
            },
            {
                'name': 'pin2-out-of-range',
                'pins': [True, True, True],
                'pin1': 1,
                'pin2': 4,
            },
            {
                'name': 'pin1-false',
                'pins': [True, False, True],
                'pin1': 1,
                'pin2': 0,
            },
            {
                'name': 'pin2-false',
                'pins': [True, False, True],
                'pin1': 0,
                'pin2': 1,
            },
            {
                'name': 'pins-out-of-range',
                'pins': [True, True, True],
                'pin1': 0,
                'pin2': 2,
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                row = Row(len(test['pins']))
                row.pins = test['pins']

                with self.assertRaises(exceptions.InvalidMoveException) as context:
                    row.knockdown(test['pin1'], test['pin2'])

    def test_knockdown_success(self):
        tests = [
            {
                'name': 'pin1-0',
                'pins': [True, True, True],
                'pin1': 0,
                'pin2': None,
                'expected': [False, True, True]
            },
            {
                'name': 'pin1-1',
                'pins': [True, True, True],
                'pin1': 1,
                'pin2': None,
                'expected': [True, False, True]
            },
            {
                'name': 'pin1-2',
                'pins': [True, True, True],
                'pin1': 2,
                'pin2': None,
                'expected': [True, True, False]
            },
            {
                'name': 'pin1--0-pin2-1',
                'pins': [True, True, True],
                'pin1': 0,
                'pin2': 1,
                'expected': [False, False, True]
            },
            {
                'name': 'pin1-1-pin2-2',
                'pins': [True, True, True],
                'pin1': 1,
                'pin2': 2,
                'expected': [True, False, False]
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                row = Row(len(test['pins']))
                row.pins = test['pins']
                row.knockdown(test['pin1'], test['pin2'])
                self.assertEqual(row.pins, test['expected'])

    def test_str(self):
        row = Row(3)
        self.assertEqual(row.__str__(), '!!!')

        row.pins = [True, False, True]
        self.assertEqual(row.__str__(), '!x!')


class TournamentTest(unittest.TestCase):
    def test_init(self):
        tests = [
            {
                'name': 'players-none',
                'players': None,
                'expected': {},
            },
            {
                'name': 'players-set',
                'players': ['p1', 'p2'],
                'expected': {
                    'p1': True,
                    'p2': True,
                },
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                tournament = Tournament(players=test['players'])
                self.assertEqual(tournament.players, test['expected'])

    def test_winner(self):
        tests = [
            {
                'name': 'players-empty',
                'players': {},
                'expected': None,
            },
            {
                'name': 'players-set',
                'players': {'p1': True, 'p2': True},
                'expected': None,
            },
            {
                'name': 'players-mixed',
                'players': {'p1': False, 'p2': True, 'p3': True},
                'expected': None,
            },
            {
                'name': 'players-winner',
                'players': {'p1': False, 'p2': False, 'p3': True},
                'expected': 'p3',
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                tournament = Tournament()
                tournament.players = test['players']
                self.assertEqual(tournament.winner, test['expected'])

    def test_players_left(self):
        tests = [
            {
                'name': 'players-empty',
                'players': {},
                'expected': 0,
            },
            {
                'name': 'players-set',
                'players': {'p1': True, 'p2': True},
                'expected': 2,
            },
            {
                'name': 'players-mixed',
                'players': {'p1': False, 'p2': True},
                'expected': 1,
            },
            {
                'name': 'players-false',
                'players': {'p1': False, 'p2': False},
                'expected': 0,
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                tournament = Tournament()
                tournament.players = test['players']
                self.assertEqual(tournament.players_left, test['expected'])

    def test_get_players(self):
        tests = [
            {
                'name': 'players-empty',
                'players': {},
                'active': None,
                'expected': [],
            },
            {
                'name': 'players-all',
                'players': {'p1': True, 'p2': False, 'p3': False},
                'active': None,
                'expected': ['p1', 'p2', 'p3'],
            },
            {
                'name': 'players-active',
                'players': {'p1': True, 'p2': False, 'p3': True},
                'active': True,
                'expected': ['p1', 'p3'],
            },
            {
                'name': 'players-removed',
                'players': {'p1': True, 'p2': False, 'p3': True},
                'active': False,
                'expected': ['p2'],
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                tournament = Tournament()
                tournament.players = test['players']
                players = tournament.get_players(test['active'])

                self.assertEqual(len(players), len(test['expected']))
                for p in players:
                    self.assertIn(p, test['expected'])

    def test_add_player_success(self):
        tournament = Tournament()
        tournament.add_player('p1')
        self.assertEqual(tournament.players, {'p1': True})

        tournament.add_player('p2')
        self.assertEqual(tournament.players, {'p1': True, 'p2': True})

    def test_add_player_duplicate(self):
        tournament = Tournament()
        tournament.add_player('p1')
        self.assertEqual(tournament.players, {'p1': True})

        with self.assertRaises(exceptions.DuplicatePlayer) as context:
            tournament.add_player('p1')
            self.assertEqual(tournament.players, {'p1': True})

    def test_remove_player_success(self):
        tournament = Tournament(players=['p1', 'p2', 'p3'])
        tournament.remove_player('p2')
        self.assertEqual(tournament.players, {'p1': True, 'p2': False, 'p3': True})

        tournament.remove_player('p3')
        self.assertEqual(tournament.players, {'p1': True, 'p2': False, 'p3': False})

    def test_remove_player_winner(self):
        tournament = Tournament(players=['p1', 'p2', 'p3'])
        tournament.remove_player('p1')
        tournament.remove_player('p2')

        with self.assertRaises(exceptions.InvalidPlayer) as context:
            tournament.remove_player('p3')
            self.assertEqual(tournament.players, {'p1': False, 'p2': False, 'p3': True})

    def test_remove_player_notfound(self):
        tournament = Tournament(players=['p1', 'p2', 'p3'])

        with self.assertRaises(exceptions.PlayerNotFound) as context:
            tournament.remove_player('p4')
            self.assertEqual(tournament.players, {'p1': True, 'p2': True, 'p3': True})

    def test_remove_player_invalid(self):
        tournament = Tournament(players=['p1', 'p2', 'p3'])
        tournament.remove_player('p2')

        with self.assertRaises(exceptions.InvalidPlayer) as context:
            tournament.remove_player('p2')
            self.assertEqual(tournament.players, {'p1': True, 'p2': False, 'p3': True})
