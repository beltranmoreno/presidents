import asyncio
import websockets
import json
from Game import Game
from Trick import Trick
from Player import Player

class GameServer:
    def __init__(self):
        self.clients = []
        self.client_to_player = {}
        self.game = Game()
        self.num_players = 0
        self.game_started = False


    async def register(self, websocket):
        self.clients.append(websocket)
        self.game.clients = self.clients
        await self.notify_players()

    async def unregister(self, websocket):
        self.clients.remove(websocket)
        player = self.client_to_player.pop(websocket, None)
        print(f"Player {player.name if player else 'Unknown'} disconnected.")
        await self.notify_players()

    async def notify_players(self):
        if self.clients:
            message = json.dumps({"type": "players", "count": len(self.clients)})
            await asyncio.gather(*[client.send(message) for client in self.clients])

    async def handle_message(self, websocket, message):
        try:
            data = json.loads(message)
            print(f"Received message from {self.client_to_player[websocket].name if websocket in self.client_to_player else 'Unknown'}: {data}")

            if data["action"] == "set_num_players":
                if len(self.clients) == 1 and not self.game_started: 
                    self.num_players = data["num_players"]
                    self.game.setup(self.num_players)
                    await self.notify_players()
                    print(f"Number of players set to {self.num_players}")

            elif data["action"] == "join":
                player_name = data["name"]
                print(f"Player {player_name} is attempting to join.")

                if self.num_players == 0:
                    print('No players set.')
                    await websocket.send(json.dumps({"type": "error", "message": "Number of players not set yet."}))
                    return

                if len(self.game.players) < self.num_players:
                    player = Player(player_name)
                    self.game.add_player(player) 
                    self.client_to_player[websocket] = player 
                    await self.notify_players()
                    print('Connected players:', len(self.game.players))
                    print('Expected players:', self.num_players)
                
                if len(self.game.players) == self.num_players:
                    print('All players joined. Starting game...')
                    await self.start_game()  

            elif data["action"] == "play" and self.game_started:
                card_indices = data["indices"]
                current_player = self.client_to_player[websocket]
                
                action, message = await self.game.trick.play_card(current_player, card_indices)
                print(f"Result of play_card: {action}, Message: {message}")

                if action == "error":
                    print(f"Error in player {current_player.name}'s move: {message}")
                    await websocket.send(json.dumps({"type": "error", "message": message}))
                else:
                    await self.update_game_state()
                    print(f"Game state updated successfully after {current_player.name}'s move.")
                    
                    if action == "end":
                        print("Game has ended.")
                        await self.end_game()
                    

            elif data["action"] == "pass" and self.game_started:
                current_player = self.client_to_player[websocket]
                print(f"Player {current_player.name} passed their turn.")
                await self.game.trick.pass_turn()
                await self.update_game_state()
                next_player = self.game.trick.get_current_player()
                if next_player and next_player != current_player:
                    print(f"Next player after pass is {next_player.name}. Notifying...")
                    await self.notify_next_player(next_player)
        
        except Exception as e:
            error_message = f"Error handling message: {str(e)}"
            print(error_message)
            await websocket.send(json.dumps({"type": "error", "message": error_message}))

    async def start_game(self):
        try:
            self.game_started = True
            self.game.distribute_cards()
            # self.game.trick = Trick(self.game.players)
            self.game.start_trick()
            await self.game.update_game_state()
        except Exception as e:
            print(f"Error starting game: {e}")

    async def update_game_state(self):
        try:
            game_state = self.game.get_game_state()
            print("Game state before serialization:", game_state)
            message = json.dumps(game_state)
            await asyncio.gather(*[client.send(message) for client in self.clients])
            print("Game state updated and sent to all clients.")
        except Exception as e:
            error_message = f"Error updating game state: {str(e)}"
            print(error_message)
            await asyncio.gather(*[client.send(json.dumps({"type": "error", "message": error_message})) for client in self.clients])
    
    async def notify_next_player(self, next_player):
        """
        Notify the next player that it is their turn.
        """
        try:
            # Find the WebSocket connection for the next player
            for websocket, player in self.client_to_player.items():
                if player.name == next_player.name:
                    print(f"[SERVER LOG] Sending 'your_turn' notification to {next_player.name}.")
                    await websocket.send(json.dumps({
                        "type": "your_turn",
                        "message": f"It's your turn, {next_player.name}!",
                        "game_state": self.game.get_game_state()
                    }))
                    print(f"[SERVER LOG] Notification sent to {next_player.name}.")
                    break

        except Exception as e:
            print(f"Error notifying next player: {e}")
            
    async def end_trick(self):
        """
        Handle the end of a trick, notify all clients, and start a new trick.
        """
        try:
            # Notify all clients that the trick has ended
            end_message = json.dumps({"type": "trick_end", "message": "The trick has ended. A new trick will start."})
            await asyncio.gather(*[client.send(end_message) for client in self.clients])

            # Reset the trick and start a new one
            self.game.trick = Trick(self.game.players)  # Start a new trick with the current players
            await self.update_game_state()
            print("A new trick has started.")
        except Exception as e:
            print(f"Error ending trick: {e}")

    async def keep_alive(self):
        """
        Periodically sends keep-alive messages to all connected clients.
        """
        while True:
            if self.clients:
                try:
                    message = json.dumps({"type": "keep_alive"})
                    await asyncio.gather(*[client.send(message) for client in self.clients])
                    print("Sent keep-alive message to all clients.")
                except Exception as e:
                    print(f"Error sending keep-alive message: {e}")

            # Sleep for 30 seconds before sending the next keep-alive message
            await asyncio.sleep(30)
    
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

start_server = websockets.serve(server.handler, "localhost", 6789, ping_interval=60, ping_timeout=120)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

