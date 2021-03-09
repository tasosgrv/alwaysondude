import random
import re
import csv
from datetime import datetime

class User:
    def __init__(self):
        self.name = 'Tasos'
        self.id = 420058166651256842
class Reaction:
    def __init__(self):
        self.emoji = '🔴'
        self.id = 809385851334557706


class Game:

    def __init__(self, bet, user):
        self.bet = bet
        self.user = user
        self.counter = -1
        self.__seed = self.calculateSeed()
        self.result = self.play()


    def calculateSeed(self):
        return hash((str(datetime.utcnow()), str(self.user.id)))

    def play(self):
        print(f"{self.user.name} wagerd {self.bet} on a Game with seed {self.__seed}")

class Coinflip(Game):
    def __init__(self, bet, user, reaction):
        self.reaction = reaction 
        super().__init__(bet, user)
        
    
    def play(self):
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)
        positions = ["🔵", "🔴"]
        if random.choice(positions) == self.reaction.emoji:
            #print(f"{self.user.name} won {Coinflip.__name__} \t Seed: {self._Game__seed}")
            return True
        else:
            #print(f"{self.user.name} lose {Coinflip.__name__} \t Seed: {self._Game__seed}")
            return False

    def simulate(self, simulations, NumberOfGames):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0 
            for i in range(0,NumberOfGames):
                r = self.play()
                games+=1
                totalStake+=bet
                if r:
                    totalWin+=bet

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")


    def __str__(self):
        return f"{Coinflip.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"
        
class Slot(Game):
    values = {
        ":lemon:" :0.25,
        ":tangerine:" :0.50,
        ":cherries:":1, 
        ":grapes:" :2, 
        ":blueberries:":5, 
        ":watermelon:":17, 
        ":bell:":40, 
        ":crown:":60, 
        ":seven:":80, 
        ":gem:":100
        }
    reel = [":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",
            ":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",
            ":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",
            ":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",
            ":blueberries:",":blueberries:",":blueberries:",":blueberries:",":blueberries:",":blueberries:",
            ":watermelon:",":watermelon:",":watermelon:",":watermelon:",":watermelon:",":watermelon:",
            ":bell:",":bell:",":bell:",":bell:",":bell:",
            ":crown:",":crown:",":crown:",":crown:",
            ":seven:",":seven:",
            ":gem:"]
    def __init__(self, bet, user):
        super().__init__(bet, user)
    
    def play(self):
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)
        results = []
        self.counter+=1
        for i in range(0, 5):
            results.append(random.choice(Slot.reel))

        if results[0]==results[1] and results[1]==results[2] and results[2]==results[3] and results[3]==results[4]:
            return (Slot.values[results[0]]*20, results) 
        elif results[0]==results[1] and results[1]==results[2] and results[2]==results[3]:
            return (Slot.values[results[0]]*8, results)
        elif results[0]==results[1] and results[1]==results[2]:
            return (Slot.values[results[0]]*4, results)
        elif results[0]==results[1]:
            return (Slot.values[results[0]]*2, results)
        else:
            return (0, results)
        
    def simulate(self, simulations, NumberOfGames):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0
            sims = []
            for i in range(0,NumberOfGames):
                r = self.play()
                row = [r[0], " ".join(map(str, r[1])), self._Game__seed]
                sims.append(row) 
                games+=1
                totalStake+=bet
                totalWin+=bet*r[0]
            
            with open('slot_simulations.csv', mode="w") as sims_file:
                sims_writer = csv.writer(sims_file, delimiter=',')
                sims_writer.writerows(sims)

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")


    def __str__(self):
        return f"{Slot.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"


if __name__ == "__main__":

    user = User()
    reaction = Reaction()
    bet = 1
    #c = Coinflip(bet, user, reaction)
    #c.simulate(1, 10)

    s = Slot(bet, user)
    s.simulate(10, 1000000)

    