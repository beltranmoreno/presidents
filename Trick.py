from Player import Player

class Trick:
    def __init__(self, players):
        self.players = players
        self.active_players = list(range(len(players)))
        self.finished_players = []
        self.played_cards = []
        self.current_trick_size = 0
        self.last_player_to_play = None
        self.skip_next_player = False

    def display_played_cards(self):
        if self.played_cards:
            print("Played cards:")
            for cards in self.played_cards:
                print(", ".join(str(card) for card in cards))
        else:
            print("No cards have been played yet.")

    def card_rank(self, card):
        rank_order = {
            '2': 15, 'Ace': 14, 'King': 13, 'Queen': 12, 'Jack': 11,
            '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3
        }
        return rank_order[card.rank]

    def play(self):
        player_index = 0
        while len(self.active_players) > 1:
            current_player_index = self.active_players[player_index]
            current_player = self.players[current_player_index]

            if not current_player.hand:
                player_index = (player_index + 1) % len(self.active_players)
                continue

            # Skip next player if required
            if self.skip_next_player:
                print(f"Skipping {self.players[self.active_players[player_index]].name}'s turn.")
                self.skip_next_player = False
                player_index = (player_index + 1) % len(self.active_players)
                continue

            # Start a new trick if the same player is to play again
            if current_player_index == self.last_player_to_play:
                print(f"\n{current_player.name} starts a new trick.")
                self.played_cards.clear()
                self.current_trick_size = 0

            print(f"\n{current_player.name}'s turn.")
            print(current_player.show_hand())

            if self.current_trick_size == 0:
                player_input = input("Enter card indices to play separated by space or type 'pass' to pass your turn: ").strip().lower()
            else:
                player_input = input(f"Enter {self.current_trick_size} card indices to play separated by space or type 'pass' to pass your turn: ").strip().lower()

            if player_input == 'pass':
                print(f"{current_player.name} has decided to pass.")
            else:
                try:
                    card_indices = list(map(int, player_input.split()))

                    # Check if indices are valid
                    if any(index < 0 or index >= len(current_player.hand) for index in card_indices):
                        print("Invalid card indices. Please try again.")
                        continue

                    if self.current_trick_size == 0:
                        self.current_trick_size = len(card_indices)

                    if len(card_indices) != self.current_trick_size:
                        print(f"You must play exactly {self.current_trick_size} cards. Please try again.")
                        continue

                    selected_cards = [current_player.hand[i] for i in card_indices]
                    selected_ranks = [card.rank for card in selected_cards]

                    if len(set(selected_ranks)) != 1:
                        print("All selected cards must be of the same rank. Please try again.")
                        continue

                    if self.played_cards and self.card_rank(selected_cards[0]) < self.card_rank(self.played_cards[-1][0]):
                        print("Cannot play lower ranked cards. Try again or pass.")
                        continue

                    for index in sorted(card_indices, reverse=True):
                        current_player.play_card(index)

                    self.played_cards.append(selected_cards)
                    self.display_played_cards()

                    self.last_player_to_play = current_player_index

                    if not current_player.hand:
                        print(f"{current_player.name} has finished all their cards!")
                        self.finished_players.append(current_player)
                        self.active_players.remove(current_player_index)
                        # End the trick and start a new one with the next player
                        self.played_cards.clear()
                        self.current_trick_size = 0
                        if len(self.active_players) > 1:
                            player_index = player_index % len(self.active_players)
                            print(f"\n{self.players[self.active_players[player_index]].name} starts a new trick.")
                        continue

                    if len(self.played_cards) > 1 and selected_ranks[0] == self.played_cards[-2][0].rank:
                        self.skip_next_player = True
                        print(f"The next player will be skipped because {current_player.name} played a matching rank!")

                except ValueError:
                    print("Invalid input. Please enter valid integers for the card indices or 'pass'.")
                    continue

            player_index = (player_index + 1) % len(self.active_players)
        
        # If only one player is left, add them to finished_players
        if len(self.active_players) == 1:
            last_player = self.players[self.active_players[0]]
            self.finished_players.append(last_player)
            self.active_players.clear()

        return self.finished_players