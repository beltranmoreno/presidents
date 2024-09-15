class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"

    def to_dict(self):
            # Convert card object to dictionary
            return {
                'rank': self.rank,
                'suit': self.suit
            }