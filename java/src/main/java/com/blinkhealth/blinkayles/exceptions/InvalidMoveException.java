package com.blinkhealth.blinkayles.exceptions;

import com.blinkhealth.blinkayles.exceptions.GameException;

public class InvalidMoveException extends GameException {
    public InvalidMoveException() {
        super();
    }

    public InvalidMoveException(String message) {
        super(message);
    }
}
