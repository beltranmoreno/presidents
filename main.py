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



def main():
    deck = Deck()
    deck.shuffle()

    num_players = int(input("Enter the number of players: "))
    players = [Player(f"Player {i + 1}") for i in range(num_players)]

    # Distribute and sort cards
    while deck.cards:
        for player in players:
            if not deck.cards:
                break
            player.receive_card(deck.cards.pop(0))
        for player in players:
            player.sort_hand()

    # Show initial hands
    display_hands(players)
    played_cards = []  # List to keep track of played cards
    skip_next_player = False  # Flag to determine if the next player should be skipped
    last_played_card = None  # Track the last played card

    # Game loop - each player plays one card per turn
    player_index = 0  # Start with the first player
    while any(player.hand for player in players):
        current_player = players[player_index]
        if not current_player.hand:
            continue


        for player in players:
            if not player.hand:
                continue
            print(f"\n{player.name}'s turn.")
            print(player.show_hand())
            card_index = int(input("Choose a card index to play: "))
            card = player.play_card(card_index)
            if card:
                print(f"{player.name} played {card}.")
                played_cards.append(card)
            else:
                print("Invalid card index.")
            display_played_cards(played_cards)
            # display_hands(players)

if __name__ == "__main__":
    main()
