class GameException(Exception): pass
class InvalidMoveException(GameException): pass
class InvalidTurnException(GameException): pass
class DuplicatePlayer(GameException): pass
class InvalidPlayer(GameException): pass
class PlayerNotFound(GameException): pass
