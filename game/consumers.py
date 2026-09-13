import json
from channels.generic.websocket import AsyncWebsocketConsumer


games = {}


class TicTacToeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.room_group_name = f"game_{self.game_id}"

        if self.game_id not in games:
            games[self.game_id] = {
                "board": [""] * 9,
                "players": {},
                "turn": "X",
                "winner": None,
                "finished": False,
            }

        self.game = games[self.game_id]

        if len(self.game["players"]) >= 2:
            await self.close()
            return

        if "X" not in self.game["players"]:
            self.symbol = "X"
        else:
            self.symbol = "O"

        self.game["players"][self.symbol] = self.channel_name

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        await self.send_game_state()

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "player.update",
                "players": len(self.game["players"])
            }
        )

    async def disconnect(self, code):
        if not hasattr(self, "game"):
            return

        if not hasattr(self, "symbol"):
            return

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        if self.game["players"].get(self.symbol) == self.channel_name:
            del self.game["players"][self.symbol]

        if self.game["players"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "player.update",
                    "players": len(self.game["players"])
                }
            )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if data.get("type") != "move":
            return

        if self.game["finished"]:
            return

        if len(self.game["players"]) < 2:
            return

        if self.game["turn"] != self.symbol:
            return

        position = data.get("position")

        if not isinstance(position, int):
            return

        if position < 0 or position > 8:
            return

        if self.game["board"][position] != "":
            return

        self.game["board"][position] = self.symbol

        winner = self.check_winner()

        if winner:
            self.game["winner"] = winner
            self.game["finished"] = True
        elif "" not in self.game["board"]:
            self.game["winner"] = "draw"
            self.game["finished"] = True
        else:
            if self.symbol == "X":
                self.game["turn"] = "O"
            else:
                self.game["turn"] = "X"

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game.update",
                "board": self.game["board"],
                "turn": self.game["turn"],
                "winner": self.game["winner"],
                "finished": self.game["finished"],
                "players": len(self.game["players"]),
            }
        )

    async def send_game_state(self):
        await self.send(
            text_data=json.dumps(
                {
                    "reason": "game_state",
                    "board": self.game["board"],
                    "turn": self.game["turn"],
                    "winner": self.game["winner"],
                    "finished": self.game["finished"],
                    "players": len(self.game["players"]),
                    "your_symbol": self.symbol,
                }
            )
        )

    async def game_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "reason": "game_state",
                    "board": event["board"],
                    "turn": event["turn"],
                    "winner": event["winner"],
                    "finished": event["finished"],
                    "players": event["players"],
                    "your_symbol": self.symbol,
                }
            )
        )

    async def player_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "reason": "players",
                    "players": event["players"]
                }
            )
        )

    def check_winner(self):
        board = self.game["board"]
        winner_combinations = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),

            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),

            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in winner_combinations:
            if board[a] and board[a] == board[b] and board[a] == board[c]:
                return board[a]

        return None
