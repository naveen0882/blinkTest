package com.blinkhealth.blinkayles;

import com.blinkhealth.blinkayles.exceptions.DuplicatePlayerException;
import com.blinkhealth.blinkayles.exceptions.InvalidGameException;
import com.blinkhealth.blinkayles.exceptions.InvalidPlayerException;
import com.blinkhealth.blinkayles.exceptions.PlayerNotFoundException;

import java.util.*;
import java.util.stream.Collectors;

public class Tournament {
    public Map<String, Boolean> players;

    public List<Game> rounds;

    public int pins;

    public Tournament(List<String> players, int pins) throws DuplicatePlayerException {
        this.players = new HashMap<>(players.size());
        for (String player: players) {
            this.addPlayer(player);
        }
        this.rounds = new ArrayList<>(players.size() - 1);
        this.pins = pins;
    }

    public int getPins() {
        return pins;
    }

    public void addNewGame(Game game) throws InvalidGameException {
        if (this.isEnded()) {
            throw new InvalidGameException("Tournament already ended");
        }

        this.rounds.add(game);
    }

    public boolean isInProgress() {
        return this.rounds.stream().anyMatch(Objects::nonNull);
    }

    public boolean isEnded() {
        return getWinner() != null;
    }

    public String getWinner() {
        if (this.getPlayersLeft() != 1) {
            return null;
        }
        return this.getPlayers(true).iterator().next();
    }

    public int getPlayersLeft() {
        return getPlayers(true).size();
    }

    public void addPlayer(String player) throws DuplicatePlayerException {
        if (players.containsKey(player)) {
            throw new DuplicatePlayerException();
        }
        players.put(player, true);
    }

    public void removePlayer(String player) throws InvalidPlayerException, PlayerNotFoundException {
        if (!players.containsKey(player)) {
            throw new PlayerNotFoundException();
        }

        if (player.equals(getWinner())) {
            throw new InvalidPlayerException("Cannot remove winner");
        } else if(!players.get(player)) {
            throw new InvalidPlayerException("Player already removed");
        }

        players.put(player, false);
    }

    public String getPreviousGameWinner() {
        if (this.isEnded()) {
            return getWinner();
        } else {
            String winner = null;
            for (Game game: this.rounds) {
                if (game != null && game.isEnded()) {
                    winner = game.getWinner();
                }
            }
            return winner;
        }
    }

    public boolean isPastLoser(String player) {
        return getPlayers(false).contains(player);
    }

    public Set<String> getPlayers(Boolean active) {
        if (active == null) {
            return players.keySet();
        } else if (active) {
            return players.entrySet().stream().filter(Map.Entry::getValue).collect(Collectors.toSet())
                    .stream().map(Map.Entry::getKey).collect(Collectors.toSet());
        } else {
            return players.entrySet().stream().filter(entry -> !entry.getValue()).collect(Collectors.toSet())
                    .stream().map(Map.Entry::getKey).collect(Collectors.toSet());
        }
    }
}
