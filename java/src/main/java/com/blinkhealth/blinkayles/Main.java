package com.blinkhealth.blinkayles;

import static spark.Spark.*;

import com.blinkhealth.blinkayles.exceptions.*;

import org.json.JSONArray;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import spark.Request;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

public class Main {
    private final static Logger logger = LoggerFactory.getLogger(Main.class);
    private static Game currentGame;
    private static Tournament tournament;

    private static String requestInfoToString(Request request) {
        StringBuilder sb = new StringBuilder();
        sb.append(request.requestMethod());
        sb.append(" " + request.url());
        sb.append(" " + request.body());
        return sb.toString();
    }

    public static void main(String[] args) {
        before((request, response) -> {
            logger.info(requestInfoToString(request));
        });

        exception(GameException.class, (exception, request, response) -> {
            response.status(400);
            response.body(exception.getClass().getSimpleName() + ": "  + exception.getMessage());
        });

        get("/tournament", (request, response) -> {
            if (tournament == null || tournament.isEnded()) {
                return "Tournament has ended. Start a new tournament";
            } else {
                JSONObject responseObj = new JSONObject();
                responseObj.put("active", new JSONArray(tournament.getPlayers(true)));
                responseObj.put("losers", new JSONArray(tournament.getPlayers(false)));
                return responseObj;
            }
        });

        post("/tournament", (request, response) -> {
            if (tournament != null && !tournament.isEnded()) {
                throw new InvalidTournamentException("A tournament is already in progress");
            }

            JSONObject requestBody = new JSONObject(request.body());
            JSONArray players = requestBody.getJSONArray("players");
            if (players.isEmpty() || players.length() < 2) {
                throw new InvalidTournamentException("Need atleast 2 playes to start the tournament");
            }

            if (!requestBody.has("pins") || requestBody.get("pins") == null ||
                    Integer.parseInt(requestBody.get("pins").toString()) <= 0) {
                throw new InvalidTournamentException("Pins should be great than 0");
            }

            List<String> playersList = players.toList().stream().map(Object::toString).collect(Collectors.toList());

            tournament = new Tournament(playersList, Integer.parseInt(requestBody.get("pins").toString()));

            return "Tournament started! Call a new game with players";
        });

        delete("/tournament/:player", (request, response) -> {
            if (tournament == null || tournament.isEnded()) {
                throw new InvalidTournamentException("Tournament has ended. Start a new tournament");
            }

            String player = request.params("player");

            tournament.removePlayer(player);

            return String.format("Removed player %s from the tournament", player);
        });

        post("/tournament/players/:player", (request, response) -> {
            if (tournament == null || tournament.isEnded()) {
                throw new InvalidTournamentException("Tournament has ended. Start a new tournament");
            }

            String player = request.params("player");

            tournament.addPlayer(player);

            return String.format("Added player %s to the tournament", player);
        });

        post("/game", (request, response) -> {
            if (tournament == null || tournament.isEnded()) {
                throw new InvalidGameException("Tournament has ended. Start a new tournament");
            }

            if (currentGame != null && !currentGame.isEnded()) {
                throw new InvalidGameException("A game is already in progress");
            }

            JSONObject requestBody = new JSONObject(request.body());

            String player1 = requestBody.get("player1").toString();
            String player2 = requestBody.get("player2").toString();

            if (player1 == null || player2 == null || player1.equals(player2)) {
                throw new InvalidPlayerException("Not enough players to play the game");
            }

            if (tournament.isPastLoser(player1)) {
                throw new InvalidPlayerException(String.format("Player %s is a past loser. Can't start a new game " +
                        "with a loser", player1));
            } else if (tournament.isPastLoser(player2)) {
                throw new InvalidPlayerException(String.format("Player %s is a past loser. Can't start a new game " +
                        "with a loser", player2));
            }

            String previousGameWinner = tournament.getPreviousGameWinner();
            if (tournament.isInProgress() &&
                    !player1.equals(previousGameWinner) && !player2.equals(previousGameWinner)) {
                throw new InvalidPlayerException("Neither of the players is the previous game winner");
            }

            //To be fair, let's give the new player the first move
            if (previousGameWinner != null) {
                String newPlayer = player1.equals(previousGameWinner) ? player2 : player1;
                currentGame = new Game(newPlayer, previousGameWinner, tournament.getPins());
            } else {
                currentGame = new Game(player1, player2, tournament.getPins());
            }

            tournament.addNewGame(currentGame);

            String template = "Game started! The player who knocks down the last pin wins.  Players: %s %s Pins: %d";
            return String.format(template, player1, player2, tournament.getPins());
        });

        post("/move/:player/:pins", (request, response) -> {
            if (currentGame == null || currentGame.isEnded()) {
                return "No active game. Start a new game.";
            }

            String[] pins = request.params("pins").split(",");
            if (request.params("pins").lastIndexOf(",") == request.params("pins").length() - 1) {
                throw new InvalidMoveException("Pin should not be empty");
            }
            if (Arrays.stream(pins).anyMatch(String::isEmpty)) {
                throw new InvalidMoveException("Pin should not be empty");
            }
            String player = request.params("player");

            if (pins.length == 0) {
                throw new InvalidMoveException("Need at least one pin to move");
            } else if (pins.length == 1) {
                currentGame.move(player, Integer.parseInt(pins[0]));
            } else if (pins.length == 2) {
                currentGame.move(player, Integer.parseInt(pins[0]), Integer.parseInt(pins[1]));
            } else {
                throw new InvalidMoveException("Need at most two pins to move");
            }

            if (currentGame.isEnded()) {

                //Remove the player from the tournament
                tournament.removePlayer(currentGame.getLoser());

                return String.format("%s is the winner! Tournament %s", currentGame.getWinner(),
                        tournament.isEnded()? "ended": "continues");
            } else {
                return currentGame.toString();
            }
        });
    }
}


