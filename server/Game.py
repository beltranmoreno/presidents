import asyncio
from Deck import Deck
from Player import Player
from Trick import Trick
import json

class Game:
    def __init__(self):
        self.players = []
        self.num_players = 0
        self.titles = ["President", "Vice President", "Neutral", "Vice Scum", "Scum"]
        self.num_tricks = 0

    def setup(self, num_players):
        self.num_players = num_players
        self.players = []
    
    def add_player(self, player_name):
        if len(self.players) < self.num_players:
            self.players.append(Player(player_name))

    def distribute_cards(self):
        deck = Deck()
        deck.shuffle()

        # Distribute and sort cards
        while deck.cards:
            for player in self.players:
                if deck.cards:
                    player.receive_card(deck.deal(1)[0])
            for player in self.players:
                player.sort_hand()

    def display_hands(self):
        for player in self.players:
            print(player.show_hand())

    def play_trick(self):
        self.trick = Trick(self.players)
        return self.trick.play()

    def assign_titles(self, finished_players):
        num_finished_players = len(finished_players)
        if num_finished_players == 4:
            titles_to_assign = ["President", "Vice President", "Vice Scum", "Scum"]
            for idx, player in enumerate(finished_players):
                title = titles_to_assign[idx]
                print(f"{player.name} is the {title}.")
        else:
            for idx, player in enumerate(finished_players):
                if idx == 0:
                    title = "President"
                elif idx == 1:
                    title = "Vice President"
                elif idx == num_finished_players - 2:
                    title = "Vice Scum"
                elif idx == num_finished_players - 1:
                    title = "Scum"
                else:
                    title = "Neutral"
                print(f"{player.name} is the {title}.")

    async def play_game(self, websocket, num_players):
        self.setup(num_players)
        self.distribute_cards()

        finished_players = []
        while len(finished_players) < self.num_players:
            trick_finished_players = await self.play_trick()
            finished_players.extend(trick_finished_players)
            if len(finished_players) == self.num_players:
                break

        self.assign_titles(finished_players)
        return finished_players

    def get_game_state(self):
        game_state = {
            "type": "game_state",
            "players": [
                {
                    "name": player.name,
                    "hand": player.show_hand()
                }
                for player in self.players
            ],
            "played_cards": [[str(card) for card in cards] for cards in self.trick.played_cards],
            "current_player": self.trick.get_current_player().name if self.trick.get_current_player() else None
        }
        return game_state

    async def handle_message(self, message):
        try:
            data = json.loads(message)
            if data["action"] == "join":
                player_name = data["name"]
                player = Player(player_name)
                self.players.append(player)

                if len(self.players) == self.num_players:
                    await self.start_game()

            elif data["action"] == "play":
                card_indices = data["indices"]
                player_name = data["name"]
                current_player = next(p for p in self.players if p.name == player_name)
                await self.trick.play_card(current_player, card_indices)
                await self.update_game_state()

            elif data["action"] == "pass":
                await self.trick.pass_turn()
                await self.update_game_state()
        
        except Exception as e:
            print(f"Error handling message: {e}")

    async def update_game_state(self):
        game_state = self.get_game_state()
        message = json.dumps(game_state)
        await asyncio.gather(*[client.send(message) for client in self.clients])

    async def start_game(self):
        self.distribute_cards()
        self.trick = Trick(self.players)
        await self.update_game_state()

    async def handler(self, websocket, path):
        await self.register(websocket)

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        finally:
            await self.unregister(websocket)