from django.urls import path

from .consumers import TicTacToeConsumer


websocket_urlpatterns = [
    path("ws/game/<str:game_id>/", TicTacToeConsumer.as_asgi()),
]