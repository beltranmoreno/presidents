# main.py
from Deck import Deck
from Player import Player

def display_hands(players):
    for player in players:
        print(player.show_hand())

def display_played_cards(played_cards):
    if played_cards:
        print("Played cards:")
        print(", ".join(str(card) for card in played_cards))
    else:
        print("No cards have been played yet.")

def card_rank(card):
    rank_order = {
        '2': 15, 'Ace': 14, 'King': 13, 'Queen': 12, 'Jack': 11,
        '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3
    }
    return rank_order[card.rank]

def main():
    deck = Deck()
    deck.shuffle()

    try:
        num_players = int(input("Enter the number of players: "))
    except ValueError:
        print("Invalid number of players. Using 4 players as default.")
        num_players = 4    
        
    players = [Player(f"Player {i + 1}") for i in range(num_players)]
    active_players = list(range(num_players))  # Indexes of players who are still playing
    finished_players = []  # Track finished players and their ranks
    titles = ["President", "Vice President", "Neutral", "Vice Scum", "Scum"]

    # Distribute and sort cards
    while deck.cards:
        for player in players:
            cards_to_deal = min(1, len(deck.cards))
            player.receive_card(deck.deal(cards_to_deal)[0])
        for player in players:
            player.sort_hand()

    # Show initial hands
    display_hands(players)
    played_cards = []  # List to keep track of played cards
    skip_next_player = False  # Flag to determine if the next player should be skipped
    last_player_to_play_a_card = None
    current_trick_size = 0  # Number of cards that must be played in the current trick

    # Game loop - each player plays one card per turn
    player_index = 0  # Start with the first player
    
    # As long as more than one player remains active
    while len(active_players) > 1:  
        current_player_index = active_players[player_index]
        current_player = players[current_player_index]

        if not current_player.hand:
            player_index = (player_index + 1) % len(active_players)
            continue

        # If player plays the same rank as one thats on the table, skip nex player
        if skip_next_player:
            print(f"Skipping {players[player_index].name}'s turn.")
            skip_next_player = False
            player_index = (player_index + 1) % len(active_players)
            continue

        # current_player_index = active_players[player_index]
        # current_player = players[current_player_index]

        # If the current player is the same as the last player to play a card, start a new trick
        if current_player_index == last_player_to_play_a_card:
            print(f"\nTrick over. {current_player.name} starts a new trick.")
            played_cards.clear()
            current_trick_size = 0
        print(f"\n{current_player.name}'s turn.")
        print(current_player.show_hand())

        if current_trick_size == 0:  # First player in the trick chooses the number of cards to play
            player_input = input("Enter card indices to play separated by space or type 'pass' to pass your turn: ").strip().lower()
        else:  # Subsequent players must match the number of cards
            player_input = input(f"Enter {current_trick_size} card indices to play separated by space or type 'pass' to pass your turn: ").strip().lower()
        
        # player_input = input(f"Enter {current_trick_size} card indices to play separated by space or type 'pass' to pass your turn: ").strip().lower()

        if player_input == 'pass':
            print(f"{current_player.name} has decided to pass.")
        else:
            try:
                card_indices = list(map(int, player_input.split()))   

                # Set the trick size based on the first player's choice
                if current_trick_size == 0:
                    current_trick_size = len(card_indices)

                if len(card_indices) != current_trick_size:
                    print(f"You must play exactly {current_trick_size} cards. Please try again.")
                    continue
                
                selected_cards = [current_player.hand[i] for i in card_indices]
                selected_ranks = [card.rank for card in selected_cards]

                if len(set(selected_ranks)) != 1:
                    print("All selected cards must be of the same rank. Please try again.")
                    continue

                if played_cards and card_rank(selected_cards[0]) < card_rank(played_cards[-1][0]):
                    print("Cannot play lower ranked cards. Try again or pass.")
                    continue

                for index in sorted(card_indices, reverse=True):
                    current_player.play_card(index)
                
                played_cards.append(selected_cards)
                display_played_cards(played_cards)

                if not current_player.hand:
                    print(f"{current_player.name} has finished all their cards!")
                    finished_players.append(current_player)
                    active_players.remove(current_player_index)
                    # End the trick and start a new one with the next player
                    played_cards.clear()
                    current_trick_size = 0
                    player_index = player_index % len(active_players)
                    print(f"\n{players[active_players[player_index]].name} starts a new trick.")
                    continue

                if current_player_index in active_players:
                    last_player_to_play_a_card = player_index

                if len(played_cards) > 1 and selected_ranks[0] == played_cards[-2][0].rank:
                    skip_next_player = True
                    print(f"The next player will be skipped because {current_player.name} played a matching rank!")

            except ValueError:
                print("Invalid input. Please enter a valid integer for the card index or 'pass'.")
                continue
        
        player_index = (player_index + 1) % len(active_players)

    # The last player who hasn't finished becomes the final ranked player
    finished_players.extend(players[i] for i in active_players)

    # All players have finished, print final rankings
    for idx, player in enumerate(finished_players):
        title = titles[idx] if idx < len(titles) else "Neutral player"
        print(f"{player.name} is the {title}.")


if __name__ == "__main__":
    main()
