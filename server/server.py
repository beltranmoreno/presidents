import asyncio
import websockets
import json
from Game import Game
from Trick import Trick
from Player import Player

class GameServer:
    def __init__(self):
        self.clients = []
        self.game = Game()
        self.num_players = 0
        self.game_started = False

    async def register(self, websocket):
        self.clients.append(websocket)
        await self.notify_players()

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        await self.notify_players()

    async def notify_players(self):
        if self.clients:
            message = json.dumps({"type": "players", "count": len(self.clients)})
            await asyncio.gather(*[client.send(message) for client in self.clients])

    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            print(f"Received message: {data}")

            if data["action"] == "set_num_players":
                if len(self.clients) == 1 and not self.game_started: 
                    self.num_players = data["num_players"]
                    self.game.setup(self.num_players)
                    await self.notify_players()
                    print(f"Number of players set to {self.num_players}")

            elif data["action"] == "join":
                player_name = data["name"]
                print('Player joined:', player_name)

                if self.num_players == 0:
                    print('No players set.')
                    await websocket.send(json.dumps({"type": "error", "message": "Number of players not set yet."}))
                    return

                if len(self.game.players) < self.num_players:
                    self.game.add_player(player_name)
                    await self.notify_players()
                    print('Connected players:', len(self.game.players))
                    print('Expected players:', self.num_players)
                
                if len(self.game.players) == self.num_players:
                    print('Starting game...')
                    await self.start_game()
                # else:
                #     await websocket.send(json.dumps({"type": "error", "message": "Game is full."}))

            elif data["action"] == "play" and self.game_started:
                card_indices = data["indices"]
                player_name = data["name"]
                current_player = next(p for p in self.game.players if p.name == player_name)
                await self.game.trick.play_card(current_player, card_indices)
                await self.update_game_state()
        except Exception as e:
            print(f"Error handling message: {e}")

    async def start_game(self):
        try:
            self.game_started = True
            self.game.distribute_cards()
            self.game.trick = Trick(self.game.players)
            await self.update_game_state()
        except Exception as e:
            print(f"Error starting game: {e}")

    async def update_game_state(self):
        try:
            game_state = self.game.get_game_state()
            message = json.dumps(game_state)
            await asyncio.gather(*[client.send(message) for client in self.clients])
        except Exception as e:
            print(f"Error updating game state: {e}")

    async def handler(self, websocket, path):
        await self.register(websocket)

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.ConnectionClosed:
            print("Connection closed")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            await self.unregister(websocket)

server = GameServer()

start_server = websockets.serve(server.handler, "localhost", 6789, ping_interval=30, ping_timeout=60)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
