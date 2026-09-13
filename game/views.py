from django.shortcuts import render


def game(request, game_id):
    return render(request, "game/game.html", {"game_id": game_id})
