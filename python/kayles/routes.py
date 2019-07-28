import json
import logging

from flask import (
    Blueprint,
    make_response,
    jsonify,
    request,
)
from kayles import exceptions, models
from kayles.models import (
    Game,
    Tournament,
)

logger = logging.getLogger(__name__)
routes = Blueprint('game', __name__)


@routes.errorhandler(exceptions.GameException)
def all_exception_handler(error):
    data = {
        'message': '{}: {}'.format(error.__class__.__name__, str(error))
    }
    return make_response(jsonify(data), 400)


@routes.route('/game', methods=['POST'])
def new_game():
    args = request.get_json(force=True) or {}
    player1 = args.get('player1')
    player2 = args.get('player2')

    validate_players(player1, player2)
    models.game = Game(player1, player2)

    data = {
        'message': 'new game started',
    }
    logger.info('started new game player1:%s player2:%s', models.game.player1, models.game.player2)
    return make_response(jsonify(data), 201)


def validate_players(player1, player2):
    """
    validates the players
    """
    if not player1 or not player2:
        raise exceptions.InvalidPlayer('need both player1 and player2')

    # determine if the players are active if there's a tournament
    if models.tournament:
        active_players = models.tournament.get_players(True)

        if models.tournament.winner:
            raise exceptions.InvalidPlayer('tournament is finished')

        if player1 not in active_players:
            raise exceptions.InvalidPlayer('player1 is invalid in the tournament')
        if player2 not in active_players:
            raise exceptions.InvalidPlayer('player2 is invalid in the tournament')

        logger.debug('participants pass and tournament detected')
    else:
        logger.debug('participants pass not in tournament')


@routes.route('/move/<player>/<int:pin1>', methods=['POST'], defaults={'pin2': None})
@routes.route('/move/<player>/<int:pin1>,<int:pin2>', methods=['POST'])
def move(player, pin1, pin2):
    if not models.game or models.game.is_ended():
        data = {
            'message': 'No active game. POST /game to start a new game.'
        }
        return make_response(jsonify(data), 400)

    models.game.move(player, pin1, pin2)

    data = {
        'message': get_move_message(models.game, models.tournament),
    }
    return make_response(jsonify(data), 201)


def get_move_message(game, tournament):
    """
    return the move mesage
    """
    if game.is_ended():
        logger.info('player:%s is the winner', game.winner)
        message = '{} is the winner!'.format(game.winner)

        if tournament:
            tournament.remove_player(game.loser)
            logger.info('player:%s is removed from the tournament', game.loser)
    else:
        message = game.__str__()

    return message


@routes.route('/tournament', methods=['GET'])
def get_tournament():
    if models.tournament == None:
        data = {
            'message': 'no active tournament',
        }
        return make_response(jsonify(data), 404)

    data = tournament_data(models.tournament)
    return make_response(jsonify(data), 200)


def tournament_data(tournament):
    data = {
        'players': {
            'active': tournament.get_players(True),
            'removed': tournament.get_players(False),
        }
    }

    if tournament.winner:
        data['winner'] = tournament.winner

    return data


@routes.route('/tournament', methods=['POST'])
def new_tournament():
    args = request.get_json(force=True) or {}
    players = args.get('players', [])

    # validate
    if not len(players) > 2:
        data = {
            'message': 'ERROR: need at least 3 players to start a tournament'
        }
        return make_response(jsonify(data), 400)

    models.tournament = Tournament(players=players)
    logger.info('started new tournament with %s players', len(players))

    data = tournament_data(models.tournament)
    return make_response(jsonify(data), 201)


@routes.route('/tournament/players/<player>', methods=['DELETE'])
def remove_player(player):
    if models.tournament == None:
        data = {
            'message': 'no active tournament',
        }
        return make_response(jsonify(data), 400)

    models.tournament.remove_player(player)
    logger.info('player:%s removed from tournament', player)

    data = tournament_data(models.tournament)
    return make_response(jsonify(data), 201)
