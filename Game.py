from Deck import Deck
from Player import Player
from Trick import Trick

class Game:
    def __init__(self):
        self.players = []
        self.num_players = 0
        self.titles = ["President", "Vice President", "Neutral", "Vice Scum", "Scum"]
        self.num_tricks = 0

    def setup(self):
        try:
            self.num_players = int(input("Enter the number of players: "))
        except ValueError:
            print("Invalid number of players. Using 4 players as default.")
            self.num_players = 4

        self.players = [Player(f"Player {i + 1}") for i in range(self.num_players)]


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
        trick = Trick(self.players)
        return trick.play()

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

    def play_game(self):
        self.setup()

        while True:
            self.distribute_cards()
            self.display_hands()

            finished_players = []
            while len(finished_players) < self.num_players:
                trick_finished_players = self.play_trick()
                finished_players.extend(trick_finished_players)
                if len(finished_players) == self.num_players:
                    break

            self.assign_titles(finished_players)

            play_again = input("Do you want to play another game? (yes/no): ").strip().lower()
            if play_again != 'yes':
                break

            for player in self.players:
                player.hand.clear()  # Clear the players' hands for the next game
