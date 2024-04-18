# Player.py
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def show_hand(self):
        return f"{self.name}'s hand: {', '.join(map(str, self.hand))}"
    
    def play_card(self, card_index):
            if 0 <= card_index < len(self.hand):
                return self.hand.pop(card_index)  # Remove and return the card at the specified index
            else:
                return None