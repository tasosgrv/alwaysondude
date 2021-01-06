import random
import re
from datetime import datetime

class Game:
    def __init__(self, bet, user, reaction):
        self.bet = bet
        self.user = user
        self.reaction = reaction
        self.__seed = self.calculateSeed()
        self.result = self.play()


    def calculateSeed(self):
        return hash((str(datetime.utcnow()), str(self.user.id)))

    def play(self):
        print(f"{self.user.name} wagerd {self.bet} on a Game")

class Coinflip(Game):
    def __init__(self, bet, user, reaction):
        super().__init__(bet, user, reaction)
    
    def play(self):
        random.seed(self._Game__seed)
        positions = ["🔵", "🔴"]
        if random.choice(positions) == self.reaction.emoji:
            print(f"{self.user.name} won \t Seed: {self._Game__seed}")
            return True
        else:
            print(f"{self.user.name} lose \t Seed: {self._Game__seed}")
            return False

    def __str__(self):
        return f"{Coinflip.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"

if __name__ == "__main__":
    players = ["Nikos", "Tasos", "Andreas", "Stefanos", "Paris", "Fotis", "Vasilis", "Giorgos", "Pavlos", "Kostas"]  
    player_ids = [420058166651256842, 374801286278676482, 729270168030543954, 786033389751762944, 420254454068281365, 792092086139879464, 776905424515235881, 450734343959347200]
    for player in players:
        c = Coinflip(200, player, "🔵")
        print(c)
        print(45*"=")
