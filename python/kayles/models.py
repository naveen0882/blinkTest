from kayles import exceptions

game = None
tournament = None


class Game(object):
    PINS = 10
    player1 = ''
    player2 = ''

    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2

        self.row = Row(self.PINS)
        self.turn = self.player1

    def move(self, player, pin1, pin2=None):
        if player != self.turn:
            raise exceptions.InvalidTurnException()

        self.row.knockdown(pin1, pin2)
        self.update_turn()

    def update_turn(self):
        if self.is_ended():
            return

        if self.turn == self.player1:
            self.turn = self.player2
        else:
            self.turn = self.player1

    def is_ended(self):
        return self.row.get_pins_left() == 0

    @property
    def winner(self):
        if self.is_ended():
            return self.turn
        else:
            return None

    @property
    def loser(self):
        if not self.is_ended():
            return None

        if self.turn == self.player1:
            return self.player2
        else:
            return self.player1

    def __str__(self):
        return self.row.__str__()


class Row(object):
    def __init__(self, length):
        self.pins = [True for i in range(length)]

    def __str__(self):
        return ''.join(['!' if x else 'x' for x in self.pins])

    def knockdown(self, index1, index2=None):
        try:
            if not self.pins[index1]:
                raise exceptions.InvalidMoveException()

            self.pins[index1] = False

            if index2:
                if abs(index1 - index2) != 1:
                    raise exceptions.InvalidMoveException()

                if not self.pins[index2]:
                    raise exceptions.InvalidMoveException()

                self.pins[index2] = False
        except IndexError:
            raise exceptions.InvalidMoveException()

    def get_pins_left(self):
        return self.pins.count(True)


class Tournament(object):
    players = None

    def __init__(self, players=None):
        self.players = {}
        players = players or []

        for player in players:
            self.add_player(player)

    @property
    def players_left(self):
        """
        return the count of how many players are left
        """
        return len(self.get_players(True))

    @property
    def winner(self):
        """
        returns the winner or none
        """
        if self.players_left != 1:
            return None

        return self.get_players(True)[0]

    def add_player(self, player):
        """
        add a new player to the tournament
        """
        if player in self.players.keys():
            raise exceptions.DuplicatePlayer()

        self.players[player] = True

    def remove_player(self, player):
        """
        remove a player from the tournament: marks them as inactive
        """
        if player not in self.players.keys():
            raise exceptions.PlayerNotFound()

        if self.winner:
            raise exceptions.InvalidPlayer('cannot remove winner')
        elif self.players[player] == False:
            raise exceptions.InvalidPlayer('player already removed')

        self.players[player] = False

    def get_players(self, active):
        """
        returns the list of players

        # Params

        * active:none|bool - filters the players on their status
        """
        if active == None:
            players = [k for k, v in self.players.items()]
        else:
            players = [k for k, v in self.players.items() if v == active]

        return players
