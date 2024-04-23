# Player.py
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def sort_hand(self):
            rank_order = {
                '3': 3, 
                '4': 4, 
                '5': 5, 
                '6': 6, 
                '7': 7, 
                '8': 8, 
                '9': 9, 
                '10': 10, 
                'Jack': 11, 
                'Queen': 12, 
                'King': 13, 
                'Ace': 14, 
                '2': 15 
            }
            self.hand.sort(key=lambda card: rank_order[card.rank])

    def show_hand(self):
        return f"{self.name}'s hand: {', '.join(map(str, self.hand))}"
    
    def play_card(self, card_index):
            if 0 <= card_index < len(self.hand):
                return self.hand.pop(card_index)  # Remove and return the card at the specified index
            else:
                return None