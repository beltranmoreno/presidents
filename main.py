# main.py
from Deck import Deck
from Player import Player

def display_hands(players):
    for player in players:
        print(player.show_hand())

def main():
    deck = Deck()
    deck.shuffle()

    num_players = int(input("Enter the number of players: "))
    players = [Player(f"Player {i + 1}") for i in range(num_players)]

    # Distribute cards
    while deck.cards:
        for player in players:
            if not deck.cards:
                break
            player.receive_card(deck.cards.pop(0))

    # Show initial hands
    display_hands(players)

    # Game loop - each player plays one card per turn
    while any(player.hand for player in players):
        for player in players:
            if not player.hand:
                continue
            print(f"\n{player.name}'s turn.")
            print(player.show_hand())
            card_index = int(input("Choose a card index to play: "))
            card = player.play_card(card_index)
            if card:
                print(f"{player.name} played {card}.")
            else:
                print("Invalid card index.")
            display_hands(players)

if __name__ == "__main__":
    main()
