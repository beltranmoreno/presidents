# Player.py
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def sort_hand(self):
            rank_order = {
                '2': 15, 'Ace': 14, 'King': 13, 'Queen': 12, 'Jack': 11,
                '10': 10, '9': 9, '8': 8, '7': 7, '6': 6, '5': 5, '4': 4, '3': 3
            }
            self.hand.sort(key=lambda card: rank_order[card.rank])

    def show_hand(self):
        # Include index numbers starting from 1
        formatted_hand = "\n".join([f"{index}. {card}" for index, card in enumerate(self.hand)])
        return f"{self.name}'s hand: \n{formatted_hand}"
            
    def play_card(self, card_index):
        try:
            if 0 <= card_index < len(self.hand):
                return self.hand.pop(card_index)
            else:
                raise IndexError("Invalid card index")
        except IndexError as e:
            print(e)
            return None