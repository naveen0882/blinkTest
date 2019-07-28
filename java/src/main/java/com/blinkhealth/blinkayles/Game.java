package com.blinkhealth.blinkayles;

import com.blinkhealth.blinkayles.exceptions.InvalidMoveException;
import com.blinkhealth.blinkayles.exceptions.InvalidTurnException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Game {
    private String player1, player2;

    private Row row;
    private String turn;

    public Game(String player1, String player2, int pins) {
        row = new Row(pins);

        this.player1 = player1;
        this.player2 = player2;

        turn = player1;
    }

    public void move(String player, int pin1, int pin2) throws InvalidTurnException, InvalidMoveException {
        if (this.isEnded()) {
            throw new InvalidMoveException("Game already ended");
        }

        if (!player.equals(turn)) {
            throw new InvalidTurnException();
        }

        row.knockdown(pin1, pin2);
        update_turn();
    }

    public void move(String player, int pin1) throws InvalidTurnException, InvalidMoveException {
        if (this.isEnded()) {
            throw new InvalidMoveException("Game already ended");
        }

        if (!player.equals(turn)) {
            throw new InvalidTurnException();
        }

        row.knockdown(pin1);
        update_turn();
    }

    public void update_turn() {
        if (!isEnded()) {
            if (turn.equals(player1)) {
                turn = player2;
            } else {
                turn = player1;
            }
        }
    }

    public boolean isEnded() {
        return row.getPinsLeft() == 0;
    }

    public String getWinner() {
        if (!isEnded()) {
            return null;
        }
        return turn;
    }

    public String getLoser() {
        if (!isEnded()) {
            return null;
        }
        return turn.equals(player1) ? player2: player1;
    }

    public String toString() {
        return row.toString();
    }
}
