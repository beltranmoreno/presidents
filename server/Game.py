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
    
    def add_player(self, player):
        if len(self.players) < self.num_players:
            self.players.append(player)

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

    def start_trick(self):
            self.trick = Trick(self.players)
            
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
            "players": [player.to_dict() for player in self.players],  # Convert players to dicts
            "played_cards": [[card.to_dict() for card in cards] for cards in self.trick.played_cards],  # Convert cards to dicts
            "current_player": self.trick.get_current_player().name if self.trick.get_current_player() else None
        }
        return game_state

   
    async def update_game_state(self):
        game_state = self.get_game_state()
        message = json.dumps(game_state)
        await asyncio.gather(*[client.send(message) for client in self.clients])
