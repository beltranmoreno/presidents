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
    pass_count = 0  # Number of consecutive passes

    # Game loop - each player plays one card per turn
    player_index = 0  # Start with the first player
    while any(player.hand for player in players):
        if skip_next_player:
            print(f"Skipping {players[player_index].name}'s turn.")
            skip_next_player = False
            player_index = (player_index + 1) % num_players
            continue

        current_player = players[player_index]
        if not current_player.hand:
            player_index = (player_index + 1) % num_players
            continue

        print(f"\n{current_player.name}'s turn.")
        print(current_player.show_hand())
        player_input = input("Enter a card index to play or type 'pass' to pass your turn: ").strip().lower()

        if player_input == 'pass':
            print(f"{current_player.name} has decided to pass.")
            pass_count += 1
        else:
            try:
                card_index = int(player_input)
                
                if card_index < 0 or card_index >= len(current_player.hand):
                    print("Invalid card index. Index is out of range. Please try again.")
                    continue
                
                card = current_player.hand[card_index]
                if played_cards and card_rank(card) < card_rank(played_cards[-1]):
                    print("Cannot play a lower ranked card. Try again or pass.")
                    continue

                card = current_player.play_card(card_index)
                if card:
                    print(f"{current_player.name} played {card}.")
                    played_cards.append(card)
                    display_played_cards(played_cards)
                    last_player_to_play_a_card = player_index
                    pass_count = 0  # Reset pass count since a card was played

                    # Check if the played card matches the rank of the last card on the table
                    if len(played_cards) > 1 and card.rank == played_cards[-2].rank:
                        skip_next_player = True
                        print(f"The next player will be skipped because {current_player.name} played a matching rank!")
                else:
                    print("Invalid card index. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a valid integer for the card index or 'pass'.")
                continue
        
        # If all other players have passed, clear the trick and start new from the last player to play
        if pass_count >= len(players) - 1:
            print("All other players have passed. Clearing the trick and starting new from the last player to play.")
            played_cards.clear()
            player_index = last_player_to_play_a_card
            pass_count = 0
            continue  # Continue without incrementing the player index

        player_index = (player_index + 1) % num_players

if __name__ == "__main__":
    main()
