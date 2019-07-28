import json
import unittest
from unittest import mock

from kayles.app import app
from kayles import exceptions, routes, models
from kayles.models import Game, Tournament


class GameTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.player1 = 'p1'
        self.player2 = 'p2'
        self.player3 = 'p3'

    def test_new_game(self):
        with mock.patch('kayles.routes.validate_players'):
            data = {
                'player1': self.player1,
                'player2': self.player2,
            }
            res = self.client.post('/game', data=json.dumps(data))
            self.assertEqual(res.status_code, 201)
            res_data = json.loads(res.data.decode())
            self.assertIn('message', res_data.keys())

    def test_validate_players_success(self):
        tests = [
            {
                'name': 'no-tournament',
                'player1': self.player2,
                'player2': self.player2,
                'tournament': None,
            },
            {
                'name': 'tournament',
                'player1': self.player2,
                'player2': self.player2,
                'tournament': Tournament(players=[self.player1, self.player2, self.player3]),
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                models.tournament = test['tournament']
                routes.validate_players(test['player1'], test['player2'])

    def test_validate_players_exceptions(self):
        inactive_t = Tournament(players=[self.player1, self.player2, self.player3])
        inactive_t.remove_player(self.player1)
        inactive_t.remove_player(self.player2)

        inactive_p1 = Tournament(players=[self.player1, self.player2, self.player3])
        inactive_p1.remove_player(self.player1)

        inactive_p2 = Tournament(players=[self.player1, self.player2, self.player3])
        inactive_p2.remove_player(self.player2)

        tests = [
            {
                'name': 'no-p1',
                'player1': None,
                'player2': self.player2,
                'tournament': None,
            },
            {
                'name': 'no-p2',
                'player1': self.player1,
                'player2': None,
                'tournament': None,
            },
            {
                'name': 'p1-not-in-tournament',
                'player1': 'p4',
                'player2': self.player2,
                'tournament': Tournament(players=[self.player1, self.player2, self.player3]),
            },
            {
                'name': 'p1-not-in-tournament',
                'player1': self.player1,
                'player2': self.player2,
                'tournament': inactive_t,
            },
            {
                'name': 'p1-inactive-in-tournament',
                'player1': self.player1,
                'player2': self.player2,
                'tournament': inactive_p1,
            },
            {
                'name': 'p2-inactive-in-tournament',
                'player1': self.player1,
                'player2': self.player2,
                'tournament': inactive_p2,
            },
        ]

        for test in tests:
            with self.subTest(name=test['name']):
                models.tournament = test['tournament']

                with self.assertRaises(exceptions.InvalidPlayer) as context:
                    routes.validate_players(test['player1'], test['player2'])

    def test_move_no_game(self):
        res = self.client.post('/move/{}/1'.format(self.player1))
        self.assertEqual(res.status_code, 400)
        res_data = json.loads(res.data.decode())
        self.assertIn('message', res_data)

    def test_move_game_ended(self):
        models.game = Game(self.player1, self.player2)
        models.game.row.pins = [False]

        res = self.client.post('/move/{}/0'.format(self.player1))
        self.assertEqual(res.status_code, 400)
        res_data = json.loads(res.data.decode())
        self.assertIn('message', res_data)

    def test_move(self):
        tests = [
            {
                'name': 'pin1',
                'pin1': 0,
                'pin2': None,
            },
            {
                'name': 'pin1-pin2',
                'pin1': 0,
                'pin2': 1,
            },
        ]

        for test in tests:
            with self.subTest(test['name']):
                models.game = Game(self.player1, self.player2)
                models.tournament = Tournament(players=[self.player1, self.player2, self.player3])

                with mock.patch('kayles.routes.models.game.move') as move, \
                        mock.patch('kayles.routes.get_move_message', return_value='hello'):

                    if test['pin2']:
                        res = self.client.post('/move/{}/{},{}'.format(self.player1, test['pin1'], test['pin2']))
                    else:
                        res = self.client.post('/move/{}/{}'.format(self.player1, test['pin1']))

                    self.assertEqual(move.call_count, 1)
                    move.assert_called_with(self.player1, test['pin1'], test['pin2'])

                    self.assertEqual(res.status_code, 201)
                    res_data = json.loads(res.data.decode())
                    self.assertEqual(res_data['message'], 'hello')

    def test_get_move_message(self):
        tests = [
            {
                'name': 'live-game',
                'winner': self.player1,
                'is_ended': False,
                'tournament': False,
                'expected': '!!!!!!!!!!',
            },
            {
                'name': 'game-ended-no-tourney',
                'winner': self.player1,
                'is_ended': True,
                'tournament': False,
                'expected':  self.player1 + ' is the winner!',
            },
            {
                'name': 'game-ended-no-tourney',
                'winner': self.player1,
                'is_ended': True,
                'tournament': True,
                'expected':  self.player1 + ' is the winner!',
            },
        ]

        for test in tests:
            with self.subTest(test['name']):
                game = Game(self.player1, self.player2)

                if test['tournament']:
                    tournament = Tournament(players=[self.player1, self.player2, self.player3])
                else:
                    tournament = None

                with mock.patch.object(Game, 'is_ended', return_value=test['is_ended']), \
                        mock.patch.object(Game, 'winner') as winner, \
                        mock.patch.object(Tournament, 'remove_player') as remove_player:

                    winner.__get__ = mock.Mock(return_value=self.player1)
                    message = routes.get_move_message(game, tournament)
                    self.assertEqual(message, test['expected'])

                    if test['tournament']:
                        self.assertEqual(remove_player.call_count, 1)
                    else:
                        self.assertEqual(remove_player.call_count, 0)

    def test_get_tournament_none(self):
        models.tournament = None
        res = self.client.get('/tournament')
        self.assertEqual(res.status_code, 404)
        res_data = json.loads(res.data.decode())
        self.assertIn('message', res_data)

    def test_get_tournament(self):
        res = self.client.get('/tournament')
        models.tournament = Tournament()
        data = {
            'hello': 'world',
        }

        with mock.patch('kayles.routes.tournament_data', return_value=data) as tournament_data:
            res = self.client.get('/tournament')
            self.assertEqual(res.status_code, 200)
            res_data = json.loads(res.data.decode())
            self.assertEqual(res_data, data)

            self.assertEqual(tournament_data.call_count, 1)
            tournament_data.assert_called_with(models.tournament)

    def test_get_tournament_data(self):
        tournament = Tournament(players=[self.player1, self.player2, self.player3])

        data = routes.tournament_data(tournament)
        self.assertEqual(len(data['players']['active']), 3)
        self.assertEqual(len(data['players']['removed']), 0)
        self.assertEqual(data['players']['removed'], [])
        self.assertNotIn('winner', data)

        tournament.remove_player(self.player1)
        data = routes.tournament_data(tournament)
        self.assertEqual(len(data['players']['active']), 2)
        self.assertEqual(len(data['players']['removed']), 1)
        self.assertEqual(data['players']['removed'], [self.player1])
        self.assertIn(self.player2, data['players']['active'])
        self.assertIn(self.player3, data['players']['active'])
        self.assertNotIn('winner', data)

        tournament.remove_player(self.player2)
        data = routes.tournament_data(tournament)
        self.assertEqual(len(data['players']['active']), 1)
        self.assertEqual(len(data['players']['removed']), 2)
        self.assertEqual(data['players']['active'], [self.player3])
        self.assertIn(self.player1, data['players']['removed'])
        self.assertIn(self.player2, data['players']['removed'])
        self.assertIn('winner', data)
        self.assertEqual(data['winner'], self.player3)

    def test_new_tournament_no_players(self):
        res = self.client.post('/tournament')
        self.assertEqual(res.status_code, 400)

    def test_new_tournament_two_players(self):
        data = {'players': [self.player1, self.player2]}
        res = self.client.post('/tournament', data=json.dumps(data))
        self.assertEqual(res.status_code, 400)

    def test_new_tournament_three_players(self):
        data = {'players': [self.player1, self.player2, self.player3]}
        res = self.client.post('/tournament', data=json.dumps(data))
        self.assertEqual(res.status_code, 201)
        res_data = json.loads(res.data.decode())
        self.assertEqual(len(res_data['players']['active']), 3)
        self.assertEqual(len(res_data['players']['removed']), 0)
        self.assertNotIn('winner', res_data)

    def test_remove_player_no_tourney(self):
        models.tournament = None
        res = self.client.delete('/tournament/players/{}'.format(self.player1))
        self.assertEqual(res.status_code, 400)

    def test_remove_player(self):
        models.tournament = Tournament(players=[self.player1, self.player2, self.player3])

        with mock.patch('kayles.routes.models.tournament.remove_player') as remove_player:
            res = self.client.delete('/tournament/players/{}'.format(self.player1))
            self.assertEqual(res.status_code, 201)

            self.assertEqual(remove_player.call_count, 1)
            remove_player.assert_called_with(self.player1)
